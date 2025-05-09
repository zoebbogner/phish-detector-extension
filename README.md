# Multi-Layered Phishing Detection Browser Extension

This project implements a three-layer phishing detection system (URL, content, behavior) as a Chrome browser extension. Detection is powered by a stacked ensemble model trained in Python and exported to JavaScript for on-device inference.

## Structure

- `data/`: raw and processed phishing/benign datasets
- `models/`: trained base ML models
- `meta/`: boosted meta-learner for stacking
- `extension/`: Chrome extension source (manifest, popup, JS, icons)
- `utils/`: Python feature extraction scripts
- `notebooks/`: Jupyter development notebooks
- `report/`: final write-up and visualizations

## Goals

- Detect phishing in real time using multiple detection layers
- Achieve high TPR and low FPR on unseen data
- Ensure fast response time and low memory footprint

## Authors

- Zoe Bogner
- Ilai Shohat