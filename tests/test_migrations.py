from django.core.management import call_command


def test_migrations_match_models(db):
    """Если модель изменили, а миграцию не создали, команда завершится с ошибкой."""
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)
