from fastapi import FastAPI, UploadFile, File, Query
from app.qa import answer_question
from app.ingest import ingest_documents
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Augumented Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest")
async def upload_file(file: UploadFile = File(...)):
    return ingest_documents(file)

@app.post("/ingest-folder")
async def upload_folder(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        result = ingest_documents(file)
        results.append(result)
    return {"results": results}

@app.get("/ask")
async def ask_question(question: str = Query(...), k: int = 3):
    return answer_question(question, top_k=k)
