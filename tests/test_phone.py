import pytest

from leads.phone import PhoneError, format_ru_phone, normalize_ru_phone


@pytest.mark.parametrize(
    "raw",
    [
        "+7 (912) 345-67-89",
        "8 912 345 67 89",
        "89123456789",
        "79123456789",
        "9123456789",
        "  +7-912-345-67-89  ",
        "+7(912)3456789",
    ],
)
def test_valid_formats_are_normalized(raw):
    assert normalize_ru_phone(raw) == "+79123456789"


def test_landline_codes_are_accepted():
    assert normalize_ru_phone("8 (495) 123-45-67") == "+74951234567"
    assert normalize_ru_phone("8 800 555-35-35") == "+78005553535"


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "abc",
        "12345",
        "+7 912 345 67",          # слишком короткий
        "+7 912 345 67 89 0",     # слишком длинный
        "+1 212 555 01 99",       # не российский номер
        "2123456789",             # код не может начинаться на 2
        "9999999999",             # все цифры одинаковые
    ],
)
def test_invalid_numbers_are_rejected(raw):
    with pytest.raises(PhoneError):
        normalize_ru_phone(raw)


def test_none_is_rejected():
    with pytest.raises(PhoneError):
        normalize_ru_phone(None)


def test_format_for_display():
    assert format_ru_phone("+79123456789") == "+7 (912) 345-67-89"
    assert format_ru_phone("12345") == "12345"
