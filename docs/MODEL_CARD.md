# Model Card

## Current Status

The project currently has a temporary embedding baseline for pipeline testing. It is not the final recognition model and must not be presented as production face recognition accuracy.

The final recognition target is MobileFaceNet or a MobileFaceNet-style lightweight embedding model exported to TFLite or ONNX.

## Final Recognition Model Target

| Field | Target |
|---|---|
| Model family | MobileFaceNet |
| Training objective | ArcFace-style metric learning loss |
| Input | 112x112 aligned face crop |
| Output | 128-d or 192-d embedding vector depending on selected model |
| Runtime target | TFLite or ONNX Runtime Mobile |
| Optimization | INT8 quantization |
| Matching | Cosine similarity |
| Storage | Encrypted local embedding, not raw face image |

## Candidate Sources

### Option A: Train/convert from an open implementation

- Candidate: `foamliu/MobileFaceNet`
- Notes: PyTorch implementation of MobileFaceNets
- License observed: Apache-2.0
- Use case: suitable as a transparent training/conversion reference
- Risk: pretrained weights/source still need to be verified before redistribution

### Option B: Use a MobileFaceNet TFLite model from a mobile demo repository

- Candidate: Flutter MobileFaceNet demo repositories
- Notes: may include `mobilefacenet.tflite`
- Use case: fast hackathon prototype
- Risk: model weight provenance and redistribution rights must be checked before final claim

### Option C: InsightFace model zoo

- Candidate: InsightFace ONNX models
- Notes: strong recognition ecosystem
- License caution: InsightFace Python code is MIT, but provided pretrained models are described as non-commercial research only
- Use case: research benchmark only unless licensing is resolved

## Current Repository Files

Expected final model file names:

```txt
models/mobilefacenet.tflite
models/mobilefacenet.onnx
```

Only one is needed. Do not commit a model file until its license and source are documented.

## Temporary Embedding Baseline

Current script:

```txt
python-scripts/embedding_baseline.py
```

Purpose:

- Validate `112x112 crop -> 128-number vector -> cosine similarity -> match CSV`
- Test enrollment/verification plumbing
- Produce benchmark outputs

Limitation:

- It is based on simple image statistics, not AI face recognition
- It can produce high scores for different face photos
- It must be replaced by MobileFaceNet before final accuracy claims

## Acceptance Criteria For Final Model

- Model source and license documented
- Model file size recorded in `docs/BENCHMARKS.md`
- Embedding shape verified
- Same-person and different-person scores measured
- Threshold chosen from observed data, not guessed
- Mobile inference path documented
- README claims updated only after measurement

