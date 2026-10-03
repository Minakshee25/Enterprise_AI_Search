from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from langchain_core.messages import AIMessage, HumanMessage

from app.db.database import get_pool
from app.graph.chat_graph import chatbot
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    CreateConversationResponse,
)


router = APIRouter()


# Temporary development user.
# Later this will come from the validated Entra access token.
DEV_USER_ID = UUID(
    "00000000-0000-0000-0000-000000000001"
)


@router.post(
    "/conversations",
    response_model=CreateConversationResponse,
)
async def create_conversation():

    conversation_id = uuid4()

    db = get_pool()

    await db.execute(
        """
        INSERT INTO conversations (
            id,
            user_id
        )
        VALUES ($1, $2)
        """,
        conversation_id,
        DEV_USER_ID,
    )

    return CreateConversationResponse(
        conversation_id=conversation_id
    )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[ChatMessage],
)
async def get_conversation_messages(
    conversation_id: UUID,
):

    db = get_pool()

    rows = await db.fetch(
        """
        SELECT
            role,
            content
        FROM messages
        WHERE conversation_id = $1
        ORDER BY created_at ASC
        """,
        conversation_id,
    )

    return [
        ChatMessage(
            role=row["role"],
            content=row["content"],
        )
        for row in rows
    ]


@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest,
):

    db = get_pool()

    conversation_exists = await db.fetchval(
        """
        SELECT EXISTS (
            SELECT 1
            FROM conversations
            WHERE id = $1
        )
        """,
        request.conversation_id,
    )

    if not conversation_exists:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    # Persist the user's message first.
    await db.execute(
        """
        INSERT INTO messages (
            conversation_id,
            role,
            content
        )
        VALUES ($1, $2, $3)
        """,
        request.conversation_id,
        "user",
        request.message,
    )

    config = {
        "configurable": {
            "thread_id": str(
                request.conversation_id
            )
        }
    }

    async def generate():

        assistant_parts = []

        async for message_chunk, metadata in chatbot.astream(
            {
                "messages": [
                    HumanMessage(
                        content=request.message
                    )
                ]
            },
            config=config,
            stream_mode="messages",
        ):

            if isinstance(
                message_chunk,
                AIMessage,
            ):
                content = message_chunk.content

                if isinstance(content, str):
                    assistant_parts.append(content)

                    yield content

        assistant_message = "".join(
            assistant_parts
        )

        if assistant_message:
            db = get_pool()

            await db.execute(
                """
                INSERT INTO messages (
                    conversation_id,
                    role,
                    content
                )
                VALUES ($1, $2, $3)
                """,
                request.conversation_id,
                "assistant",
                assistant_message,
            )

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )