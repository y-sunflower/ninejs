(function () {
  var cachedText = null;

  function setStatus(status, message) {
    if (!status) return;
    status.textContent = message;
    if (message) {
      setTimeout(function () {
        status.textContent = "";
      }, 2000);
    }
  }

  async function getLlmsText() {
    if (cachedText !== null) return cachedText;
    var res = await fetch(new URL("llms.txt", document.baseURI), {
      cache: "no-store",
    });
    if (!res.ok) throw new Error("Failed to fetch llms.txt: " + res.status);
    cachedText = await res.text();
    return cachedText;
  }

  async function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      return;
    }

    var textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }

  function initLlmsButtons() {
    var copyBtn = document.getElementById("llms-copy");
    var viewBtn = document.getElementById("llms-view");
    var preview = document.getElementById("llms-preview");
    var previewContent = document.getElementById("llms-preview-content");
    var status = document.getElementById("llms-status");

    if (copyBtn && !copyBtn.dataset.llmsReady) {
      copyBtn.dataset.llmsReady = "true";
      copyBtn.addEventListener("click", async function () {
        try {
          await copyText(await getLlmsText());
          setStatus(status, "Copied");
        } catch (e) {
          setStatus(status, "Copy failed");
        }
      });
    }

    if (viewBtn && preview && previewContent && !viewBtn.dataset.llmsReady) {
      viewBtn.dataset.llmsReady = "true";
      viewBtn.addEventListener("click", async function () {
        if (preview.classList.contains("is-open")) {
          preview.classList.remove("is-open");
          viewBtn.setAttribute("aria-expanded", "false");
          viewBtn.textContent = "View";
          return;
        }

        try {
          previewContent.textContent = await getLlmsText();
          preview.classList.add("is-open");
          viewBtn.setAttribute("aria-expanded", "true");
          viewBtn.textContent = "Hide";
        } catch (e) {
          setStatus(status, "Load failed");
        }
      });
    }
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(initLlmsButtons);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLlmsButtons);
  } else {
    initLlmsButtons();
  }
})();
