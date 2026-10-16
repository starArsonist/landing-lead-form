from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=60, verbose_name="Имя")),
                ("phone", models.CharField(max_length=16, verbose_name="Телефон")),
                ("message", models.TextField(blank=True, max_length=500, verbose_name="Сообщение")),
                ("utm_source", models.CharField(blank=True, max_length=100, verbose_name="utm_source")),
                ("utm_medium", models.CharField(blank=True, max_length=100, verbose_name="utm_medium")),
                ("utm_campaign", models.CharField(blank=True, max_length=100, verbose_name="utm_campaign")),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True, verbose_name="IP-адрес")),
                (
                    "status",
                    models.CharField(
                        choices=[("new", "Новая"), ("contacted", "Связались"), ("closed", "Закрыта")],
                        default="new",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                ("notified", models.BooleanField(default=False, verbose_name="Уведомление отправлено")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
            ],
            options={
                "verbose_name": "заявка",
                "verbose_name_plural": "заявки",
                "ordering": ["-created_at", "-pk"],
                "indexes": [models.Index(fields=["ip_address", "created_at"], name="lead_ip_created_idx")],
            },
        ),
    ]
