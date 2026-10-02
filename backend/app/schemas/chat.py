from uuid import UUID

from pydantic import BaseModel, Field


class CreateConversationResponse(BaseModel):
    conversation_id: UUID


class ChatRequest(BaseModel):
    conversation_id: UUID

    message: str = Field(
        min_length=1,
        max_length=10000
    )

# this is our schema: 
# this is a chatmessage class, each object of this class will be a chatmessage
# {
#     "role": "assistant",
#     "content": "..."
# }

class ChatMessage(BaseModel):
    role: str
    content: str