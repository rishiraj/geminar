# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import uuid
import requests
from io import BytesIO
from collections import defaultdict
import threading
import time
import random

# Gemini code (assuming it's in gemini_integration.py)
from google import genai
from google.genai import types
import base64

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a strong random key

classrooms = {}  # Dictionary to store classroom data (in-memory)

# Word lists for generating readable classroom names
adjectives = ["Gentle", "Calm", "Sunny", "Quiet", "Happy", "Brave", "Wise", "Kind", "Cool", "Bright"]
nouns = ["Stream", "Brook", "Field", "Garden", "Valley", "Haven", "Grove", "Meadow", "Harbor", "Cove"]

def generate_classroom_name():
    adj = random.choice(adjectives)
    noun = random.choice(nouns)
    return f"{adj} {noun}"


def generate_gemini_answer(pdf_url, question):
    try:
        client = genai.Client(
            vertexai=True,
            project="open-genai",
            location="us-central1",
        )

        document1 = types.Part.from_uri(
            file_uri=pdf_url,
            mime_type="application/pdf",
        )

        model = "gemini-2.0-flash-exp"
        contents = [
            types.Content(
            role="user",
            parts=[
                document1,
                types.Part.from_text(text=question)
            ]
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            temperature = 1,
            top_p = 0.95,
            max_output_tokens = 8192,
            response_modalities = ["TEXT"],
            safety_settings = [types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
            ),types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
            )],
            system_instruction=[types.Part.from_text(text="""Answer the question based on the provided document. Be concise and helpful.""")],
        )
        
        response = client.models.generate_content(model = model, contents = contents, config = generate_content_config)
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Sorry, I couldn't answer that question right now. Please try again later or ask your teacher."


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        pdf_url = request.form.get("pdf_url")
        if pdf_url:
            classroom_name = generate_classroom_name()
            classroom_id = classroom_name.replace(" ", "").lower() # Readable classroom name
            classrooms[classroom_id] = {
                "pdf_url": pdf_url,
                "name": classroom_name, # Store readable name
                "students": {},
                "questions": [],
                "understanding": defaultdict(int),
                "gemini_answers": {}
            }
            return redirect(url_for("teacher_classroom", classroom_id=classroom_id))
    return render_template("index.html")

@app.route("/classroom/<classroom_id>", methods=["GET", "POST"])
def classroom(classroom_id):
    if classroom_id not in classrooms:
        return "Classroom not found."

    if request.method == "POST":
        student_name = request.form.get("student_name")
        if student_name:
            session['student_name'] = student_name
            session['classroom_id'] = classroom_id
            if student_name not in classrooms[classroom_id]["students"]:
                classrooms[classroom_id]["students"][student_name] = {"understanding": "neutral"} # Initialize understanding level
            return redirect(url_for("student_view", classroom_id=classroom_id))

    return render_template("classroom_join.html", classroom_id=classroom_id, classroom_name=classrooms[classroom_id]["name"])


@app.route("/teacher/<classroom_id>")
def teacher_classroom(classroom_id):
    if classroom_id not in classrooms:
        return "Classroom not found."
    classroom_name = classrooms[classroom_id]["name"]
    classroom_url = url_for('classroom', classroom_id=classroom_id, _external=True) # Generate shareable link
    return render_template("teacher_view.html", classroom_id=classroom_id, classroom_name=classroom_name, classroom_url=classroom_url)


@app.route("/student/<classroom_id>")
def student_view(classroom_id):
    if classroom_id not in classrooms:
        return "Classroom not found."
    if 'student_name' not in session or session['classroom_id'] != classroom_id:
        return redirect(url_for("classroom", classroom_id=classroom_id))

    student_name = session['student_name']
    classroom_name = classrooms[classroom_id]["name"]
    return render_template("student_view.html", classroom_id=classroom_id, student_name=student_name, classroom_name=classroom_name)


@app.route("/update_understanding/<classroom_id>", methods=["POST"])
def update_understanding(classroom_id):
    if classroom_id not in classrooms:
        return jsonify({"status": "error", "message": "Classroom not found."})
    if 'student_name' not in session or session['classroom_id'] != classroom_id:
        return jsonify({"status": "error", "message": "Student not logged in."})

    understanding_level = request.form.get("understanding")
    student_name = session['student_name']

    if understanding_level in ["green", "yellow", "red", "neutral"]:
        classrooms[classroom_id]["students"][student_name]["understanding"] = understanding_level
        classrooms[classroom_id]["understanding"] = defaultdict(int) # Recalculate counts
        for student_data in classrooms[classroom_id]["students"].values():
            understanding = student_data["understanding"]
            if understanding in ["green", "yellow", "red"]:
                classrooms[classroom_id]["understanding"][understanding] += 1

        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Invalid understanding level."})


@app.route("/ask_question/<classroom_id>", methods=["POST"])
def ask_question(classroom_id):
    if classroom_id not in classrooms:
        return jsonify({"status": "error", "message": "Classroom not found."})
    if 'student_name' not in session or session['classroom_id'] != classroom_id:
        return jsonify({"status": "error", "message": "Student not logged in."})

    question_text = request.form.get("question")
    student_name = session['student_name']

    if question_text:
        question_id = str(uuid.uuid4())
        classrooms[classroom_id]["questions"].append({
            "id": question_id,
            "student": student_name,
            "text": question_text,
            "gemini_answer": None,
            "answer_satisfactory": None
        })
        return jsonify({"status": "success", "question_id": question_id})
    else:
        return jsonify({"status": "error", "message": "Question text cannot be empty."})


@app.route("/get_gemini_answer/<classroom_id>/<question_id>", methods=["GET"])
def get_gemini_answer_route(classroom_id, question_id):
    if classroom_id not in classrooms:
        return jsonify({"status": "error", "message": "Classroom not found."})

    question_data = next((q for q in classrooms[classroom_id]["questions"] if q["id"] == question_id), None)
    if not question_data:
        return jsonify({"status": "error", "message": "Question not found."})

    if question_data["gemini_answer"] is None:
        pdf_url = classrooms[classroom_id]["pdf_url"]
        question_text = question_data["text"]
        gemini_answer = generate_gemini_answer(pdf_url, question_text)
        question_data["gemini_answer"] = gemini_answer
        classrooms[classroom_id]["gemini_answers"][question_id] = gemini_answer # Store for faster access

    return jsonify({"status": "success", "answer": question_data["gemini_answer"]})


@app.route("/rate_answer/<classroom_id>/<question_id>", methods=["POST"])
def rate_answer(classroom_id, question_id):
    if classroom_id not in classrooms:
        return jsonify({"status": "error", "message": "Classroom not found."})
    if 'student_name' not in session or session['classroom_id'] != classroom_id:
        return jsonify({"status": "error", "message": "Student not logged in."})

    rating = request.form.get("rating") # "satisfactory" or "unsatisfactory"

    question_data = next((q for q in classrooms[classroom_id]["questions"] if q["id"] == question_id), None)
    if not question_data:
        return jsonify({"status": "error", "message": "Question not found."})

    if rating in ["satisfactory", "unsatisfactory"]:
        question_data["answer_satisfactory"] = rating
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Invalid rating."})


@app.route("/get_classroom_data/<classroom_id>")
def get_classroom_data(classroom_id):
    if classroom_id not in classrooms:
        return jsonify({"status": "error", "message": "Classroom not found."})

    understanding_counts = classrooms[classroom_id]["understanding"]
    questions_data = classrooms[classroom_id]["questions"]
    return jsonify({
        "status": "success",
        "understanding": understanding_counts,
        "questions": questions_data
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001) # Run on port 5001