"""Нормализация российских номеров телефона. Не зависит от Django."""
import re


class PhoneError(ValueError):
    """Номер нельзя привести к формату +7XXXXXXXXXX."""


_NON_DIGITS = re.compile(r"\D")
# Первая цифра кода: 3 (Москва и центр), 4, 8 (в т. ч. 800), 9 (мобильные).
_VALID_FIRST_DIGIT = "3489"


def normalize_ru_phone(raw: str) -> str:
    """Привести номер к виду ``+7XXXXXXXXXX``.

    Принимает ``+7 (912) 345-67-89``, ``8 912 345 67 89``, ``79123456789`` и ``9123456789``.
    """
    digits = _NON_DIGITS.sub("", raw or "")

    if len(digits) == 11 and digits[0] in "78":
        digits = digits[1:]
    elif len(digits) != 10:
        raise PhoneError("Введите номер в формате +7 (900) 123-45-67")

    if digits[0] not in _VALID_FIRST_DIGIT:
        raise PhoneError("Похоже, номер указан неверно: проверьте код оператора")
    if len(set(digits)) == 1:
        raise PhoneError("Похоже, номер указан неверно: все цифры одинаковые")

    return f"+7{digits}"


def format_ru_phone(normalized: str) -> str:
    """``+79123456789`` -> ``+7 (912) 345-67-89``; чужой формат возвращается как есть."""
    match = re.fullmatch(r"\+7(\d{3})(\d{3})(\d{2})(\d{2})", normalized)
    if not match:
        return normalized
    code, first, second, third = match.groups()
    return f"+7 ({code}) {first}-{second}-{third}"
