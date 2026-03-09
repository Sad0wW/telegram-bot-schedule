from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from typing import Any, Awaitable, Callable, Dict

import logging

class LoggerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            logging.info(f"[MESSAGE] {event.from_user.id} (@{event.from_user.username}) -> {event.text if event.text else event.caption}")
        elif isinstance(event, CallbackQuery):
            logging.info(f"[CALLBACK] {event.from_user.id} (@{event.from_user.username}) -> {event.data}")

        return await handler(event, data)