(() => {
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  const storageKey = 'panda-docs-theme';
  let preference;
  try {
    const stored = localStorage.getItem(storageKey);
    if (stored === 'light' || stored === 'dark') preference = stored;
  } catch {
    // The toggle still works when browser storage is unavailable.
  }

  function applyTheme() {
    const theme = preference || (system.matches ? 'dark' : 'light');
    root.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')
      ?.setAttribute('content', theme === 'dark' ? '#181818' : '#392c73');
    const toggle = document.querySelector('#theme-toggle');
    if (toggle) {
      // Name the theme the button switches to, so it never reads "Dark mode" on a dark page.
      const next = theme === 'dark' ? 'light' : 'dark';
      toggle.hidden = false;
      toggle.textContent = next === 'dark' ? 'Dark mode' : 'Light mode';
      toggle.setAttribute('aria-label', `Switch to ${next} mode`);
    }
  }

  // Run before the stylesheet so a saved dark theme does not flash light.
  applyTheme();
  system.addEventListener('change', () => {
    if (!preference) applyTheme();
  });
  document.addEventListener('DOMContentLoaded', () => {
    applyTheme();
    document.querySelector('#theme-toggle').addEventListener('click', () => {
      preference = root.dataset.theme === 'dark' ? 'light' : 'dark';
      try {
        localStorage.setItem(storageKey, preference);
      } catch {
        // Keep this page usable even when the preference cannot be saved.
      }
      applyTheme();
    });
  });
})();
