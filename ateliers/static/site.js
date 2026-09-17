/* Only source-site behavior: dependent fields and same-tab drafts. No AI. */
"use strict";
(() => {
  document.querySelector('[data-help-launch]')?.addEventListener('submit', () => {
    try { sessionStorage.setItem('adq:help-open', '1'); } catch (_) {}
  });
  document.addEventListener('visibilitychange', () => {
    try {
      if (document.visibilityState === 'visible' && sessionStorage.getItem('adq:help-open') === '1') {
        window.location.reload();
      }
    } catch (_) {}
  });
  const cleared = document.querySelector("[data-clear-draft]");
  if (cleared) {
    try { sessionStorage.removeItem(`adq:${cleared.dataset.session}:${cleared.dataset.clearDraft}`); } catch (_) {}
  }
  const form = document.querySelector("form[data-draft]");
  if (!form) return;
  const key = `adq:${form.dataset.session}:${form.dataset.draft}`;
  const controls = [...form.elements].filter(el => el.name && el.name !== "csrf" && el.type !== "password" && el.type !== "submit");
  const catalogNode = document.getElementById("catalog-data");
  const catalog = catalogNode ? JSON.parse(catalogNode.textContent) : null;
  const activity = document.getElementById("activity");
  const slot = document.getElementById("slot");

  function updateActivity(previousSlot = "") {
    if (!activity) return;
    const selection = catalog[activity.value];
    slot.replaceChildren(new Option("Sélectionner", ""));
    if (selection) {
      Object.entries(selection.slots).forEach(([value, label]) => slot.add(new Option(label, value)));
    }
    slot.disabled = !selection;
    slot.value = selection && Object.hasOwn(selection.slots, previousSlot) ? previousSlot : "";
  }

  function saveDraft() {
    const draft = {};
    for (const control of controls) {
      if (control.type === "checkbox") {
        draft[control.name] ??= [];
        if (control.checked) draft[control.name].push(control.value);
      } else draft[control.name] = control.value;
    }
    try { sessionStorage.setItem(key, JSON.stringify(draft)); } catch (_) {}
  }

  if (form.dataset.hasErrors !== "true") {
    try {
      const draft = JSON.parse(sessionStorage.getItem(key) || "null");
      if (draft && typeof draft === "object") {
        for (const control of controls) {
          if (control.name === "slot") continue;
          if (control.type === "checkbox") control.checked = Array.isArray(draft[control.name]) && draft[control.name].includes(control.value);
          else if (typeof draft[control.name] === "string") control.value = draft[control.name];
        }
        updateActivity(typeof draft.slot === "string" ? draft.slot : "");
      } else updateActivity(slot?.value);
    } catch (_) { updateActivity(slot?.value); }
  } else updateActivity(slot?.value);

  activity?.addEventListener("change", () => { updateActivity(); saveDraft(); });
  form.addEventListener("input", saveDraft);
  form.addEventListener("change", saveDraft);
  form.addEventListener("submit", () => {
    saveDraft();
    // Server uniqueness constraints remain authoritative for duplicate requests.
    form.querySelector('button[type="submit"]').disabled = true;
  });
  window.addEventListener("pagehide", saveDraft);
  window.addEventListener("pageshow", () => {
    form.querySelector('button[type="submit"]').disabled = false;
  });
  saveDraft();
})();
