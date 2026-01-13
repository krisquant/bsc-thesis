import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.friendship import FriendshipStatus
from app.schemas.users import UserResponse


class FriendRequestCreate(BaseModel):
    email: EmailStr


class FriendRequestAction(str, enum.Enum):
    ACCEPT = "ACCEPT"
    DECLINE = "DECLINE"


class FriendRequestRespond(BaseModel):
    action: FriendRequestAction


class FriendshipResponse(BaseModel):
    uuid: UUID
    requester_id: UUID
    addressee_id: UUID
    status: FriendshipStatus
    created_at: datetime
    updated_at: datetime

    requester: Optional[UserResponse] = None
    addressee: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class FriendListResponse(BaseModel):
    friends: list[UserResponse]
    total: int


class FriendRequestListResponse(BaseModel):
    incoming: list[FriendshipResponse]
    outgoing: list[FriendshipResponse]
