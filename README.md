
# 🚀 Infinity: Instant Peer Review and Micro-Collaboration Platform

## 💡 Project Overview

**Infinity** is a full-stack web platform designed to enable **instant peer reviews and micro-collaboration** among students working on academic or personal projects. Students can showcase their work at various stages (idea, prototype, final), receive meaningful feedback, track growth, and co-work on project tasks.

Built by the *Team Infinity*, this platform aims to **bridge the feedback gap** in student project development, enhance learning, and promote community-driven collaboration.

---

## ✨ Key Features

- ✅ Upload and manage projects in **stage-wise format**
- 💬 **Threaded peer reviews** with structured comments
- 🤝 **Micro-Collaboration invites** for task-specific co-working
- 🧠 **AI-generated feedback summaries** using Google Gemini API
- 📊 Skill tagging and growth analytics
- 🔔 Like/comment/notification system
- 📨 Real-time in-app messaging between collaborators


---

## 🔧 Tech Stack

| Layer       | Technology                     |
|------------|--------------------------------|
| Frontend   | HTML, CSS, JavaScript          |
| Backend    | Python Flask                   |
| Database   | MongoDB                        |
| AI         | Google Gemini API (used for feedback summary) |
| Messaging  | Threaded in-app messaging      |


---

## 🧠 AI & Gemini Integration

- The platform uses **Google Gemini API** to generate concise summaries of peer feedback for each project.
- You need to **manually insert your API key** in the backend route `/summarize_feedback`.

---

## 🗄️ MongoDB Configuration

- MongoDB is used for storing users, projects, comments, likes, notifications, microcollab data, and messages.
- Ensure MongoDB is running locally on the default port (`mongodb://localhost:27017/`)
- The main database used: `infinityDB`
- Collections include:
  - `users`
  - `projects`
  - `comments`
  - `notifications`
  - `likes`
  - `microcollabs`
  - `messages`

---

## 🔑 Authentication

- Basic session-based login system using Flask.
- Signup, login, and logout features included.
- Role-based UI separation for:
  - Project Owner
  - Collaborator
  - Reviewer

---

## 📁 Project Modules

### 1. Project Dashboard
- Add/Edit/Delete your projects
- Tag skills & add external links
- View likes, comments, and suggestions

### 2. Review Center
- See who reviewed your work
- Summarize suggestions using Gemini AI
- Like or reply to comments

### 3. MicroCollab Board
- View invites and accept/decline tasks
- Message thread per collab
- Organize by:
  - Discover (public collabs)
  - My Collabs (your tasks)
  - Accepted (joined by you)

---

## 🧪 How to Run Locally

1. Clone the repository

2. Install dependencies:

3. Make sure MongoDB is running on `localhost:27017`

4. Start the Flask server:

   ```bash
   python app.py
   ```

5. Visit the app on:

   ```
   http://127.0.0.1:5000/
   ```

---

## ❗ Notes

* **Gemini API Key** is used in `/summarize_feedback` route (backend).
* For public GitHub usage, **I do not include the API key**.

---

## 👥 Team Infinity

* **Shiva Nandhini R** 
* Bhathma Priyaa V
* Suja Bala J

---


