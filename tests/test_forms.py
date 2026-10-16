from leads.forms import LeadForm


def test_valid_form_normalizes_phone(payload):
    form = LeadForm(payload)
    assert form.is_valid(), form.errors
    assert form.cleaned_data["phone"] == "+79123456789"
    assert not form.is_bot


def test_name_is_stripped_and_required(payload):
    payload["name"] = "  Анна  "
    form = LeadForm(payload)
    assert form.is_valid()
    assert form.cleaned_data["name"] == "Анна"

    payload["name"] = ""
    assert "name" in LeadForm(payload).errors


def test_short_name_is_rejected(payload):
    payload["name"] = "А"
    assert "name" in LeadForm(payload).errors


def test_invalid_phone_is_rejected(payload):
    payload["phone"] = "12345"
    errors = LeadForm(payload).errors
    assert "phone" in errors
    assert "+7" in errors["phone"][0]


def test_consent_is_required(payload):
    del payload["consent"]
    assert "consent" in LeadForm(payload).errors


def test_message_is_optional_and_limited(payload):
    payload["message"] = ""
    assert LeadForm(payload).is_valid()
    payload["message"] = "x" * 501
    assert "message" in LeadForm(payload).errors


def test_honeypot_marks_bot(payload):
    payload["website"] = "http://spam.example"
    form = LeadForm(payload)
    assert form.is_valid()
    assert form.is_bot
