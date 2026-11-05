// Inspect actual engine registrations in an isolated VM; never execute scene builders.
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const root = process.argv[2];
const element = () => ({style: {}, appendChild() {}, removeChild() {}});
const document = {documentElement: element(), head: element(), createElement: element,
  querySelector: element, getElementById: element};
const window = {CASE: {dur: 1, theme: {}, look: {}, imgs: {}}, __SCENE_TYPES_ONLY: true};
const context = vm.createContext({window, document, gsap: {timeline: () => ({})}, makeBeat: () => ({SLAM: {}, beat: () => {}}), console});
vm.runInContext(fs.readFileSync(path.join(root, "casefile.js"), "utf8"), context, {timeout: 5000});
if (!Array.isArray(window.__SCENE_TYPES) || !window.__SCENE_TYPES.length) throw Error("scene registry unavailable");
const devices = {};
context.HFS = {device(name, definition) {
  if (typeof name !== "string" || Object.hasOwn(devices, name)) throw Error("invalid or duplicate device: " + name);
  if (!definition || typeof definition.build !== "function") throw Error("invalid device builder: " + name);
  devices[name] = context.currentFile;
}};
for (const file of fs.readdirSync(path.join(root, "hfs")).filter(f => f.endsWith(".js") && f !== "bridge.js").sort()) {
  context.currentFile = path.basename(file, ".js");
  vm.runInContext(fs.readFileSync(path.join(root, "hfs", file), "utf8"), context, {timeout: 5000});
}
process.stdout.write(JSON.stringify({scenes: window.__SCENE_TYPES, devices}));

