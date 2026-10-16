import pytest
from django.urls import reverse

from leads.models import Lead

pytestmark = pytest.mark.django_db

JSON = {"HTTP_ACCEPT": "application/json"}


def test_landing_renders_form_with_utm(client):
    response = client.get(reverse("landing"), {"utm_source": "ads"})
    assert response.status_code == 200
    page = response.content.decode()
    assert 'name="phone"' in page
    assert 'value="ads"' in page
    assert "csrfmiddlewaretoken" in page


def test_landing_truncates_long_utm(client):
    response = client.get(reverse("landing"), {"utm_source": "a" * 500})
    assert "a" * 101 not in response.content.decode()


def test_submit_without_js_redirects_to_thanks(client, payload):
    response = client.post(reverse("submit"), payload)
    assert response.status_code == 302
    assert response.url == reverse("thanks")
    lead = Lead.objects.get()
    assert lead.phone == "+79123456789"
    assert lead.utm_source == "ads"


def test_submit_with_json_returns_redirect_target(client, payload):
    response = client.post(reverse("submit"), payload, **JSON)
    assert response.status_code == 200
    assert response.json() == {"ok": True, "redirect": reverse("thanks")}


def test_invalid_form_returns_errors_as_json(client, payload):
    payload["phone"] = "123"
    response = client.post(reverse("submit"), payload, **JSON)
    assert response.status_code == 400
    assert "phone" in response.json()["errors"]
    assert Lead.objects.count() == 0


def test_invalid_form_without_js_rerenders_page(client, payload):
    payload["name"] = ""
    response = client.post(reverse("submit"), payload)
    assert response.status_code == 400
    assert "Укажите имя" in response.content.decode()


def test_bot_gets_success_but_nothing_is_saved(client, payload):
    payload["website"] = "http://spam.example"
    response = client.post(reverse("submit"), payload, **JSON)
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert Lead.objects.count() == 0


def test_rate_limited_ip_gets_429(client, payload, settings):
    settings.LEADS_RATE_LIMIT_PER_HOUR = 1
    assert client.post(reverse("submit"), payload, **JSON).status_code == 200
    payload["phone"] = "+7 912 000 00 09"
    response = client.post(reverse("submit"), payload, **JSON)
    assert response.status_code == 429
    assert Lead.objects.count() == 1


def test_duplicate_submission_looks_successful(client, payload):
    client.post(reverse("submit"), payload, **JSON)
    response = client.post(reverse("submit"), payload, **JSON)
    assert response.status_code == 200
    assert Lead.objects.count() == 1


def test_csrf_is_enforced():
    from django.test import Client

    strict = Client(enforce_csrf_checks=True)
    response = strict.post(reverse("submit"), {"name": "x"})
    assert response.status_code == 403


def test_get_on_submit_is_not_allowed(client):
    assert client.get(reverse("submit")).status_code == 405


def test_thanks_page(client):
    assert client.get(reverse("thanks")).status_code == 200


def test_forwarded_header_is_ignored_by_default(client, payload):
    client.post(reverse("submit"), payload, HTTP_X_FORWARDED_FOR="1.2.3.4")
    assert Lead.objects.get().ip_address == "127.0.0.1"


def test_forwarded_header_is_used_when_trusted(client, payload, settings):
    settings.LEADS_TRUST_X_FORWARDED_FOR = True
    client.post(reverse("submit"), payload, HTTP_X_FORWARDED_FOR="1.2.3.4, 10.0.0.1")
    assert Lead.objects.get().ip_address == "1.2.3.4"
