(() => {
  const root = document.documentElement;
  const validThemes = ['light', 'dark', 'black'];
  let savedTheme;
  try { savedTheme = localStorage.getItem('lifetrack-theme'); } catch { /* Storage may be disabled. */ }
  const applyTheme = theme => {
    root.dataset.theme = validThemes.includes(theme) ? theme : 'light';
    root.dataset.bsTheme = root.dataset.theme === 'light' ? 'light' : 'dark';
    if (window.Plotly) {
      const styles = getComputedStyle(root);
      document.querySelectorAll('.js-plotly-plot').forEach(chart => {
        window.Plotly.relayout(chart, {
          paper_bgcolor: styles.getPropertyValue('--paper').trim(),
          plot_bgcolor: styles.getPropertyValue('--paper').trim(),
          'font.color': styles.getPropertyValue('--ink').trim(),
          'xaxis.gridcolor': styles.getPropertyValue('--line').trim(),
          'yaxis.gridcolor': styles.getPropertyValue('--line').trim(),
          'xaxis.zerolinecolor': styles.getPropertyValue('--line').trim(),
          'yaxis.zerolinecolor': styles.getPropertyValue('--line').trim(),
        });
      });
    }
  };
  applyTheme(savedTheme);
  document.addEventListener('DOMContentLoaded', () => {
    applyTheme(root.dataset.theme);
    const selector = document.querySelector('[data-theme-select]');
    if (selector) {
      selector.value = root.dataset.theme;
      selector.addEventListener('change', () => {
        applyTheme(selector.value);
        try { localStorage.setItem('lifetrack-theme', root.dataset.theme); } catch { /* Theme still applies for this page. */ }
      });
    }
    document.querySelectorAll('.nav-link').forEach(link => {
      if (link.pathname === window.location.pathname) link.setAttribute('aria-current', 'page');
    });
    document.querySelectorAll('form[data-confirm]').forEach(form => form.addEventListener('submit', event => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    }));
  });
})();
