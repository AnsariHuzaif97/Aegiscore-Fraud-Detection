---
title: AegisCore
emoji: 🛡️
colorFrom: red
colorTo: purple
sdk: docker
pinned: false
license: mit
short_description: 'Enterprise-grade fraud intelligence platform powered by SMOTE'
---

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=40&pause=1000&color=9C27B0&center=true&vCenter=true&width=800&lines=AegisCore;Enterprise+Fraud+Intelligence;Real-Time+Anomaly+Detection;Powered+by+FastAPI" alt="Typing SVG" />
</div>

<p align="center">
  <em>High-performance, machine-learning-driven fraud detection platform designed for the modern enterprise.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
</p>

---

## 🎯 The Objective

**AegisCore** was built to solve a critical issue in financial ecosystems: identifying fraudulent transactions accurately amidst a massive sea of legitimate ones. Financial data is inherently imbalanced. AegisCore tackles this by leveraging advanced data science techniques, particularly **SMOTE (Synthetic Minority Over-sampling Technique)**, combined with an ultra-fast **FastAPI** backend and a responsive UI, ensuring zero UI lag and seamless analytics delivery.

## ✨ Enterprise Features

| Feature | Description | Technology |
| :--- | :--- | :--- |
| ⚡ **Real-Time Inference** | Low-latency prediction endpoints capable of handling high transaction volumes. | FastAPI |
| 🧠 **Advanced ML Handling** | Handles highly imbalanced datasets natively to maintain minority class accuracy. | Scikit-learn (SMOTE) |
| 📊 **Dynamic Dashboard** | Premium, modern UI with smooth transitions and high-impact analytics displays. | HTML5, Vanilla JS |
| 🐳 **Cloud-Native Deployment** | Completely containerized setup, enabling one-click deployments to Hugging Face or any cloud. | Docker |

## 🏗️ System Architecture

AegisCore utilizes a decoupled architecture for maximum scalability and performance. 

```mermaid
graph TD;
    A[Client UI - Dashboard] -->|REST API - JSON| B(FastAPI Backend);
    B --> C{ML Inference Engine};
    C -->|Loads| D[(fraud_detection_artifacts.pkl)];
    C -->|Returns Prediction| B;
    B -->|Response| A;
```

## 🚀 Deployment & Getting Started

Launch AegisCore locally or in the cloud in under a minute using Docker.

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/aegiscore.git
cd aegiscore
```

### 2. Run with Docker (Recommended)
```bash
# Build the image
docker build -t aegiscore .

# Run the container
docker run -p 7860:7860 aegiscore
```
> **Note:** Access the dynamic dashboard by navigating to `http://localhost:7860` in your web browser.

### 3. Local Development (Without Docker)
```bash
pip install -r requirements.txt
cd backend
uvicorn main:app --host 0.0.0.0 --port 7860
```

## 📂 Repository Structure

```text
aegiscore/
├── backend/                       # Core API and prediction logic
│   ├── main.py                    # FastAPI entrypoint
│   └── ml.py                      # Model loading and inference wrappers
├── frontend/                      # Presentation layer
│   ├── index.html                 # Landing page
│   └── dashboard.html             # Main analytics interface
├── fraud_detection_artifacts.pkl  # Serialized ML pipeline & Scalers
├── Dockerfile                     # Container specs for deployment
└── requirements.txt               # Backend dependencies
```

## 🛡️ License & Acknowledgements

Developed and maintained as part of a high-performance MLOps portfolio. This project is licensed under the **MIT License**.

<div align="center">
  <b>Built with passion for data security and software engineering.</b>
</div>
