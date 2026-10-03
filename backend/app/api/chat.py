from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException
from app.auth.user import get_current_user

from langchain_core.messages import AIMessage, HumanMessage

from app.db.database import get_pool
from app.graph.chat_graph import chatbot
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    CreateConversationResponse,
)

router = APIRouter()

@router.post(
    "/conversations",
    response_model=CreateConversationResponse,
)
async def create_conversation(
    user_id: UUID = Depends(get_current_user),
):

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
        user_id,
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
    user_id: UUID = Depends(get_current_user),
):

    db = get_pool()

    rows = await db.fetch(
        """
        SELECT
            m.role,
            m.content
        FROM messages m

        JOIN conversations c
            ON c.id = m.conversation_id

        WHERE m.conversation_id = $1
        AND c.user_id = $2

        ORDER BY m.created_at ASC
        """,
        conversation_id,
        user_id,
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
    user_id: UUID = Depends(get_current_user),
):

    db = get_pool()

    conversation_exists = await db.fetchval(
        """
        SELECT EXISTS (
            SELECT 1
            FROM conversations
            WHERE id = $1
            AND user_id = $2
        )
        """,
        request.conversation_id,
        user_id,
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