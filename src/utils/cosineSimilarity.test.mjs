import assert from "node:assert/strict";
import {
  calculateCosineSimilarity,
  verifyFaceMatch,
} from "./cosineSimilarity.js";

assert.equal(Number(calculateCosineSimilarity([1, 2, 3], [1, 2, 3]).toFixed(6)), 1);
assert.equal(Number(calculateCosineSimilarity([1, 0], [-1, 0]).toFixed(6)), -1);
assert.equal(Number(calculateCosineSimilarity([1, 0], [0, 1]).toFixed(6)), 0);
assert.equal(calculateCosineSimilarity([0, 0], [1, 1]), 0);

const match = verifyFaceMatch([0.8, 0.2, 0.1], [0.79, 0.21, 0.1], 0.6);
assert.equal(match.isMatch, true);
assert.equal(match.confidence >= 99, true);

const mismatch = verifyFaceMatch([1, 0, 0], [0, 1, 0], 0.6);
assert.equal(mismatch.isMatch, false);

assert.throws(
  () => calculateCosineSimilarity([1, 2], [1]),
  /identical length/,
);

console.log("cosineSimilarity tests passed");

