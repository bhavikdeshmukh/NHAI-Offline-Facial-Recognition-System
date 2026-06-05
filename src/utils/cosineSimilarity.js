/**
 * Calculates cosine similarity between two face embedding vectors.
 * Formula: (A dot B) / (||A|| * ||B||)
 */
export function calculateCosineSimilarity(vectorA, vectorB) {
  if (!Array.isArray(vectorA) || !Array.isArray(vectorB)) {
    throw new Error("Embedding vectors must be arrays.");
  }

  if (vectorA.length !== vectorB.length) {
    throw new Error("Embedding vectors must be of identical length.");
  }

  if (vectorA.length === 0) {
    return 0;
  }

  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let index = 0; index < vectorA.length; index += 1) {
    const valueA = Number(vectorA[index]);
    const valueB = Number(vectorB[index]);

    if (!Number.isFinite(valueA) || !Number.isFinite(valueB)) {
      throw new Error("Embedding vectors must contain only finite numbers.");
    }

    dotProduct += valueA * valueB;
    normA += valueA * valueA;
    normB += valueB * valueB;
  }

  if (normA === 0 || normB === 0) {
    return 0;
  }

  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

/**
 * Validates a live face embedding against a stored embedding template.
 */
export function verifyFaceMatch(liveEmbedding, storedEmbedding, threshold = 0.6) {
  const score = calculateCosineSimilarity(liveEmbedding, storedEmbedding);
  const confidence = Math.max(0, Math.min(100, ((score + 1) / 2) * 100));

  return {
    isMatch: score >= threshold,
    score,
    confidence: Math.round(confidence),
  };
}

