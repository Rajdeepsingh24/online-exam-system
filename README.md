# 🧑‍💻 Web-Based Online Examination Management System

## 📌 Introduction

The Web-Based Online Examination Management System is designed to automate the traditional examination process. It provides a digital platform where administrators can manage exams and students can attempt exams online.

This system eliminates manual work, reduces errors in evaluation, and ensures efficient handling of exam-related data.

---

## 🎯 Objectives

* To provide a platform for conducting online exams
* To automate result calculation
* To manage student and exam data efficiently
* To reduce manual errors in evaluation
* To provide quick and accurate results

---

## 🚀 Features

### 👨‍🏫 Admin / Teacher Module

* Create and manage exams
* Add, update, and delete questions
* Set exam duration and marks
* View student attempts
* Monitor and manage results

### 👨‍🎓 Student Module

* Register and login securely
* View available exams
* Attempt exams within time limit
* Submit answers
* View results instantly

---

## 🛠️ Technologies Used

* **Frontend:** HTML, CSS
* **Backend:** Python (Django Framework)
* **Database:** SQLite / MySQL
* **Tools:** VS Code, GitHub

---

## 📂 Project Structure

```bash
EXAM-SYSTEM/
│
├── backend/
│   ├── exam_project/     # Django project settings
│   ├── exams/            # Exam management app
│   ├── users/            # User management app
│   ├── templates/        # HTML templates
│   ├── static/           # CSS files
│   ├── manage.py
│
├── README.md
├── .gitignore
├── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/Rajdeepsingh24/online-exam-system.git
cd online-exam-system/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Run Server

```bash
python manage.py runserver
```

### 6. Open in Browser

```
http://127.0.0.1:8000/
```

---

## 📸 Project Output

After running the project, the system provides:

* Login Page
* Student Dashboard
* Admin Dashboard
* Exam Interface
* Result Display

👉 (Add screenshots here to improve presentation)

---

## 🔐 Limitations

* Supports mainly objective-type questions
* No advanced cheating detection system
* Basic UI design
* Limited scalability for large users

---

## 🔮 Future Enhancements

* AI-based online proctoring
* Mobile responsive design
* Advanced analytics and reports
* Email notifications for exams and results
* Multi-user scalability

---

## 🧠 Learning Outcomes

* Understanding of Django framework
* Database integration using MySQL/SQLite
* Web application development
* CRUD operations implementation
* GitHub project management

---

## 👤 Author

**Rajdeep Singh**
BCA Final Year Project

---

## 📌 GitHub Repository

👉 https://github.com/Rajdeepsingh24/online-exam-system
