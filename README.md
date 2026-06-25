
<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=0:0052D4,100:4364F7,200:6FB1FC&height=250&section=header&text=AegisCore&fontSize=80&fontAlignY=35&animation=twinkling&fontColor=ffffff&desc=Fraud%20Intelligence%20Platform&descAlignY=55&descSize=20" width="100%" />
</div>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=30&pause=1000&color=4364F7&center=true&vCenter=true&width=800&lines=Enterprise+Fraud+Intelligence;Real-Time+Anomaly+Detection;Powered+by+FastAPI;SMOTE+Imbalance+Handling" alt="Typing SVG" />
</div>

<p align="center">
  <em>High-performance, machine-learning-driven fraud detection platform designed for the modern enterprise.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-0052D4?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/scikit--learn-4364F7?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/JavaScript-6FB1FC?style=for-the-badge&logo=javascript&logoColor=white" alt="JavaScript">
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
git clone https://github.com/AnsariHuzaif97/Aegiscore-Fraud-Detection.git
cd Aegiscore-Fraud-Detection
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

Developed and maintained by [AnsariHuzaif97](https://github.com/AnsariHuzaif97). This project is licensed under the **MIT License**.

<div align="center">
  <b>Built with passion for data security and software engineering.</b>
</div>
