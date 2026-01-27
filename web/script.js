const buttons = document.querySelectorAll(".copy-button");

const copyText = async (text) => {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return true;
  }

  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();
  try {
    return document.execCommand("copy");
  } finally {
    document.body.removeChild(textarea);
  }
};

buttons.forEach((button) => {
  button.addEventListener("click", async () => {
    const text = button.dataset.copy;
    if (!text) {
      return;
    }
    const original = button.textContent;
    try {
      await copyText(text);
      button.classList.add("is-copied");
      button.textContent = "Copied";
      window.setTimeout(() => {
        button.classList.remove("is-copied");
        button.textContent = original;
      }, 1400);
    } catch (err) {
      button.textContent = "Failed";
      window.setTimeout(() => {
        button.textContent = original;
      }, 1400);
    }
  });
});
