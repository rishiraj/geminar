# Geminar: Interactive Seminars with Real-time Feedback and Gemini based Q&A

[![Project Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)](https://github.com/rishiraj/geminar)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Project Idea

Digital classroom tool inspired by Dylan Wiliam's colored cups concept, enhanced for online and in-person lectures. Features real-time student understanding visualization, question asking, and AI-powered answers using Google Gemini, aimed at improving student engagement and addressing learning needs promptly.

## Features

*   **Easy Classroom Creation:** Teachers create classrooms with a lecture PDF URL, getting a shareable link.
*   **Simple Student Joining:** Students join classrooms by entering their name.
*   **Real-time Understanding Feedback:** Students use buttons (Green, Yellow, Red, Neutral) to indicate comprehension. Teacher and students see a live pie chart of class understanding.
*   **Real-time Questions & AI Answers:** Students ask questions visible to all. Gemini AI provides instant answers based on the lecture PDF.
*   **Student Feedback on AI:** Students rate AI answers as Satisfactory (✅) or Pass to Teacher (❌).
*   **Teacher Moderation:** Mark questions as solved, remove disruptive students (and their questions), view student list and feedback.
*   **Responsive & Beautiful Design:** Pastel colors, rounded edges, animations, mobile-friendly.

## Instructions

### 1. Setup and Installation

**Prerequisites:**

*   **Python 3.7+ and pip**
*   **Google Gemini API Access** (Vertex AI project setup required)

**Installation Steps:**

1.  **Clone the repository (or download the files):**
    ```bash
    git clone https://github.com/rishiraj/geminar
    cd geminar
    ```

### 2. Running the Application

1.  **Navigate to project directory and run:**
    ```bash
    python app.py
    ```

2.  **Access in browser:** Go to `http://127.0.0.1:5001/` or `http://localhost:5001/`.

### 3. Teacher Usage

1.  **Create Classroom:** Go to homepage, enter PDF URL, click "Create Classroom".
2.  **Teacher View:** Bookmark/keep open the Teacher View page. Share the classroom link with students.
3.  **Monitor:** Use the Teacher View to see understanding chart, student questions, AI answers, student feedback, mark questions solved, remove students.

### 4. Student Usage

1.  **Join Classroom:** Use the classroom link from the teacher, enter name, click "Join Classroom".
2.  **Student View:** Use buttons to give understanding feedback (Green, Yellow, Red, Neutral). Ask questions, get AI answers ("Get AI Answer"), rate AI answers (✅ Satisfactory / ❌ Pass to Teacher).

### 5. Accessing from Different Networks (Public IP)

1.  **Run Flask on `0.0.0.0`:** In `app.py`, use `app.run(debug=True, port=5001, host='0.0.0.0')`.
2.  **Find Public IP:** Use a website like `whatismyip.com`.
3.  **Router Port Forwarding:** Forward external port `5001` (TCP) to your computer's local IP and port `5001`.
4.  **Share Public IP URL:** Give students `http://<Your Public IP Address>:5001/classroom/<classroom_id>`.

**Security Note:** Flask development server is not for production. Public IP access has security considerations.

### 6. Technologies

*   Python, Flask, Google Gemini API, HTML, CSS, JavaScript, Chart.js

### 7. License

Licensed under [Apache-2.0 License](https://opensource.org/licenses/Apache-2.0).

---

**Enjoy teaching with interactive feedback and AI assistance!**
