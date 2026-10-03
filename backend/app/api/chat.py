from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.auth.user import get_current_user
from app.db.database import get_pool
from app.graph.chat_graph import chatbot
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    ConversationSummary,
    CreateConversationResponse,
)


router = APIRouter()


# ---------------------------------------------------------
# CREATE CONVERSATION
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# LIST CONVERSATIONS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# GET CONVERSATION MESSAGES
# ---------------------------------------------------------

@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[ChatMessage],
)
async def get_conversation_messages(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user),
):
    db = get_pool()

    # Make sure the conversation belongs
    # to the authenticated user.
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


# ---------------------------------------------------------
# CHAT
# ---------------------------------------------------------

@router.post("/chat/stream")
async def stream_chat(
    request: ChatRequest,
    user_id: UUID = Depends(get_current_user),
):
    db = get_pool()

    # -----------------------------------------------------
    # 1. Verify conversation ownership
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 2. Save user's message
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 3. Update conversation activity timestamp
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 4. LangGraph configuration
    #
    # Every conversation receives its own LangGraph thread.
    # -----------------------------------------------------

    config = {
        "configurable": {
            "thread_id": str(
                request.conversation_id
            )
        }
    }

    # -----------------------------------------------------
    # 5. Execute LangGraph
    # -----------------------------------------------------

    async def generate():

        assistant_parts = []

        async for update in chatbot.astream(
            {
                "messages": [
                    HumanMessage(
                        content=request.message
                    )
                ]
            },
            config=config,

            # IMPORTANT:
            #
            # We use "updates" instead of "messages".
            #
            # The graph contains internal LLM calls:
            #
            # translation
            # supervisor
            # knowledge agent
            # output translation
            #
            # We do NOT want those intermediate outputs
            # appearing in the React UI.
            stream_mode="updates",
        ):

            output = None

            # ---------------------------------------------
            # Simple messages:
            #
            # hello
            # hi
            # thanks
            # etc.
            # ---------------------------------------------

            if "simple_response" in update:
                output = update[
                    "simple_response"
                ]

            # ---------------------------------------------
            # Normal agent workflow.
            #
            # Everything eventually passes through
            # final_response before reaching the user.
            # ---------------------------------------------

            elif "final_response" in update:
                output = update[
                    "final_response"
                ]

            # Ignore internal graph nodes:
            #
            # query_understanding
            # detect_language
            # translate_to_english
            # supervisor
            # knowledge_agent
            # translate_answer
            # etc.

            if not output:
                continue

            messages = output.get(
                "messages",
                [],
            )

            if not messages:
                continue

            final_message = messages[-1]

            content = final_message.content

            if isinstance(content, str):
                assistant_parts.append(
                    content
                )

                yield content

        # -------------------------------------------------
        # 6. Combine the user-visible assistant output
        # -------------------------------------------------

        assistant_message = "".join(
            assistant_parts
        )

        # -------------------------------------------------
        # 7. Persist assistant response in PostgreSQL
        # -------------------------------------------------

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

    # -----------------------------------------------------
    # 8. Send response to React
    # -----------------------------------------------------

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )