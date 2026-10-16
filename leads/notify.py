"""Уведомление о заявке в Telegram. Не зависит от Django и сторонних библиотек.

Если токен или чат не заданы, отправка пропускается. Сбой сети не должен ломать приём
заявки, поэтому все сетевые ошибки возвращаются как ``False`` и пишутся в лог.
"""
from __future__ import annotations

import logging
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
MESSAGE_LIMIT = 3500  # Telegram принимает до 4096 символов; оставляем запас.


def format_lead_message(*, name: str, phone: str, message: str = "", source: str = "") -> str:
    lines = ["Новая заявка", "", f"Имя: {name}", f"Телефон: {phone}"]
    if message:
        lines.append(f"Сообщение: {message}")
    if source:
        lines.append(f"Источник: {source}")
    return "\n".join(lines)[:MESSAGE_LIMIT]


def send_telegram(
    text: str,
    *,
    token: str,
    chat_id: str,
    urlopen: Callable[..., object] = urllib.request.urlopen,
    timeout: float = 5.0,
) -> bool:
    """Отправить сообщение в чат. Вернуть ``True``, если Telegram принял запрос."""
    if not token or not chat_id:
        logger.info("Telegram не настроен, уведомление пропущено")
        return False

    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    request = urllib.request.Request(TELEGRAM_API.format(token=token), data=payload, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:  # type: ignore[operator]
            return 200 <= response.status < 300  # type: ignore[attr-defined]
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # Токен находится в адресе запроса, поэтому в лог пишем только тип ошибки.
        logger.warning("Не удалось отправить уведомление в Telegram: %s", type(exc).__name__)
        return False
