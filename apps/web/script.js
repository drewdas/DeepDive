(function () {
  const btn = document.getElementById('copy-bibtex');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    const code = document.querySelector('.bibtex code');
    if (!code) return;
    const text = code.innerText;

    try {
      await navigator.clipboard.writeText(text);
    } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }

    const original = btn.textContent;
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = original;
      btn.classList.remove('copied');
    }, 1800);
  });
})();
