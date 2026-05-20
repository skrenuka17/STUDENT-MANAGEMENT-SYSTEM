// EduTrack — Global JS Utilities

// ── MODAL HELPERS ────────────────────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) {
    el.classList.remove("hidden");
    // Focus first input inside
    const first = el.querySelector("input:not([disabled]), select");
    if (first) setTimeout(() => first.focus(), 100);
  }
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add("hidden");
}

// Close modal on overlay click
document.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-overlay")) {
    e.target.classList.add("hidden");
  }
});

// Close modal on ESC
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-overlay:not(.hidden)").forEach(m => m.classList.add("hidden"));
  }
});

// ── TOAST HELPER ─────────────────────────────────────────────────────────────
let toastTimeout;
function showToast(message, success = true) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  clearTimeout(toastTimeout);
  toast.textContent = message;
  toast.className = `toast ${success ? "success" : "error"}`;
  toastTimeout = setTimeout(() => {
    toast.className = "toast hidden";
  }, 3500);
}
