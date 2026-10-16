"""Приём заявки: защита от спама, дубликатов и уведомление."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone

from .models import Lead
from .notify import format_lead_message, send_telegram


class Outcome(Enum):
    CREATED = "created"
    DUPLICATE = "duplicate"
    RATE_LIMITED = "rate_limited"


@dataclass(frozen=True)
class SubmitResult:
    outcome: Outcome
    lead: Lead | None = None

    @property
    def accepted(self) -> bool:
        """Заявка принята: создана новая или уже есть такая же недавняя."""
        return self.outcome in (Outcome.CREATED, Outcome.DUPLICATE)


def client_ip(request: HttpRequest) -> str | None:
    if settings.LEADS_TRUST_X_FORWARDED_FOR:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if forwarded:
            return forwarded.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def submit_lead(data: dict, ip: str | None, *, send=send_telegram) -> SubmitResult:
    """Сохранить заявку, если не превышен лимит и нет свежего дубликата.

    ``data`` — ``cleaned_data`` формы. ``send`` можно подменить в тестах.
    """
    now = timezone.now()

    if ip:
        recent = Lead.objects.filter(ip_address=ip, created_at__gte=now - timedelta(hours=1))
        if recent.count() >= settings.LEADS_RATE_LIMIT_PER_HOUR:
            return SubmitResult(Outcome.RATE_LIMITED)

    window = now - timedelta(minutes=settings.LEADS_DUPLICATE_WINDOW_MINUTES)
    duplicate = Lead.objects.filter(phone=data["phone"], created_at__gte=window).first()
    if duplicate:
        return SubmitResult(Outcome.DUPLICATE, duplicate)

    lead = Lead.objects.create(
        name=data["name"],
        phone=data["phone"],
        message=data.get("message", ""),
        utm_source=data.get("utm_source", ""),
        utm_medium=data.get("utm_medium", ""),
        utm_campaign=data.get("utm_campaign", ""),
        ip_address=ip,
    )

    text = format_lead_message(
        name=lead.name, phone=lead.phone_display, message=lead.message, source=lead.utm_source
    )
    if send(text, token=settings.TELEGRAM_BOT_TOKEN, chat_id=settings.TELEGRAM_CHAT_ID):
        Lead.objects.filter(pk=lead.pk).update(notified=True)
        lead.notified = True
    return SubmitResult(Outcome.CREATED, lead)
