# import os
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings



# BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# VECTOR_DIR=os.path.join(BASE_DIR, "MODELS", "vectorizers")

# # courses=["AI","Mathematics for Machine Learning","Web Development","Python"]
# # for course in courses:  
# courses = ["AI", "Web Development", "Mathematics for Machine Learning", "Python"]
# vector_dbs = {c: load_vector_db(c) for c in courses}
# # def load_vector_db(course_name: str):
# #     embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# #     db_path=os.path.join(VECTOR_DIR, course_name)
# #     return FAISS.load_local(db_path,embeddings,allow_dangerous_deserialization=True)
    

# def course_vector_db(course_name: str):
#      embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#      db_path=os.path.join(VECTOR_DIR, course_name)
#      return FAISS.load_local(db_path,embeddings,allow_dangerous_deserialization=True)
    
     
# def chat(course_name: str):
#     db = load_vector_db(course_name)
#     print(f"Chatbot ready for {course_name} 🚀")

#     while True:
#             query = input("You: ")
#             if query.lower() in ["exit", "quit", "bye"]:
#                 break
#             docs = db.similarity_search(query, k=3)
#             print("\n--- Answer ---")
#             print("--------------\n")    
#             for i, doc in enumerate(docs, 1):
#                 print(f"{i}. {doc.page_content[:300]}... (source: {doc.metadata})")


# if __name__=="__main__":
#      chat ("Mathematics for Machine Learning")


import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

HISTORY_FILE="DATA/student_history.csv"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DIR = os.path.join(BASE_DIR, "MODELS", "vectorizers")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def course_vector_db(course_name: str):
    db_path = os.path.join(VECTOR_DIR, course_name)
    return FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
