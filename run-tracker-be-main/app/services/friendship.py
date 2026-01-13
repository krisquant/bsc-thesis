from uuid import UUID

from app.core.exc import (
    BadRequestException,
    ForbiddenException,
    ObjectNotFoundException,
)
from app.core.unit_of_work import ABCUnitOfWork
from app.models.friendship import FriendshipStatus
from app.models.user import User
from app.schemas.friendship import (
    FriendListResponse,
    FriendRequestAction,
    FriendRequestListResponse,
    FriendshipResponse,
)
from app.schemas.users import UserResponse


class FriendshipService:
    async def send_request(
        self, uow: ABCUnitOfWork, requester: User, email: str
    ) -> FriendshipResponse:
        async with uow:
            # 1. Find user by email
            addressee = await uow.user.get_by_email(email)
            if not addressee:
                raise ObjectNotFoundException(email, "User")

            # Ensure we compare strings
            requester_uuid_str = str(requester.uuid)
            addressee_uuid_str = str(addressee.uuid)

            if addressee_uuid_str == requester_uuid_str:
                raise BadRequestException("Cannot send friend request to yourself")

            # 2. Check if friendship already exists
            # Repository expects strings or UUIDs?
            # If Friendship model has Mapped[str], we should pass strings.
            existing = await uow.friendship.get_friendship(
                requester_uuid_str, addressee_uuid_str
            )
            if existing:
                if existing.status == FriendshipStatus.ACCEPTED:
                    raise BadRequestException("Already friends")
                # existing.requester_id is str
                if existing.requester_id == requester_uuid_str:
                    raise BadRequestException("Friend request already sent")
                if existing.addressee_id == requester_uuid_str:
                    raise BadRequestException(
                        "User has already sent you a friend request"
                    )

            # 3. Create request
            friendship = await uow.friendship.create_one(
                {
                    "requester_id": requester_uuid_str,
                    "addressee_id": addressee_uuid_str,
                    "status": FriendshipStatus.PENDING,
                }
            )

            # Manually attach relationships to avoid lazy loading error in Pydantic validation
            friendship.requester = requester
            friendship.addressee = addressee

            return FriendshipResponse.model_validate(friendship)

    async def respond_to_request(
        self,
        uow: ABCUnitOfWork,
        user_id: UUID,
        request_id: UUID,
        action: FriendRequestAction,
    ) -> None:
        async with uow:
            friendship = await uow.friendship.get_one(uuid=request_id)
            if not friendship:
                raise ObjectNotFoundException(request_id, "Friend request")

            user_id_str = str(user_id)
            addressee_id_str = str(friendship.addressee_id)
            requester_id_str = str(friendship.requester_id)

            if action == FriendRequestAction.ACCEPT:
                if user_id_str != addressee_id_str:
                    raise ForbiddenException(
                        "Only the recipient can accept this request"
                    )

            if action == FriendRequestAction.DECLINE:
                if user_id_str != addressee_id_str and user_id_str != requester_id_str:
                    raise ForbiddenException(
                        "You do not have permission to decline/cancel this request"
                    )

            if friendship.status != FriendshipStatus.PENDING:
                raise BadRequestException("Request is not pending")

            if action == FriendRequestAction.ACCEPT:
                await uow.friendship.update_one(
                    request_id, {"status": FriendshipStatus.ACCEPTED}
                )
            else:
                await uow.friendship.delete_one(request_id)

    async def list_friends(
        self, uow: ABCUnitOfWork, user_id: UUID
    ) -> FriendListResponse:
        async with uow:
            friendships = await uow.friendship.get_friends(user_id)

            friends = []
            for f in friendships:
                # Determine which user is the friend
                if str(f.requester_id) == str(user_id):
                    # We need to fetch the addressee.
                    # Since we are inside a session, we can access the relationship if lazy loading is enabled,
                    # or we should eagerly load it in the repo.
                    # For now, let's assume lazy loading works or we fetch explicitly.
                    # To be safe and async-friendly, let's fetch explicitly if relationship is not loaded.
                    # Actually, let's just use the relationship if it's awaitable or configured for async.
                    # Standard SQLAlchemy async requires explicit loading or selectinload.
                    # Let's assume we need to fetch the user.
                    friend_user = await uow.user.get_one(uuid=f.addressee_id)
                else:
                    friend_user = await uow.user.get_one(uuid=f.requester_id)

                if friend_user:
                    friends.append(UserResponse.model_validate(friend_user))

            return FriendListResponse(friends=friends, total=len(friends))

    async def list_requests(
        self, uow: ABCUnitOfWork, user_id: UUID
    ) -> FriendRequestListResponse:
        async with uow:
            # Incoming
            incoming = await uow.friendship.get_pending_requests(
                user_id, type="incoming"
            )

            # Outgoing
            outgoing = await uow.friendship.get_pending_requests(
                user_id, type="outgoing"
            )

            return FriendRequestListResponse(
                incoming=[FriendshipResponse.model_validate(f) for f in incoming],
                outgoing=[FriendshipResponse.model_validate(f) for f in outgoing],
            )


def get_friendship_service() -> FriendshipService:
    return FriendshipService()
