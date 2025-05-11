# RAG based Chatbot (Optimized with HuggingFace + Quantization)

A Retrieval-Augmented Generation chatbot that ingests documents, stores embeddings in FAISS, and answers using a quantized HuggingFace model.

## 🛠️ Local Setup

```bash
git clone <repo-url>
cd augumentalchat
pip install -r requirements.txt
uvicorn app.main:app --reload
```
browse the swagger docs at http://localhost:8000/docs

## Docker

```bash
docker-compose build
docker-compose up
