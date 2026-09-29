# 🎓 E-Learning Platform

A full-featured E-Learning web application built with **Flask**, **SQLite**, and **Tailwind CSS / Vanilla JS**. The platform enables tutors to upload courses and students to browse, bookmark, and interact with educational content.

🚀 **Live Demo:** [https://e-learning-platform-wt7c.onrender.com/](https://e-learning-platform-wt7c.onrender.com/)

---

## ✨ Features

- **User Authentication:** Student and Tutor registration/login with secure session management.
- **Course Management:** Tutors can upload, edit, and manage video courses and playlists.
- **Interactive UI:** Responsive dashboard, course search, category filtering, and sidebar navigation.
- **Bookmarks & Likes:** Students can bookmark favorite lessons and like content.
- **Contact & Support:** Built-in contact form powered by `Flask-Mail`.

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask, Flask-SQLAlchemy, Flask-Mail)
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite
- **WSGI Server:** Gunicorn
- **Deployment:** Render (Connected via GitHub CI/CD)

---

## 📁 Project Structure

```text
Project-VTA/
├── instance/          # SQLite database (database.db)
├── static/            # Static assets (CSS, JS, images, uploaded files)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/         # HTML template files
├── app.py             # Main Flask application entry point
├── Procfile           # Render deployment configuration
└── requirements.txt   # Python dependencies
