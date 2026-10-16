from django import forms

from .phone import PhoneError, normalize_ru_phone


class LeadForm(forms.Form):
    name = forms.CharField(
        label="Ваше имя",
        min_length=2,
        max_length=60,
        strip=True,
        widget=forms.TextInput(
            attrs={"autocomplete": "name", "placeholder": "Как к вам обращаться"}
        ),
        error_messages={"required": "Укажите имя", "min_length": "Имя слишком короткое"},
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=30,
        widget=forms.TextInput(
            attrs={"autocomplete": "tel", "inputmode": "tel", "placeholder": "+7 (900) 123-45-67"}
        ),
        error_messages={"required": "Укажите телефон"},
    )
    message = forms.CharField(
        label="Комментарий",
        required=False,
        max_length=500,
        strip=True,
        widget=forms.Textarea(
            attrs={"rows": 3, "placeholder": "Что хотите сделать? (необязательно)"}
        ),
    )
    consent = forms.BooleanField(
        label="Согласен на обработку персональных данных",
        error_messages={"required": "Нужно согласие на обработку данных"},
    )
    # Ловушка для ботов: человек это поле не видит и не заполняет.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1"}))
    utm_source = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput)
    utm_medium = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput)
    utm_campaign = forms.CharField(required=False, max_length=100, widget=forms.HiddenInput)

    def clean_phone(self) -> str:
        try:
            return normalize_ru_phone(self.cleaned_data["phone"])
        except PhoneError as exc:
            raise forms.ValidationError(str(exc)) from exc

    @property
    def is_bot(self) -> bool:
        return bool(self.cleaned_data.get("website"))
