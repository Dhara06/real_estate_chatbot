#  Real Estate Analysis Chatbot

**Author:** Dhara Rajpurohit
**Project Type:** Full-Stack Web Application (React + Django)

---

##  Project Description

The **Real Estate Analysis Chatbot** is a smart web application that allows users to ask questions about real estate trends, property prices, and demand across different locations. It processes user queries using a Django backend and visualizes results using interactive charts and tables in a React frontend.

This system helps users make **data-driven property decisions** by providing meaningful insights such as:

* Area-wise property trends
* Price growth analysis
* Demand comparison

---

##  Features

*  Interactive chatbot-style interface
*  Real-time data analysis
*  Line and Bar chart visualizations
*  Area-wise comparison
*  Clean and responsive UI
*  REST API-based backend

---

##  Tech Stack

### Frontend:

* React.js
* Tailwind CSS
* Recharts
* Lucide React Icons

### Backend:

* Django
* Django REST Framework
* Python

### Deployment:

* Frontend: Vercel
* Backend: Render

---

##  Project Setup

###  Backend Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

###  Frontend Setup

```bash
npm install
npm start
```

---

##  API Endpoint Example

```http
POST /api/analyze/
```

**Request Body:**

```json
{
  "query": "Analyze Wakad"
}
```

---

##  Output

* Summary analysis in text format
* Chart-based visualization (Line / Bar)
* Tabular representation of detailed data

---

##  Developed By

**Dhara Rajpurohit**
B.Tech Student | Software Engineering
Passionate about AI, Web Development & Data-Driven Applications

---

##  License

This project is created for educational and academic purposes.

---

✅ If you like this project, feel free to fork, star ⭐ and use it for learning!
