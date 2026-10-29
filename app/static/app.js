/* Grand Stay Hotel - small progressive enhancements.
   Every form still works without JavaScript; the server validates everything.
   1. Mobile menu   2. Dismissible messages   3. Show/hide password
   4. Date range helpers   5. Inline field validation   6. Confirm dialog */
(function () {
  "use strict";

  // 1. Mobile menu --------------------------------------------------------
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  // 2. Dismissible flash messages ----------------------------------------
  document.querySelectorAll("[data-dismiss]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var msg = btn.closest(".flash");
      if (msg) msg.remove();
    });
  });

  // 3. Show / hide password ----------------------------------------------
  document.querySelectorAll("[data-toggle-password]").forEach(function (btn) {
    var input = document.getElementById(btn.getAttribute("data-toggle-password"));
    if (!input) return;
    btn.addEventListener("click", function () {
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.textContent = show ? "Hide" : "Show";
      btn.setAttribute("aria-pressed", String(show));
      btn.setAttribute("aria-label", show ? "Hide password" : "Show password");
    });
  });

  // 4. Date range: no past check-in, check-out after check-in --------------
  function isoDate(d) {
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return d.getFullYear() + "-" + m + "-" + day;
  }
  function addDays(iso, n) {
    var p = iso.split("-").map(Number);
    return isoDate(new Date(p[0], p[1] - 1, p[2] + n));
  }
  document.querySelectorAll("[data-date-range]").forEach(function (form) {
    var checkIn = form.querySelector("[name=check_in]");
    var checkOut = form.querySelector("[name=check_out]");
    if (!checkIn || !checkOut) return;
    var today = isoDate(new Date());
    checkIn.min = today;
    function updateMin() {
      checkOut.min = addDays(checkIn.value || today, 1);
    }
    checkIn.addEventListener("change", function () {
      updateMin();
      // Only when the guest moves check-in past check-out: suggest one night.
      // (Never on page load - the form must show exactly what was searched.)
      if (checkIn.value && checkOut.value && checkOut.value <= checkIn.value) {
        checkOut.value = addDays(checkIn.value, 1);
      }
    });
    updateMin();
  });

  // 5. Inline field validation (forms marked data-validate) -------------
  var messages = {
    valueMissing: function (label) { return "Enter your " + label.toLowerCase() + "."; },
    typeMismatch: function () { return "Enter an email address like name@example.com."; },
    tooShort: function (label, input) { return "Use at least " + input.minLength + " characters."; }
  };
  function fieldMessage(input) {
    var label = (document.querySelector("label[for='" + input.id + "']") || {}).textContent || "value";
    var v = input.validity;
    if (v.valueMissing) return messages.valueMissing(label.trim());
    if (v.typeMismatch) return messages.typeMismatch();
    if (v.tooShort || (input.minLength > 0 && input.value.length < input.minLength)) return messages.tooShort(label, input);
    return "";
  }
  function showError(input) {
    var box = document.querySelector("[data-error-for='" + input.id + "']");
    var msg = fieldMessage(input);
    if (box) { box.textContent = msg; box.hidden = !msg; }
    if (msg) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
    return !msg;
  }
  document.querySelectorAll("form[data-validate]").forEach(function (form) {
    var inputs = form.querySelectorAll("input[required], input[minlength]");
    inputs.forEach(function (input) {
      input.addEventListener("blur", function () { if (input.value) showError(input); });
      input.addEventListener("input", function () { if (input.getAttribute("aria-invalid")) showError(input); });
    });
    form.addEventListener("submit", function (e) {
      var firstBad = null;
      inputs.forEach(function (input) { if (!showError(input) && !firstBad) firstBad = input; });
      if (firstBad) { e.preventDefault(); firstBad.focus(); }
    });
  });

  // 6. Confirmation dialog for forms marked data-confirm ------------------
  var dialog = document.getElementById("confirm-dialog");
  if (dialog && typeof dialog.showModal === "function") {
    var pending = null, opener = null;
    var title = document.getElementById("confirm-dialog-title");
    var body = document.getElementById("confirm-dialog-body");
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        pending = form;
        opener = document.activeElement;
        if (form.dataset.confirmTitle) title.textContent = form.dataset.confirmTitle;
        if (form.dataset.confirmBody) body.textContent = form.dataset.confirmBody;
        dialog.showModal();
        dialog.querySelector("[data-dialog-close]").focus();   // safe choice first
      });
    });
    dialog.querySelector("[data-dialog-close]").addEventListener("click", function () { dialog.close(); });
    dialog.querySelector("[data-dialog-confirm]").addEventListener("click", function (e) {
      if (!pending) return;
      e.currentTarget.disabled = true;      // no double submits
      HTMLFormElement.prototype.submit.call(pending);   // skips the submit listener above
    });
    dialog.addEventListener("close", function () {
      if (opener && document.contains(opener)) opener.focus();
      pending = null;
    });
  }
})();
