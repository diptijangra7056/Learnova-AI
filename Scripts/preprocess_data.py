import os
import json
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "DATA", "RAW")
PROCESSED_DIR = os.path.join(BASE_DIR, "DATA", "Embedded")

os.makedirs(PROCESSED_DIR, exist_ok=True)

def load_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def preprocess_course(course_name):
    course_dir = os.path.join(RAW_DIR, course_name)
    if not os.path.exists(course_dir):
        print(f"No raw data for {course_name}")
        return
    
    all_texts = []
    for file in os.listdir(course_dir):
        if file.endswith(".pdf"):
            text = load_pdf(os.path.join(course_dir, file))
            all_texts.append({"content": text, "source": file})
    
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100
    )
    chunks = []
    for doc in all_texts:
        parts = text_splitter.split_text(doc["content"])
        for i, part in enumerate(parts):
            chunks.append({
                "content": part,
                "source": f"{doc['source']} (chunk {i})"
            })

    # Save
    save_path = os.path.join(PROCESSED_DIR, f"{course_name}_chunks.json")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Processed {course_name}: {len(chunks)} chunks saved at {save_path}")


if __name__ == "__main__":
    courses = ["AI", "Web Development", "Mathematics for Machine Learning", "Python"]
    for course in courses:
        preprocess_course(course)
