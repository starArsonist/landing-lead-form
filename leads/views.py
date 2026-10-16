import logging

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import LeadForm
from .services import Outcome, client_ip, submit_lead

logger = logging.getLogger(__name__)

RATE_LIMIT_MESSAGE = "Слишком много заявок с вашего адреса. Попробуйте позже или позвоните нам."


def _wants_json(request: HttpRequest) -> bool:
    return "application/json" in request.headers.get("Accept", "")


def _utm_initial(request: HttpRequest) -> dict[str, str]:
    keys = ("utm_source", "utm_medium", "utm_campaign")
    return {key: request.GET.get(key, "")[:100] for key in keys}


@require_GET
def landing(request: HttpRequest) -> HttpResponse:
    return render(request, "leads/landing.html", {"form": LeadForm(initial=_utm_initial(request))})


@require_GET
def thanks(request: HttpRequest) -> HttpResponse:
    return render(request, "leads/thanks.html")


@require_POST
def submit(request: HttpRequest) -> HttpResponse:
    form = LeadForm(request.POST)

    if not form.is_valid():
        if _wants_json(request):
            return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)
        return render(request, "leads/landing.html", {"form": form}, status=400)

    if form.is_bot:
        # Боту отвечаем так же, как человеку, но ничего не сохраняем.
        logger.info("Отброшена заявка с заполненной ловушкой")
        return _success(request)

    result = submit_lead(form.cleaned_data, client_ip(request))
    if result.outcome is Outcome.RATE_LIMITED:
        if _wants_json(request):
            errors = {"__all__": [{"message": RATE_LIMIT_MESSAGE}]}
            return JsonResponse({"ok": False, "errors": errors}, status=429)
        form.add_error(None, RATE_LIMIT_MESSAGE)
        return render(request, "leads/landing.html", {"form": form}, status=429)

    return _success(request)


def _success(request: HttpRequest) -> HttpResponse:
    thanks_url = reverse("thanks")
    if _wants_json(request):
        return JsonResponse({"ok": True, "redirect": thanks_url})
    return redirect(thanks_url)
