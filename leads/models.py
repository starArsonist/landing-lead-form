from django.db import models

from .phone import format_ru_phone


class Lead(models.Model):
    """Заявка с лендинга."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        CONTACTED = "contacted", "Связались"
        CLOSED = "closed", "Закрыта"

    name = models.CharField("Имя", max_length=60)
    phone = models.CharField("Телефон", max_length=16)
    message = models.TextField("Сообщение", max_length=500, blank=True)
    utm_source = models.CharField("utm_source", max_length=100, blank=True)
    utm_medium = models.CharField("utm_medium", max_length=100, blank=True)
    utm_campaign = models.CharField("utm_campaign", max_length=100, blank=True)
    ip_address = models.GenericIPAddressField("IP-адрес", null=True, blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    notified = models.BooleanField("Уведомление отправлено", default=False)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "заявка"
        verbose_name_plural = "заявки"
        ordering = ["-created_at", "-pk"]
        indexes = [models.Index(fields=["ip_address", "created_at"], name="lead_ip_created_idx")]

    def __str__(self) -> str:
        return f"{self.name}, {self.phone_display}"

    @property
    def phone_display(self) -> str:
        return format_ru_phone(self.phone)
