import os
import json
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
# import OpenRouterEmmbedding
from dotenv import load_dotenv
import openai

load_dotenv()
api_key = os.getenv("OPEN_ROUTER_API_KEY")

# Set OpenRouter endpoint and key
openai.api_key = api_key
openai.api_base = "https://openrouter.ai/api/v1"

import requests



print("Loaded API key:", os.getenv("OPEN_ROUTER_API_KEY")) 
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR=os.path.join(BASE_DIR, "DATA", "Embedded")
VECTOR_DIR= os.path.join(BASE_DIR, "MODELS", "vectorizers")

os.makedirs(VECTOR_DIR, exist_ok=True)

def build_vector_db(course_name: str):

    chunks_path=os.path.join(PROCESSED_DIR, f"{course_name}_chunks.json")
    if not os.path.exists(chunks_path):
        print(f"Missing chunks file for {course_name}. Run preprocess_data.py first.")
        return
    
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks=json.load(f)
    
    texts= [c["content"] for c in chunks]
    metadatas=[]
    for c in chunks:
        meta={}
        if "source" in c:
            meta["source"] = c["source"]
        elif "page" in c:
            meta["page"] = c["page"]
        else:
            meta["course"] = course_name
        metadatas.append(meta)
    # metadatas= [{"source": c["page"]} for c in chunks]

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_db=FAISS.from_texts(texts,embeddings, metadatas=metadatas)


    save_path= os.path.join(VECTOR_DIR, course_name)
    vector_db.save_local(save_path)

    print(f"Vector DB saved for {course_name} at {save_path}")


if __name__=="__main__":
    courses= ["AI","Web Development","Mathematics for Machine Learning","Python"]
    for course in courses:
        build_vector_db(course)

# class OpenRouterEmbeddings:
#     def __init__(self, model, api_key):
#         self.model = model
#         self.api_key = api_key

#     def embed_documents(self, texts):
#         return [self._embed(text) for text in texts]

#     def embed_query(self, text):
#         return self._embed(text)

#     def _embed(self, text):
#         url = "https://openrouter.ai/api/v1/embeddings"
#         headers = {"Authorization": f"Bearer {self.api_key}"}
#         data = {"model": self.model, "input": text}
#         resp = requests.post(url, headers=headers, json=data).json()
#         print("Status Code:", resp.status_code)
#         print("Raw response:", resp.text)   # 👈 this will show if it's HTML or JSON
        
#         resp.raise_for_status()  # raises error for 4xx/5xx
#         result = resp.json() 
#         return resp["data"][0]["embedding"]
