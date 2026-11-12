// Run with: node --test tests/appearance.test.cjs (no packages required).
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');
const source = readFileSync('app/static/js/app.js', 'utf8');
const css = readFileSync('app/static/css/app.css', 'utf8');

test('appearance persists, updates Bootstrap and redraws chart colors', () => {
  const root = { dataset: {} };
  const events = {};
  const selector = { addEventListener: (name, action) => { events[name] = action; } };
  const layouts = [];
  const storage = new Map([['lifetrack-theme', 'black']]);
  vm.runInNewContext(source, {
    document: {
      documentElement: root,
      addEventListener: (name, action) => { events[name] = action; },
      querySelector: () => selector,
      querySelectorAll: query => query === '.js-plotly-plot' ? [{}] : [],
    },
    localStorage: { getItem: key => storage.get(key), setItem: (key, value) => storage.set(key, value) },
    getComputedStyle: () => ({ getPropertyValue: () => '#eeeeee' }),
    window: { Plotly: { relayout: (_, layout) => layouts.push(layout) } },
  });
  events.DOMContentLoaded();
  assert.equal(selector.value, 'black');
  for (const theme of ['light', 'dark', 'black']) {
    selector.value = theme;
    events.change();
    assert.equal(root.dataset.theme, theme);
    assert.equal(root.dataset.bsTheme, theme === 'light' ? 'light' : 'dark');
    assert.equal(storage.get('lifetrack-theme'), theme);
    assert.equal(layouts.at(-1)['font.color'], '#eeeeee');
  }
});

const luminance = hex => {
  const channels = hex.match(/[a-f\d]{2}/gi).map(value => parseInt(value, 16) / 255);
  return channels.map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4)
    .reduce((sum, value, index) => sum + value * [.2126, .7152, .0722][index], 0);
};
test('text, secondary text and links meet 4.5:1 contrast in each theme', () => {
  for (const selector of [':root', ':root[data-theme="dark"]', ':root[data-theme="black"]']) {
    const block = css.slice(css.indexOf(selector + '{')).split('}')[0];
    const colors = Object.fromEntries([...block.matchAll(/--([\w-]+):#([a-f\d]+)(?=[;}])/gi)]
      .map(([, key, hex]) => [key, hex.length === 3 ? hex.split('').map(c => c + c).join('') : hex]));
    for (const foreground of ['ink', 'muted', 'accent']) {
      for (const background of ['paper', 'canvas']) {
        const values = [luminance(colors[foreground]), luminance(colors[background])].sort((a, b) => b - a);
        assert.ok((values[0] + .05) / (values[1] + .05) >= 4.5, `${selector}: ${foreground}/${background}`);
      }
    }
  }
});
