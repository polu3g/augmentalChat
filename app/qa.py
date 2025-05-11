from app.utils import search_faiss, generate_answer

def answer_question(question: str, top_k: int):
    relevant_chunks = search_faiss(question, k=top_k)
    return {"answer": generate_answer(question, relevant_chunks)}
