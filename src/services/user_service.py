import logging

import httpx

logger = logging.getLogger(__name__)


class UserService:
    """Регистрация/синхронизация пользователя в единой БД проекта через API."""

    def __init__(self, api_url: str):
        self.api_url = api_url

    async def register_or_sync(self, telegram_id: int, name: str = "", username: str = "") -> bool:
        """Upsert пользователя в app_users через POST /api/v1/auth/telegram."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_url}/api/v1/auth/telegram",
                    json={
                        "telegram_id": telegram_id,
                        "name": name,
                        "username": username,
                    },
                    timeout=10,
                )
            if resp.status_code == 200:
                logger.info(f"User {telegram_id} registered/synced")
                return True
            logger.warning(f"Register failed for {telegram_id}: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Error registering user {telegram_id}: {e}")
        return False