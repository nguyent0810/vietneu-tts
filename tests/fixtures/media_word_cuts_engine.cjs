// Exercise the real engine/longform with a DOM and record scheduled tweens.
const fs = require('fs');
const vm = require('vm');
const { parseHTML } = require(process.env.HF_TEST_LINKEDOM);
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const { window } = parseHTML(`<html data-resolution="landscape"><body class="wide">
<div id="root"><div id="stage"></div><div id="capzone"></div></div></body></html>`);
const { document } = window;
const scheduled = [];
function record(targets, props, at) {
  if (!targets) return timeline;
  if (!targets.nodeType && typeof targets !== 'string' && targets[Symbol.iterator]) {
    Array.from(targets).forEach(t => record(t, props, at));
  } else {
    scheduled.push({ target: targets.id || targets.className || 'helper',
      start: Number(at) || 0, end: (Number(at) || 0) + (Number(props.duration) || 0), props });
  }
  return timeline;
}
const timeline = {
  fromTo: (t, from, to, at) => record(t, to, at),
  to: (t, props, at) => record(t, props, at),
  set: (t, props, at) => record(t, { ...props, duration: 0 }, at),
  seek: () => timeline,
};
const gsap = { timeline: () => timeline, set: () => {}, getProperty: () => 0 };
const styles = (node) => ({
  width: '1920px', height: '1080px', left: '0px', top: '0px',
  getPropertyValue: (key) => key === '--lf-theme' ? 'night' : '',
});
window.__timelines = {};
window.__hyperframes = { getVariables: () => ({
  lines: input.lines, duration: 160, series: 'bud', accent: '#aa8833', seg_off: 0,
}) };
for (const ln of input.lines) {
  if (!ln.media) continue;
  const clip = document.createElement('img');
  clip.id = 'mediaclip' + ln.sentence_id;
  clip.className = 'media-clip';
  if (ln.media.cine) clip.dataset.cine = '1';
  document.getElementById('root').appendChild(clip);
}
// This fixture checks scheduled transforms, not pixels or the O9 raster gate.
const context = vm.createContext({ window, document, console: { log() {}, error() {} }, gsap, getComputedStyle: styles });
vm.runInContext(fs.readFileSync(input.root + '/hyperframes_short/compositions/engine.js', 'utf8'), context);
context.HF = window.HF;
vm.runInContext(fs.readFileSync(input.root + '/hyperframes_short/compositions/longform.js', 'utf8'), context);
// Keep two plain shots on the Ken Burns path, plus cine and a framed shot.
window.HF_LONG.begin = () => {};
window.HF_STYLE = { buildMediaScene: () => {}, enterMedia: () => {},
  transition: () => {} };
window.HF.build();
const cameras = scheduled.filter(s => /^mediaclip/.test(s.target) && s.end > s.start &&
  ['scale', 'x', 'y', 'xPercent', 'yPercent', 'rotation', 'rotationX', 'rotationY']
    .some(k => Object.hasOwn(s.props, k)));
const captions = Array.from(document.querySelectorAll('#capzone > .cap'))
  .map(n => n.children.length);
process.stdout.write(JSON.stringify({ cameras, captions }));
