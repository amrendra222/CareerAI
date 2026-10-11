# CareerAI – AI Interviewer & Career Intelligence System

CareerAI is a Generative AI-powered web application designed to help students and job seekers analyze their resumes, evaluate job descriptions, identify skill gaps, and prepare for interviews. It uses the Groq Cloud API to generate personalized career insights and recommendations.

## 🚀 Features

- **Resume Analysis:** Upload and analyze resumes in PDF format to extract relevant information and identify skills, qualifications, and experience.
- **Job Description Analysis:** Analyze job descriptions to understand required skills, qualifications, and experience.
- **Career Matching:** Compare a resume with a job description and generate a job-fit score, matched skills, missing skills, and recommendations.
- **Skill Gap Analysis:** Identify technical and professional skills that need improvement.
- **AI-Powered Insights:** Generate personalized career recommendations and learning priorities.
- **Interview Preparation:** Support AI-powered interview preparation and career development.
- **Resume Management:** Save, view, and delete uploaded resumes.
- **Web-Based Interface:** Access features through a user-friendly frontend.

## 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- FastAPI
- Uvicorn
- SQLAlchemy

### Database
- SQLite

### Generative AI
- Groq Cloud API
- `openai/gpt-oss-20b` model

### Additional Libraries
- PyPDF2
- Pydantic
- Python-dotenv
- HTTPX

## 🏗️ Project Structure

```text
CareerAI/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── prompts/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .gitignore
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js
│   └── index.html
│
└── README.md
```

*Note: The structure above illustrates the intended organization. Actual files and folders may vary depending on the current implementation.*

## ⚙️ Prerequisites

Before running CareerAI locally, install:

- Python 3.11 or a compatible Python version supported by the dependencies.
- A modern web browser.
- Visual Studio Code or another code editor.
- A Groq Cloud API key.

## 📥 Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/CareerAI.git
cd CareerAI
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Set Up the Backend

```bash
cd backend
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the `backend` directory.

Add the following configuration:

```env
APP_NAME=CareerAI
DATABASE_URL=sqlite:///./careerai.db
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key
```

Replace the placeholder values with your own credentials. Configure Clerk variables only if your current application requires them.

**Security:** Never commit your `.env` file, API keys, authentication secrets, or private database files to GitHub.

### 4. Start the Backend

From the `backend` directory, run:

```bash
uvicorn app.main:app
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Run the Frontend

Open `frontend/index.html` in your browser or serve the frontend using a local development server.

Ensure the frontend API configuration points to the running backend:

```javascript
const API_BASE = "http://127.0.0.1:8000";
```

For production deployment, update this URL to the deployed backend address and configure backend CORS appropriately.

## 🔐 Security Considerations

- Keep API keys and authentication secrets in environment variables.
- Exclude `.env`, virtual environments, and local database files from source control.
- Configure appropriate authentication and authorization before public deployment.
- Use HTTPS for production deployments.
- Protect uploaded resumes and personal information from unauthorized access.

## ☁️ Deployment

CareerAI can be deployed using separate frontend and backend hosting services.

A possible deployment arrangement is:

- **Frontend:** Netlify or a static-site hosting service.
- **Backend:** Render or another Python-compatible hosting service.
- **Database:** SQLite for local development; a persistent database is recommended for production.

Before deploying, configure production environment variables, CORS, the frontend API URL, and persistent database storage. Do not assume a temporary hosting filesystem will preserve uploaded resumes or database records.

## 🎯 Project Objectives

- Simplify resume evaluation using Generative AI.
- Help candidates understand their suitability for job opportunities.
- Identify missing skills and areas for improvement.
- Provide personalized career and interview preparation insights.
- Bring resume analysis and career matching into a single application.

## 🔮 Future Enhancements

- Advanced AI mock interviews.
- Interview feedback and performance scoring.
- Personalized learning roadmaps.
- Additional resume formats.
- Improved job recommendation capabilities.
- Persistent cloud database and secure document storage.
- Detailed career analytics and progress tracking.

## 👨‍💻 Author

**CareerAI Project**

A Generative AI application for resume analysis, career intelligence, and interview preparation.


