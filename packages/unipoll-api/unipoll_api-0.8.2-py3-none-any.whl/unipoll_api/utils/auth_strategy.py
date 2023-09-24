import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, Optional

from fastapi_users import exceptions, models
from fastapi_users.authentication.strategy.base import Strategy
from fastapi_users.authentication.strategy.db.adapter import AccessTokenDatabase
from fastapi_users.authentication.strategy.db.models import AP
from fastapi_users.manager import BaseUserManager


class DatabaseStrategy(
    Strategy[models.UP, models.ID], Generic[models.UP, models.ID, AP]
):
    def __init__(
        self, database: AccessTokenDatabase[AP], lifetime_seconds: Optional[int] = None
    ):
        self.database = database
        self.lifetime_seconds = lifetime_seconds

    async def read_token(
        self, token: Optional[str], user_manager: BaseUserManager[models.UP, models.ID]
    ) -> Optional[models.UP]:
        if token is None:
            return None

        max_age = None
        if self.lifetime_seconds:
            max_age = datetime.now(timezone.utc) - timedelta(
                seconds=self.lifetime_seconds
            )

        access_token = await self.database.get_by_token(token, max_age)
        if access_token is None:
            return None

        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def write_token(self, user: models.UP):
        token_dict = self._create_access_token_dict(user)
        token = await self.database.create(token_dict)
        return token

    async def destroy_token(self, token: str, user: models.UP) -> None:
        access_token = await self.database.get_by_token(token)
        if access_token is not None:
            await self.database.delete(access_token)

    # Destroy all tokens for a user
    async def destroy_token_family(self, user: models.UP) -> None:
        tokens = await self.database.get_token_family_by_user_id(user.id)  # type: ignore
        await tokens.delete()

    def _create_access_token_dict(self, user: models.UP) -> Dict[str, Any]:
        access_token = secrets.token_urlsafe()
        refresh_token = secrets.token_urlsafe()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id
        }
