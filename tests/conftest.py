import pytest


@pytest.fixture
def payload():
    return {
        "name": "Анна",
        "phone": "8 (912) 345-67-89",
        "message": "Нужна смета на двушку",
        "consent": "on",
        "website": "",
        "utm_source": "ads",
        "utm_medium": "cpc",
        "utm_campaign": "autumn",
    }


@pytest.fixture(autouse=True)
def no_real_telegram(settings):
    """Тесты никогда не должны ходить в сеть: токен пустой, отправка пропускается."""
    settings.TELEGRAM_BOT_TOKEN = ""
    settings.TELEGRAM_CHAT_ID = ""
