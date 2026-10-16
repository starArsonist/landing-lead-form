from datetime import timedelta

import pytest
from django.utils import timezone

from leads.models import Lead
from leads.services import Outcome, submit_lead


@pytest.fixture
def data():
    return {
        "name": "Анна",
        "phone": "+79123456789",
        "message": "Смета",
        "utm_source": "ads",
        "utm_medium": "",
        "utm_campaign": "",
    }


def never_send(text, *, token, chat_id):
    return False


def test_lead_is_created_and_notified(db, data):
    sent = []

    def fake_send(text, *, token, chat_id):
        sent.append(text)
        return True

    result = submit_lead(data, "10.0.0.1", send=fake_send)

    assert result.outcome is Outcome.CREATED
    assert result.accepted
    lead = Lead.objects.get()
    assert lead.phone == "+79123456789"
    assert lead.ip_address == "10.0.0.1"
    assert lead.notified is True
    assert "+7 (912) 345-67-89" in sent[0]


def test_failed_notification_still_saves_lead(db, data):
    result = submit_lead(data, "10.0.0.1", send=never_send)
    assert result.outcome is Outcome.CREATED
    assert Lead.objects.get().notified is False


def test_recent_duplicate_is_not_saved_twice(db, data):
    submit_lead(data, "10.0.0.1", send=never_send)
    result = submit_lead(data, "10.0.0.2", send=never_send)
    assert result.outcome is Outcome.DUPLICATE
    assert result.accepted
    assert Lead.objects.count() == 1


def test_old_duplicate_is_allowed(db, data, settings):
    submit_lead(data, "10.0.0.1", send=never_send)
    old = timezone.now() - timedelta(minutes=settings.LEADS_DUPLICATE_WINDOW_MINUTES + 1)
    Lead.objects.update(created_at=old)
    result = submit_lead(data, "10.0.0.1", send=never_send)
    assert result.outcome is Outcome.CREATED
    assert Lead.objects.count() == 2


def test_rate_limit_per_ip(db, data, settings):
    settings.LEADS_RATE_LIMIT_PER_HOUR = 2
    for index in range(2):
        data["phone"] = f"+7912000000{index}"
        assert submit_lead(data, "10.0.0.1", send=never_send).outcome is Outcome.CREATED

    data["phone"] = "+79120000009"
    blocked = submit_lead(data, "10.0.0.1", send=never_send)
    assert blocked.outcome is Outcome.RATE_LIMITED
    assert not blocked.accepted
    assert Lead.objects.count() == 2

    # другой адрес не затронут
    assert submit_lead(data, "10.0.0.2", send=never_send).outcome is Outcome.CREATED


def test_rate_limit_window_expires(db, data, settings):
    settings.LEADS_RATE_LIMIT_PER_HOUR = 1
    submit_lead(data, "10.0.0.1", send=never_send)
    Lead.objects.update(created_at=timezone.now() - timedelta(hours=2))
    data["phone"] = "+79120000009"
    assert submit_lead(data, "10.0.0.1", send=never_send).outcome is Outcome.CREATED
