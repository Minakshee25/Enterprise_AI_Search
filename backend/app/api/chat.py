from uuid import UUID, uuid4

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from langchain_core.messages import HumanMessage, AIMessage

from app.graph.chat_graph import chatbot
from app.schemas.chat import (
    ChatMessage,
    ChatRequest,
    CreateConversationResponse,
)


router = APIRouter()

# this endpoint is only to generate the ID
# CreateConversationResponse from schemas has UUID object inside
@router.post("/conversations", response_model=CreateConversationResponse)
def create_conversation():
    return CreateConversationResponse(
        conversation_id=uuid4()
    )


# this api is to add conversation history
@router.get("/conversations/{conversation_id}/messages", response_model=list[ChatMessage],)
def get_conversation_messages(conversation_id: UUID,):
    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }

    state = chatbot.get_state(config)

    messages = state.values.get(
        "messages",
        []
    )

    result = []

    for message in messages:

        if isinstance(message, HumanMessage):
            role = "user"

        elif isinstance(message, AIMessage):
            role = "assistant"

        else:
            continue

        result.append(
            ChatMessage(
                role=role,
                content=message.content,
            )
        )

    return result

@router.post("/chat/stream")
def stream_chat(request: ChatRequest,):

    config = {
        "configurable": {
            "thread_id": str(
                request.conversation_id
            )
        }
    }

    def generate():
        
        for message_chunk, metadata in chatbot.stream(
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
                AIMessage
            ):
                content = message_chunk.content

                if isinstance(content, str):
                    yield content

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )