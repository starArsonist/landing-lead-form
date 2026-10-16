import urllib.error
import urllib.parse

from leads.notify import MESSAGE_LIMIT, format_lead_message, send_telegram


class FakeResponse:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_message_contains_all_fields():
    text = format_lead_message(
        name="Анна", phone="+7 (912) 345-67-89", message="Нужна смета", source="ads"
    )
    assert "Имя: Анна" in text
    assert "Телефон: +7 (912) 345-67-89" in text
    assert "Сообщение: Нужна смета" in text
    assert "Источник: ads" in text


def test_optional_fields_are_omitted():
    text = format_lead_message(name="Анна", phone="+7 (912) 345-67-89")
    assert "Сообщение" not in text
    assert "Источник" not in text


def test_message_is_truncated():
    text = format_lead_message(name="А", phone="1", message="x" * 10_000)
    assert len(text) == MESSAGE_LIMIT


def test_send_posts_form_encoded_payload():
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["body"] = urllib.parse.parse_qs(request.data.decode())
        captured["timeout"] = timeout
        return FakeResponse(200)

    assert send_telegram("привет", token="TOKEN", chat_id="42", urlopen=fake_urlopen) is True
    assert captured["url"] == "https://api.telegram.org/botTOKEN/sendMessage"
    assert captured["body"] == {"chat_id": ["42"], "text": ["привет"]}
    assert captured["timeout"] == 5.0


def test_missing_credentials_skip_sending():
    def must_not_be_called(*args, **kwargs):
        raise AssertionError("не должно быть сетевого запроса")

    assert send_telegram("текст", token="", chat_id="42", urlopen=must_not_be_called) is False
    assert send_telegram("текст", token="T", chat_id="", urlopen=must_not_be_called) is False


def test_network_error_returns_false_and_hides_token(caplog):
    def broken(request, timeout):
        raise urllib.error.URLError("https://api.telegram.org/botSECRET/sendMessage")

    with caplog.at_level("WARNING"):
        assert send_telegram("x", token="SECRET", chat_id="1", urlopen=broken) is False
    assert "SECRET" not in caplog.text
    assert "URLError" in caplog.text


def test_non_2xx_status_is_failure():
    assert send_telegram(
        "x", token="T", chat_id="1", urlopen=lambda request, timeout: FakeResponse(500)
    ) is False
