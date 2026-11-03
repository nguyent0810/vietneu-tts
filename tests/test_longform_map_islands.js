const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("hyperframes_short/compositions/longform.js", "utf8");
const start = source.indexOf("  function appendVietnamMapInset(");
const end = source.indexOf("\n  visuals.map =", start);
assert(start >= 0 && end > start, "map inset builder should exist before map registration");
const sandbox = {};
vm.runInNewContext(source.slice(start, end), sandbox);

function node(tag, attrs = {}, text = "") {
  return { tag, ...attrs, textContent: text, children: [], dataset: {},
    appendChild(child) { this.children.push(child); return child; } };
}
const el = (tag, className, text = "") => node(tag, { className }, text);
const sv = (tag, attrs, parent) => {
  const child = node(tag, attrs);
  if (parent) parent.appendChild(child);
  return child;
};
const build = sandbox.appendVietnamMapInset;

const vietnamStage = node("stage");
const inset = build([{ name: "Vietnam" }], vietnamStage, el, sv);
assert.equal(vietnamStage.children.length, 1, "Vietnam map should add exactly one inset to the stage");
assert.equal(inset.dataset.mapInset, "vietnam-islands");
const groups = inset.children[0].children;
assert.deepEqual(groups.map((group) => group["data-island"]), ["Hoàng Sa", "Trường Sa"]);
assert(groups.every((group) => group.children.some((child) => child.tag === "circle")));
assert(groups.every((group) => group.children.some((child) => child.textContent === group["data-island"])));

const foreignStage = node("stage");
assert.equal(build([{ name: "China" }], foreignStage, el, sv), null);
assert.equal(foreignStage.children.length, 0, "foreign map should not add a Vietnam inset");
console.log("DOM regression passed: Vietnam has both island groups; China has no inset");
