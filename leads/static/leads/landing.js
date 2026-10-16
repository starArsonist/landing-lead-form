// Прогрессивное улучшение: без JS форма отправляется обычным POST и работает так же.
(function () {
  "use strict";

  var form = document.getElementById("lead");
  if (!form) return;
  var status = document.getElementById("form-status");
  var button = form.querySelector("button[type=submit]");

  function clearErrors() {
    form.querySelectorAll(".error, .form-error").forEach(function (node) { node.remove(); });
    status.textContent = "";
  }

  function showError(field, text) {
    var holder = form.querySelector('[name="' + field + '"]');
    var p = document.createElement("p");
    p.className = "error";
    p.textContent = text;
    if (holder) holder.closest(".field").appendChild(p);
    else status.textContent = text;
  }

  // Подставляем +7 и расставляем скобки/дефисы, не мешая удалять символы.
  var phone = form.querySelector('[name="phone"]');
  phone.addEventListener("input", function (event) {
    if (event.inputType && event.inputType.indexOf("delete") === 0) return;
    var digits = phone.value.replace(/\D/g, "");
    if (digits[0] === "8" || digits[0] === "7") digits = digits.slice(1);
    digits = digits.slice(0, 10);
    var out = digits.length ? "+7 (" + digits.slice(0, 3) : "";
    if (digits.length >= 3) out += ") " + digits.slice(3, 6);
    if (digits.length >= 6) out += "-" + digits.slice(6, 8);
    if (digits.length >= 8) out += "-" + digits.slice(8, 10);
    phone.value = out;
  });

  form.addEventListener("submit", function (event) {
    if (!window.fetch) return;
    event.preventDefault();
    clearErrors();
    button.disabled = true;
    status.textContent = "Отправляем…";

    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { "Accept": "application/json" },
      credentials: "same-origin"
    })
      .then(function (response) {
        return response.json().then(function (data) { return { ok: response.ok, data: data }; });
      })
      .then(function (res) {
        if (res.ok && res.data.ok) {
          window.location.href = res.data.redirect;
          return;
        }
        status.textContent = "";
        var errors = res.data.errors || {};
        Object.keys(errors).forEach(function (field) {
          errors[field].forEach(function (item) {
            showError(field === "__all__" ? "" : field, item.message);
          });
        });
      })
      .catch(function () {
        status.textContent = "Не удалось отправить заявку. Проверьте соединение и попробуйте ещё раз.";
      })
      .then(function () { button.disabled = false; });
  });
})();
