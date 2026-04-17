from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
import pandas as pd
import joblib
import os
import openai as op
from dotenv import load_dotenv
from manage_enrollment import generate_enrollment
from chatbot import course_vector_db
import csv
import pyttsx3
import speech_recognition as sr
import time
import threading
import csv
import requests

#-----------path directories------------------------------- 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
QUERIES_FILE = os.path.join("DATA", "student_queries.csv")
NOTES_DIR = os.path.join(ROOT_DIR, "DATA", "Raw")
CHAT_FILE = os.path.join(ROOT_DIR, "DATA", "chats.csv")

load_dotenv()
api_keys=os.getenv("OPEN_ROUTER_API_KEY")
print("API KEY:", api_keys)
op.api_key=api_keys 
op.api_base="https://openrouter.ai/api/v1"




def ask_openrouter(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPEN_ROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"OpenRouter Error {response.status_code}: {response.text}")

    return response.json()["choices"][0]["message"]["content"].strip()



#------------------voice section---------------------------------------------------------------
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('volume', 1.0)
engine.setProperty("rate", 120)

def speak(audio):
    try:
        engine.say(audio)
        engine.runAndWait()
        print(f"speaking: {audio}")
    except Exception as e:
        print(f"error in speak(): {e}")
def voice_command():
     r=sr.Recognizer()
     with sr.Microphone() as source:
         print("Listening....")
         try:
             r.adjust_for_ambient_noise(source,duration=1)
             audio=r.listen(source,timeout=5,phrase_time_limit=8)
             content=r.recognize_google(audio,language='en-in')
             print("You said:",content)
             return content.lower()
         except sr.UnknownValueError:
             print("Sorry,I can't understand.")
             return ""

def save_student_query(enrollment_id, course_name, query, answers):
    file_exists = os.path.isfile(QUERIES_FILE)
    write_header = (not file_exists) or (os.stat(QUERIES_FILE).st_size == 0)

    with open(QUERIES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["enrollment_id", "course_name", "query", "answers"])
        writer.writerow([enrollment_id, course_name, query, " | ".join(answers)])


app = Flask(
    __name__,
    template_folder=os.path.join(ROOT_DIR, "templates"),
    static_folder=os.path.join(ROOT_DIR, "static")
)
app.secret_key = "supersecret]]"  # needed for sessions

user_histories={}
# Load trained recommendation model

model = joblib.load(os.path.join(ROOT_DIR, "MODELS","recommendation_model.pkl"))
label_encoder = joblib.load(os.path.join(ROOT_DIR, "MODELS", "label_encoder.pkl"))
HISTORY_FILE = os.path.join(ROOT_DIR, "DATA", "student_history.csv")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        student_id = request.form["student_id"]
        english_marks = int(request.form["english_marks"])
        math_marks = int(request.form["math_marks"])  
        science_marks = int(request.form["science_marks"]) 
        computer_marks = int(request.form["computer_marks"]) 
        

        features = [[english_marks, math_marks, science_marks, computer_marks]]

        predicted_label= model.predict(features)[0]
        recommended_course=label_encoder.inverse_transform([predicted_label])[0]
        ret=render_template("recommend.html", course=recommended_course, student_id=student_id)

        if recommended_course:
            threading.Thread(
    target=speak,
    args=(f"your recommended course is {recommended_course} enroll yourself",)
).start()
        return ret
    return render_template("index.html")

@app.route("/enroll", methods=["POST"])
def enroll():
    student_name = request.form["student_name"]
    course = request.form["course"]
    
    enrollment_id, password = generate_enrollment(student_name, course)

    return render_template(
        'enroll_success.html',
        name=student_name,
        course=course,
        enrollment_id=enrollment_id,
        password=password
    )
@app.route("/login", methods=["GET", "POST"])


# @app.route("/enroll", methods=["POST"])
# def enroll():
#     student_name = request.form["student_name"]
#     course = request.form["course"]
    
#     enrollment_id, password = generate_enrollment(student_name, course)

#     # ✅ AUTO LOGIN AFTER ENROLL
#     session["enrollment_id"] = enrollment_id
#     session["student_name"] = student_name

#     # ✅ REDIRECT TO DASHBOARD (NOT TEXT)
#     return redirect(url_for("dashboard", success=1))
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        enrollment_id = request.form["enrollment_id"]
        password = request.form["password"]

        df = pd.read_csv(HISTORY_FILE)
        user = df[(df["enrollment_id"] == enrollment_id) & (df["password"] == password)]

        if not user.empty:
            session["enrollment_id"] = enrollment_id
            return redirect(url_for("dashboard"))
        else:
            return "❌ Invalid login!"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "enrollment_id" not in session:
        return redirect(url_for("login"))

    # Read history file
    df = pd.read_csv(HISTORY_FILE)

    # Get student’s enrolled courses
    student_courses = df[df["enrollment_id"] == session["enrollment_id"]]["course"].tolist()

    # Only show notes for enrolled courses that actually exist
    available_courses = [d for d in os.listdir(NOTES_DIR) if os.path.isdir(os.path.join(NOTES_DIR, d))]
    enrolled_courses = [c for c in available_courses if c in student_courses]

    return render_template("course_dashboard.html", courses=enrolled_courses)
# @app.route("/dashboard")
# def dashboard():
#     if "enrollment_id" not in session:
#         return redirect(url_for("login"))

#     df = pd.read_csv(HISTORY_FILE)

#     student_data = df[df["enrollment_id"] == session["enrollment_id"]]
#     student_courses = student_data["course"].tolist()
#     student_name = student_data["student_name"].iloc[0]

#     available_courses = [d for d in os.listdir(NOTES_DIR) if os.path.isdir(os.path.join(NOTES_DIR, d))]
#     enrolled_courses = [c for c in available_courses if c in student_courses]

#     return render_template(
#         "course_dashboard.html",
#         courses=enrolled_courses,
#         name=student_name
#     )

@app.route("/course_chat/<course_name>", methods=["GET", "POST"])
def course_chat(course_name):
    if "enrollment_id" not in session:
        return redirect(url_for("login"))

    # Load the vector DB for the course
    db = course_vector_db(course_name)

    # Initialize current chat if not exists
    if "current_chat" not in session:
        session["current_chat"] = []

    if "previous_chats" not in session:
        session["previous_chats"] = []

    current_chat = session["current_chat"]
    previous_chats = session["previous_chats"]

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if not query:
            query = voice_command()

        if not query:
            reply = "Sorry, I cannot understand. Please try again."
            current_chat.append({"role": "assistant", "content": reply})
            session.modified = True
            threading.Thread(target=speak, args=(reply,), daemon=True).start()
            return render_template(
                "course_chat.html",
                course_name=course_name,
                current_chat=current_chat,
                previous_chats=previous_chats
            )

        # Append user query
        current_chat.append({"role": "user", "content": query})

        # Retrieve relevant notes
        docs = db.similarity_search(query, k=3)
        retrieved_text = "\n".join([doc.page_content for doc in docs])

        messages = [
            {"role": "system", "content": f"You are a personal tutor for {course_name}. Use context from notes to explain clearly."},
            {"role": "user", "content": f"Question: {query}\n\nContext:\n{retrieved_text}\n\nAnswer in detail:"}
        ]

        try:
            refined_answer = ask_openrouter(messages)
        except Exception as e:
            refined_answer = f"⚠️ API Error: {str(e)}"
            print("GPT Error:", e)

        # Append assistant response
        current_chat.append({"role": "assistant", "content": refined_answer})
        session.modified = True

        # Speak response
        threading.Thread(target=speak, args=(refined_answer,), daemon=True).start()

    return render_template(
        "course_chat.html",
        course_name=course_name,
        current_chat=current_chat,
        previous_chats=previous_chats
    )

@app.route("/course_chat/new/<course_name>")
def new_chat(course_name):
    # Save old chat if not empty
    if "current_chat" in session and session["current_chat"]:
        previous_chats = session.get("previous_chats", [])
        title = f"Chat {len(previous_chats)+1} – {time.strftime('%H:%M')}"
        previous_chats.append({"title": title, "messages": session["current_chat"]})
        session["previous_chats"] = previous_chats
        session.modified = True

    # Reset current chat
    session["current_chat"] = []
    return redirect(url_for("course_chat", course_name=course_name))

@app.route("/course_chat/load/<course_name>/<int:chat_index>")
def load_chat(course_name, chat_index):
    if "previous_chats" not in session:
        return redirect(url_for("course_chat", course_name=course_name))

    previous_chats = session["previous_chats"]

    if 0 <= chat_index < len(previous_chats):
        # Load the selected old chat into current_chat
        session["current_chat"] = previous_chats[chat_index]["messages"]
        session.modified = True

    return redirect(url_for("course_chat", course_name=course_name))

# Optional route to "save" current chat to sidebar
@app.route("/course_chat/save/<course_name>")
def save_chat(course_name):
    if "current_chat" in session and session["current_chat"]:
        previous_chats = session.get("previous_chats", [])
        # Give a simple title with timestamp
        title = f"Chat {len(previous_chats)+1} – {time.strftime('%Y-%m-%d %H:%M')}"
        previous_chats.append({"title": title, "messages": session["current_chat"]})
        session["previous_chats"] = previous_chats
        session["current_chat"] = []  # Reset current chat
        session.modified = True
    print("session updated")
    return redirect(url_for("course_chat", course_name=course_name))


@app.route("/notes/<course_name>")
def notes(course_name):
    if "enrollment_id" not in session:
        return redirect(url_for("login"))

    # Verify student is enrolled in this course
    df = pd.read_csv(HISTORY_FILE)
    student_courses = df[df["enrollment_id"] == session["enrollment_id"]]["course"].tolist()

    if course_name not in student_courses:
        return "❌ You are not enrolled in this course!"

    course_notes_dir = os.path.join(NOTES_DIR, course_name)
    if not os.path.exists(course_notes_dir):
        return f"No notes found for {course_name}"

    pdfs = [f for f in os.listdir(course_notes_dir) if f.lower().endswith(".pdf")]
    return render_template("notes.html", course_name=course_name, pdfs=pdfs)

@app.route("/notes/<course_name>/<filename>")
def download_notes(course_name, filename):
    course_notes_dir = os.path.join(NOTES_DIR, course_name)
    return send_from_directory(course_notes_dir, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)





# def course_chat(course_name):
#     if "enrollment_id" not in session:
#         return redirect(url_for("login"))

#     db = course_vector_db(course_name)
#     if "chat_history" not in session:
#         session["chat_history"] = []

#     history = session["chat_history"]

#     if request.method == "POST":
#         query = request.form.get("query", "").strip()

#         if not query:
#             query=voice_command()
            
#         if not query:
#             reply= "sorry i cannot undersatnd.please try again"
#             history.append({"role": "assistant", "content": reply})
#             session.modified = True
#             threading.Thread(target=speak, args=(reply,), daemon=True).start()
#             return render_template("course_chat.html", course_name=course_name, chat_history=session["chat_history"])
    
#         docs = db.similarity_search(query, k=3)
#         retrieved_text= "\n".join([doc.page_content for doc in docs])
            
#         messages = [
#             {"role": "system", "content": f"You are a personal tutor for {course_name}. Use context from notes to explain clearly."},
#             {"role": "user", "content": f"Question: {query}\n\nContext:\n{retrieved_text}\n\nAnswer in detail:"}
#         ]
       
#         try:
#             # gpt_response = op.ChatCompletion.create(
#             #     model="openai/gpt-3.5-turbo",
#             #     messages = messages
#             # )
#             # refined_answer=gpt_response["choices"][0]["message"]["content"].strip()
#             refined_answer = ask_openrouter(messages)
#         except Exception as e:
#             refined_answer = f"⚠️ API Error: {str(e)}"
#             print("GPT Error:", e)
#         history.append({"role": "user", "content": query})
#         history.append({"role": "assistant", "content": refined_answer})
#         session["chat_history"] = history
#         session.modified = True

#         threading.Thread(target=speak, args=(refined_answer,), daemon=True).start()
#         return render_template("course_chat.html", course_name=course_name, chat_history=history)

#     return render_template("course_chat.html", course_name=course_name, chat_history=history)