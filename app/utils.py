import os, pickle, csv
from PyPDF2 import PdfReader
import faiss
from sentence_transformers import SentenceTransformer
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForCausalLM
)
import torch
from huggingface_hub import login
from dotenv import load_dotenv

# Get env variables
HF_TOKEN_KEY = os.getenv("HF_TOKEN_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")
DEVICE = os.getenv("DEVICE")
INDEX_FILE = os.getenv("INDEX_FILE")
DOC_STORE = os.getenv("DOC_STORE")

# Set Hugging Face token
login(token=HF_TOKEN_KEY)

# ==== Lightweight Embedding Model ====
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def get_embeddings(texts):
    return embedder.encode(texts, convert_to_numpy=True)


# Load HF Model for Inference ====
model_name = MODEL_NAME
tokenizer = AutoTokenizer.from_pretrained(model_name)

generator = pipeline("text-generation", model=model_name, tokenizer=tokenizer, device=-1)


if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
else:
    index = faiss.IndexFlatL2(384)  # Dimension for MiniLM

try:
    with open(DOC_STORE, "rb") as f:
        documents = pickle.load(f)
except:
    documents = []

# ==== Load and Chunk Document ====
def load_and_chunk(filepath, ext):
    text = ""
    if ext == "pdf":
        reader = PdfReader(filepath)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == "txt":
        with open(filepath, 'r') as f:
            text = f.read()
    elif ext == "csv":
        with open(filepath, newline='') as f:
            reader = csv.reader(f)
            text = "\n".join([", ".join(row) for row in reader])
    return [text[i:i+500] for i in range(0, len(text), 500)]

# ==== Generate Embeddings ====
def generate_embeddings(chunks):
    return get_embeddings(chunks)

# ==== Save to Vector DB ====
def save_to_faiss(embeddings, chunks, filename):
    global documents
    print(f"Adding {len(chunks)} chunks from {filename} to FAISS index.")
    index.add(embeddings)
    documents.extend([(chunk, filename) for chunk in chunks])
    faiss.write_index(index, INDEX_FILE)
    with open(DOC_STORE, "wb") as f:
        pickle.dump(documents, f)

# ==== Search Similar Chunks ====
def search_faiss(query, k):
    print(f"Searching for top {k} chunks for query: {query}")
    query_emb = get_embeddings([query])
    D, I = index.search(query_emb, k)
    return [documents[i][0] for i in I[0]]

# ==== Generate Answer from LLM ====
def generate_answer(question, contexts):
    context_str = "\n".join(contexts)
    prompt = f"[INST] Use the following context to answer the question:\n{context_str}\n\nQuestion: {question} [/INST]"
    
    result = generator(prompt, max_new_tokens=256, do_sample=True)
    return result[0]["generated_text"]