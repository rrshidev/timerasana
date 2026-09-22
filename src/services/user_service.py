import logging
from typing import Dict, Optional

import httpx

from src.i18n import normalize_lang, lang_from_telegram

logger = logging.getLogger(__name__)


class UserService:
    """Регистрация/синхронизация пользователя в единой БД проекта через API.

    Язык таймер-бота хранится в единой БД Dharana (app_users.timer_language) —
    отдельная ячейка от основного бота/приложения (app_users.language).
    По умолчанию берётся язык из настроек Telegram пользователя.
    """

    def __init__(self, api_url: str):
        self.api_url = api_url
        self._lang_cache: Dict[int, str] = {}

    async def register_or_sync(
        self,
        telegram_id: int,
        name: str = "",
        username: str = "",
        language: Optional[str] = None,
    ) -> bool:
        """Upsert пользователя в app_users через POST /api/v1/auth/telegram.

        Возвращает True при успехе; язык пользователя (timer_language) кэшируется.
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.api_url}/api/v1/auth/telegram",
                    json={
                        "telegram_id": telegram_id,
                        "name": name,
                        "username": username,
                        "language": language or "ru",
                    },
                    timeout=10,
                )
            if resp.status_code == 200:
                user = resp.json().get("user", {})
                lang = user.get("timer_language")
                self._lang_cache[telegram_id] = normalize_lang(lang) if lang else "ru"
                logger.info(f"User {telegram_id} registered/synced (lang={self._lang_cache[telegram_id]})")
                return True
            logger.warning(f"Register failed for {telegram_id}: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Error registering user {telegram_id}: {e}")
        return False

    async def get_language(self, telegram_id: int, tg_language_code: Optional[str] = None) -> str:
        """Получить язык таймер-бота пользователя. Кэшируется.

        Если пользователя нет в базе — регистрируем с языком из настроек Telegram.
        """
        cached = self._lang_cache.get(telegram_id)
        if cached:
            return cached

        default_lang = lang_from_telegram(tg_language_code)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.api_url}/api/v1/auth/telegram/{telegram_id}/language",
                    timeout=10,
                )
            if resp.status_code == 200:
                lang = normalize_lang(resp.json().get("language"))
                self._lang_cache[telegram_id] = lang
                return lang
            if resp.status_code == 404:
                # Пользователя ещё нет — создаём через /telegram с языком Telegram.
                await self.register_or_sync(telegram_id, language=default_lang)
                return self._lang_cache.get(telegram_id, default_lang)
        except Exception as e:
            logger.error(f"Error getting language for {telegram_id}: {e}")

        self._lang_cache[telegram_id] = default_lang
        return default_lang

    def get_cached_language(self, telegram_id: int, default: str = "ru") -> str:
        """Синхронное чтение языка из кэша (без сети).

        Используется в фоновом цикле обновления таймеров, где сетевой
        запрос на каждый тик нежелателен.
        """
        return self._lang_cache.get(telegram_id, default)

    async def set_language(self, telegram_id: int, language: str) -> bool:
        """Сменить язык таймер-бота через PUT /api/v1/auth/telegram/{id}/language."""
        lang = normalize_lang(language)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.put(
                    f"{self.api_url}/api/v1/auth/telegram/{telegram_id}/language",
                    json={"language": lang},
                    timeout=10,
                )
            if resp.status_code == 200:
                actual = normalize_lang(resp.json().get("language"))
                self._lang_cache[telegram_id] = actual
                logger.info(f"Language for user {telegram_id} set to {actual}")
                return True
            logger.warning(f"Set language failed for {telegram_id}: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Error setting language for {telegram_id}: {e}")
        return False