from uuid import UUID

from app.core.exc import ForbiddenException, ObjectNotFoundException
from app.core.unit_of_work import ABCUnitOfWork
from app.models.user import User
from app.schemas.challenge import (
    ChallengeAttemptCreate,
    ChallengeAttemptResponse,
    ChallengeCreate,
    ChallengeListResponse,
    ChallengeResponse,
)
from app.utils.distance_utils import extract_route_endpoints, points_within_radius


class ChallengeService:
    async def create_challenge(
        self, uow: ABCUnitOfWork, user: "User", data: ChallengeCreate
    ) -> ChallengeResponse:
        async with uow:
            # 1. Verify source run belongs to user
            run = await uow.run.get_one(uuid=data.source_run_id)
            if not run:
                raise ObjectNotFoundException(data.source_run_id, "Run")

            if str(run.user_uuid) != str(user.uuid):
                raise ForbiddenException(
                    "You can only create challenges from your own runs"
                )

            # 2. Create challenge
            challenge_data = data.model_dump()
            challenge_data["creator_id"] = str(user.uuid)
            challenge_data["source_run_id"] = str(data.source_run_id)

            challenge = await uow.challenge.create_one(challenge_data)

            # 3. Manually populate relationships to avoid MissingGreenlet error
            challenge.creator = user
            challenge.source_run = run

            return ChallengeResponse.model_validate(challenge)

    async def list_available_challenges(
        self, uow: ABCUnitOfWork, user_id: UUID, page: int, limit: int
    ) -> ChallengeListResponse:
        async with uow:
            # 1. Get friends
            friendships = await uow.friendship.get_friends(user_id)
            friend_ids = []
            for f in friendships:
                if str(f.requester_id) == str(user_id):
                    friend_ids.append(f.addressee_id)
                else:
                    friend_ids.append(f.requester_id)

            # Add self to see own challenges? Maybe not "available" but good for testing.
            # Let's stick to friends for "available to beat".

            if not friend_ids:
                return ChallengeListResponse(
                    items=[], total=0, page=page, limit=limit, total_pages=0
                )

            # 2. Get challenges
            challenges, total = await uow.challenge.get_available_challenges(
                friend_ids, page=page, limit=limit
            )

            # 3. Populate creator info (optional, but good for UI)
            # Relationships are now eager loaded in the repository
            items = [ChallengeResponse.model_validate(c) for c in challenges]

            return ChallengeListResponse(
                items=items,
                total=total,
                page=page,
                limit=limit,
                total_pages=(total + limit - 1) // limit if limit > 0 else 0,
            )

    async def get_challenge(
        self, uow: ABCUnitOfWork, challenge_id: UUID
    ) -> ChallengeResponse:
        async with uow:
            challenge = await uow.challenge.get_by_id(challenge_id)
            if not challenge:
                raise ObjectNotFoundException(challenge_id, "Challenge")

            # Relationships are now eager loaded in the repository
            return ChallengeResponse.model_validate(challenge)

    async def get_challenge_by_run(
        self, uow: ABCUnitOfWork, run_id: UUID
    ) -> ChallengeResponse | None:
        async with uow:
            challenge = await uow.challenge.get_by_run_id(run_id)
            if not challenge:
                return None

            # Relationships are now eager loaded in the repository
            return ChallengeResponse.model_validate(challenge)

    async def attempt_challenge(
        self,
        uow: ABCUnitOfWork,
        user_id: UUID,
        challenge_id: UUID,
        data: ChallengeAttemptCreate,
    ) -> ChallengeAttemptResponse:
        async with uow:
            # 1. Get challenge
            challenge = await uow.challenge.get_one(uuid=challenge_id)
            if not challenge:
                raise ObjectNotFoundException(challenge_id, "Challenge")

            # 2. Get source run
            source_run = await uow.run.get_one(uuid=challenge.source_run_id)
            if not source_run:
                raise ObjectNotFoundException(challenge.source_run_id, "Source Run")

            # 3. Get attempt run
            attempt_run = await uow.run.get_one(uuid=data.run_id)
            if not attempt_run:
                raise ObjectNotFoundException(data.run_id, "Attempt Run")

            if str(attempt_run.user_uuid) != str(user_id):
                raise ForbiddenException("You can only submit your own runs")

            # 4. Calculate success based on route comparison
            # Extract first and last points from both routes
            source_start, source_end = extract_route_endpoints(source_run.route)
            attempt_start, attempt_end = extract_route_endpoints(attempt_run.route)

            # Success if both start and end points are within 100m radius
            # Default to False if routes are missing or invalid
            success = False
            if source_start and source_end and attempt_start and attempt_end:
                start_match = points_within_radius(
                    source_start, attempt_start, radius_meters=100
                )
                end_match = points_within_radius(
                    source_end, attempt_end, radius_meters=100
                )
                success = start_match and end_match

            # 5. Create Attempt
            attempt = await uow.challenge_attempt.create_one(
                {
                    "challenge_id": str(challenge_id),
                    "user_id": str(user_id),
                    "run_id": str(data.run_id),
                    "success": success,
                }
            )

            # Manually populate relationships to avoid MissingGreenlet
            user = await uow.user.get_one(uuid=user_id)
            attempt.user = user
            attempt.run = attempt_run

            return ChallengeAttemptResponse.model_validate(attempt)

    async def get_challenge_attempts(
        self, uow: ABCUnitOfWork, challenge_id: UUID
    ) -> list[ChallengeAttemptResponse]:
        async with uow:
            # Verify challenge exists
            challenge = await uow.challenge.get_one(uuid=challenge_id)
            if not challenge:
                raise ObjectNotFoundException(challenge_id, "Challenge")

            # Get attempts
            attempts = await uow.challenge_attempt.get_attempts_by_challenge(
                challenge_id
            )

            # Attempts already have user and run eager loaded from repository
            return [
                ChallengeAttemptResponse.model_validate(attempt) for attempt in attempts
            ]


def get_challenge_service() -> ChallengeService:
    return ChallengeService()
