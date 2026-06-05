# Python Model Lab

This folder contains development-time scripts for preprocessing, model preparation, benchmarking, and explainability.

These scripts are not the mobile app. They are used to prepare evidence, convert models, and measure real performance before making claims in the README or presentation.

## First Scripts

- `clahe_preprocess.py`: applies CLAHE lighting normalization to an image or folder of images.
- `create_sample_images.py`: creates synthetic lighting samples for a safe first test.
- `benchmark_pipeline.py`: records timing and model file-size measurements.

## Install Requirements

```powershell
pip install -r requirements.txt
```

## Planned Scripts

- `convert_mobilefacenet.py`
- `convert_fasnet.py`
- `evaluate_embeddings.py`
- `generate_gradcam.py`

## Rule

Any number used in the final presentation should come from a script output, benchmark table, or saved evidence file.
