from uuid import UUID, uuid4

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
    ConversationSummary,
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

    conversation_exists = await db.fetchval(
        """
        SELECT EXISTS (
            SELECT 1
            FROM conversations
            WHERE id = $1
            AND user_id = $2
        )
        """,
        conversation_id,
        user_id,
    )

    if not conversation_exists:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

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
    user_id: UUID = Depends(get_current_user),
):
    db = get_pool()

    # Make sure this conversation exists
    # and belongs to the currently authenticated user.
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

    # Save the user's message.
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

    # Mark this conversation as recently active.
    await db.execute(
        """
        UPDATE conversations
        SET updated_at = NOW()
        WHERE id = $1
        AND user_id = $2
        """,
        request.conversation_id,
        user_id,
    )

    # LangGraph uses the conversation ID as its thread ID.
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

        # Combine all streamed chunks into one final assistant message.
        assistant_message = "".join(
            assistant_parts
        )

        # Persist the completed assistant response.
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

@router.get(
    "/conversations",
    response_model=list[ConversationSummary],
)
async def list_conversations(
    user_id: UUID = Depends(get_current_user),
):
    db = get_pool()

    rows = await db.fetch(
        """
        SELECT
            id,
            title,
            updated_at
        FROM conversations
        WHERE user_id = $1
        ORDER BY updated_at DESC
        """,
        user_id,
    )

    return [
        ConversationSummary(
            conversation_id=row["id"],
            title=row["title"],
            updated_at=row["updated_at"],
        )
        for row in rows
    ]

