import tempfile
from app.utils import load_and_chunk, generate_embeddings, save_to_faiss

def ingest_documents(file):
    ext = file.filename.split(".")[-1].lower()
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file.file.read())
    temp_file_path = temp_file.name
    print(f"Temporary file created at: {temp_file_path}")
    chunks = load_and_chunk(temp_file_path, ext)
    print(f"Loaded {len(chunks)} chunks from {file.filename}")
    embeddings = generate_embeddings(chunks)
    print(f"Generated {len(embeddings)} embeddings for {file.filename}")
    save_to_faiss(embeddings, chunks, file.filename)
    print(f"Saved {len(chunks)} chunks from {file.filename} to FAISS index.")
    return {"status": "success", "chunks": len(chunks)}
