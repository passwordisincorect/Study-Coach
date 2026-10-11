// Built-in Node.js regression tests; no npm dependencies.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const source = readFileSync(new URL("../static/app.js", import.meta.url), "utf8");
const start = source.indexOf("function isUneditedLegacyStarter(");
const end = source.indexOf("function saveDraft()", start);
assert.ok(start >= 0 && end > start, "Editor draft logic missing");

const store = new Map();
let writes = 0;
const context = {
  draftKey: (id) => "draft:" + id,
  localStorage: {
    getItem: (key) => store.get(key) ?? null,
    setItem: (key, value) => { writes++; store.set(key, value); },
  },
};
vm.createContext(context);
vm.runInContext(source.slice(start, end), context);

const starter = [
  "#include <iostream>",
  "#include <cmath>",
  "#include <string>",
  "#include <vector>",
  "",
  "using namespace std;",
  "",
  "int main() {",
  "    // Viết code của bạn ở đây",
  "",
  "    return 0;",
  "}",
  "",
].join("\n");
const legacy = starter
  .replace("#include <vector>\n\nusing namespace std;", "#include <vector>\nusing namespace std;")
  .replace(/\n/g, "\n\n\n\n");

assert.equal(context.loadDraft({ id: 1, starter }), starter, "Missing draft should use clean starter");
assert.equal(writes, 0, "Missing draft should not write storage");

store.set("draft:2", legacy);
assert.equal(context.loadDraft({ id: 2, starter }), starter, "Unedited legacy draft should be repaired");
assert.equal(store.get("draft:2"), starter, "Repaired legacy draft should be saved once");
assert.equal(writes, 1);

assert.equal(context.loadDraft({ id: 2, starter }), starter);
assert.equal(writes, 1, "Already repaired draft should not be saved again");

const custom = legacy.replace("    // Viết code của bạn ở đây", "    int answer = 42;");
store.set("draft:3", custom);
assert.equal(context.loadDraft({ id: 3, starter }), custom, "User-edited draft must be preserved");
assert.equal(store.get("draft:3"), custom);
assert.equal(writes, 1, "Custom draft must not be rewritten");

const newerCustom = starter.replace("    return 0;", "    return 1;");
store.set("draft:4", newerCustom);
assert.equal(context.loadDraft({ id: 4, starter }), newerCustom);
assert.equal(store.get("draft:4"), newerCustom);
assert.equal(writes, 1);

console.log("EDITOR_DRAFT_TESTS_OK=5");
