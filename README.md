# EduGenie – AI-Powered Learning Assistant

EduGenie is a production-quality, intelligent educational web application designed for students, educators, and lifelong self-learners. Powered by FastAPI and Google Gemini, EduGenie transforms complex academic material into clear, accessible, and interactive learning experiences.

---

## 🌟 Key Features

1. **💡 Concept Explanations (`POST /explain`)**
   - Demystifies intricate concepts in mathematics, computer science, science, and humanities.
   - Provides beginner-friendly definitions, intuitive mental models / analogies, step-by-step breakdowns, concrete examples, key formulas/takeaways, and real-world applications.

2. **❓ Academic Ask AI / Q&A (`POST /qa`)**
   - Direct, high-precision answers to academic questions.
   - Explains underlying reasoning without unnecessary fluff or fabrication.
   - Clarifies ambiguities and maintains student-friendly language.

3. **📝 Interactive Quiz Generator (`POST /quiz`)**
   - Generates exactly 3 rigorous multiple-choice questions from any topic or pasted textbook passage.
   - Each question features 4 distinct options, verified correct answers, and educational explanations.
   - Includes an interactive in-browser quiz engine with immediate visual feedback, answer reveal, and score tracking.

4. **📚 Quick-Revision Summarizer (`POST /summarize`)**
   - Condenses lengthy textbook chapters, research articles, or lecture notes.
   - Preserves core facts and eliminates repetition without introducing outside hallucinations.
   - Displays real-time statistics (original words, summary words, reading time saved) and high-yield bulleted takeaways.

5. **🧭 Personalized Learning Paths (`POST /learn/recommendations`)**
   - Builds complete, structured roadmaps organized across three stages: Beginner, Intermediate, and Advanced.
   - Adapts to the learner's starting proficiency.
   - Delivers recommended study sequences, estimated completion timelines, milestone projects, practice routines, and verified media resources (books, videos, documentation).

---

## 🏗️ System Architecture

```
                                  ┌──────────────────────────────┐
                                  │      Browser Client (UI)     │
                                  │   (HTML5 / CSS3 / Vanilla JS)│
                                  └──────────────┬───────────────┘
                                                 │
                                                 │ Fetch API (JSON)
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │       FastAPI Backend        │
                                  │     (Uvicorn ASGI Server)    │
                                  └──────────────┬───────────────┘
                                                 │
     ┌───────────────────┬───────────────────────┼───────────────────────┬───────────────────┐
     ▼                   ▼                       ▼                       ▼                   ▼
┌──────────┐   ┌──────────────────┐   ┌────────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│  qna.py  │   │explanation_module│   │   quiz_module.py   │   │ summary_module.py │   │ learning_path.py  │
│ (/qa)    │   │ (/explain)       │   │ (/quiz)            │   │ (/summarize)      │   │ (/learn/...)      │
└────┬─────┘   └─────────┬────────┘   └─────────┬──────────┘   └─────────┬─────────┘   └─────────┬─────────┘
     │                   │                       │                       │                       │
     └───────────────────┴───────────────────────┼───────────────────────┴───────────────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │      gemini_service.py       │
                                  │  (google-generativeai SDK)   │
                                  └──────────────┬───────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │      Google Gemini API       │
                                  │     (models/gemini-3.8-flash)│
                                  └──────────────────────────────┘
```

---

## 💻 Tech Stack

- **Backend:**
  - Python 3.10+
  - FastAPI (REST API framework)
  - Uvicorn (High-performance ASGI server)
  - Pydantic v2 (Input & output data validation)
  - Google Gemini API (`google-generativeai` SDK)
  - python-dotenv (Environment configuration)
  - Jinja2 (HTML template rendering)

- **Frontend:**
  - Semantic HTML5 & Modern CSS3
  - Modern Glassmorphism & Micro-animations
  - Vanilla JavaScript (Async/Await Fetch API, stateful quiz engine)
  - Google Fonts (Outfit, Plus Jakarta Sans, JetBrains Mono)
  - FontAwesome 6 icons

---

## 📁 Project Folder Structure

```
EduGenie/
├── main.py                   # FastAPI server entry point, middleware & routing
├── gemini_service.py         # Reusable Gemini AI helper service with error handling
├── qna.py                    # Academic Q&A endpoint (/qa)
├── explanation_module.py     # Concept simplification endpoint (/explain)
├── quiz_module.py            # 3-question MCQ generator endpoint (/quiz)
├── summary_module.py         # Text summarization endpoint (/summarize)
├── learning_path.py          # Personalized roadmap endpoint (/learn/recommendations)
├── requirements.txt          # Production Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Local environment configuration (git ignored)
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation & run guide
│
├── templates/
│   └── index.html            # Jinja2 master dashboard template
│
└── static/
    ├── style.css             # Responsive design system & glassmorphism theme
    └── script.js             # Client-side controller & interactive quiz engine
```

---

## 🚀 Installation & Local Execution

### 1. Clone or Open Workspace
Ensure you have Python 3.10 or higher installed:
```bash
python --version
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (or copy `.env.example`):
```bash
cp .env.example .env
```
Open `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=models/gemini-3.8-flash
PORT=8000
HOST=127.0.0.1
```

### 5. Launch the Application
Start the Uvicorn development server:
```bash
uvicorn main:app --reload
```

### 6. Access EduGenie
Open your web browser and navigate to:
```
http://127.0.0.1:8000
```
Interactive Swagger API documentation is available at:
```
http://127.0.0.1:8000/docs
```

---

## 📡 API Endpoints Documentation

### 1. Health & Status
- **`GET /`**: Renders the student dashboard UI.
- **`GET /api/status`**: Returns backend and AI configuration status.

---

### 2. Ask AI (`POST /qa`)
Answers academic and educational inquiries directly with explanations.

- **Request Body:**
  ```json
  {
    "question": "Which is the largest ocean?"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "question": "Which is the largest ocean?",
    "answer": "The Pacific Ocean is the largest and deepest ocean on Earth. It covers more than 63 million square miles (165 million square kilometers), which is more than 30% of the Earth's surface—larger than all the landmasses on Earth combined."
  }
  ```

---

### 3. Explain Concept (`POST /explain`)
Breaks down concepts using analogies, step-by-step logic, and real-world examples.

- **Request Body:**
  ```json
  {
    "concept": "Pythagoras Theorem",
    "level": "beginner"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "concept": "Pythagoras Theorem",
    "simple_definition": "A mathematical relationship in a right-angled triangle stating that the square of the longest side equals the sum of the squares of the other two sides.",
    "intuitive_explanation": "Imagine walking along two sides of a rectangular field versus taking the diagonal shortcut across the middle.",
    "step_by_step": [
      "Identify the right angle (90 degrees).",
      "Label the side opposite to the right angle as the hypotenuse (c).",
      "Square side a and side b: a² + b².",
      "Take the square root of the sum to find c."
    ],
    "simple_example": "For a triangle with legs 3 and 4: 3² + 4² = 9 + 16 = 25. The square root of 25 is 5.",
    "key_points": [
      "Formula: a² + b² = c²",
      "Only applies to right-angled triangles"
    ],
    "real_world_example": "Used by architects to construct square walls and in GPS systems to calculate direct distances."
  }
  ```

---

### 4. Generate Quiz (`POST /quiz`)
Generates exactly 3 multiple-choice questions with 4 options and verified answers.

- **Request Body:**
  ```json
  {
    "topic_or_passage": "Photosynthesis"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "topic_or_passage": "Photosynthesis",
    "questions": [
      {
        "question": "What is the primary byproduct of photosynthesis released into the atmosphere?",
        "options": [
          "Oxygen",
          "Carbon dioxide",
          "Nitrogen",
          "Methane"
        ],
        "correct_answer": "Oxygen",
        "explanation": "Plants split water molecules during the light reactions, releasing oxygen gas as a byproduct."
      }
    ]
  }
  ```

---

### 5. Summarizer (`POST /summarize`)
Produces concise summary paragraphs and high-yield key bullet points.

- **Request Body:**
  ```json
  {
    "text": "The Solar System is the gravitationally bound system of the Sun and the objects that orbit it. It formed 4.6 billion years ago from the gravitational collapse of a giant interstellar molecular cloud..."
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "summary": "Formed 4.6 billion years ago from a collapsed molecular cloud, the Solar System comprises the Sun and orbiting celestial bodies, with the Sun accounting for most mass...",
    "key_points": [
      "Formed 4.6 billion years ago via gravitational collapse.",
      "Contains four terrestrial inner planets and four giant outer planets.",
      "The Sun holds the vast majority of total mass."
    ],
    "original_word_count": 136,
    "summary_word_count": 48,
    "compression_ratio_pct": 65
  }
  ```

---

### 6. Personalized Learning Path (`POST /learn/recommendations`)
Creates structured syllabi across Beginner, Intermediate, and Advanced stages.

- **Request Body:**
  ```json
  {
    "topic": "SQL",
    "current_level": "Beginner"
  }
  ```
- **Response (`200 OK`):**
  ```json
  {
    "topic": "SQL",
    "current_level": "Beginner",
    "overview": "Mastering SQL enables you to query, manipulate, and analyze relational databases powering modern applications.",
    "estimated_timeline": "8-10 weeks (5-7 hours/week)",
    "recommended_order": [
      "Phase 1: Basic Queries & Filtering",
      "Phase 2: Joins, Aggregations & Grouping",
      "Phase 3: Window Functions & Indexing"
    ],
    "beginner": {
      "stage_title": "Foundations & Querying Basics",
      "focus_summary": "Understanding relational tables and standard SELECT statements.",
      "what_to_learn": ["SELECT, FROM, WHERE clauses", "ORDER BY and LIMIT", "Filtering with LIKE, IN, BETWEEN"],
      "suggested_resources": ["PostgreSQL Tutorial", "Mode Analytics SQL School"]
    },
    "intermediate": { ... },
    "advanced": { ... },
    "practice_suggestions": ["Solve 2 SQL problems daily on LeetCode/StrataScratch"],
    "projects_exercises": ["Design a schema for an online bookstore and write analytical queries"],
    "recommended_media": ["Book: SQL for Data Analysis by Cathy Tanimura", "Interactive: SQLBolt"]
  }
  ```

---

## 🔒 Security & Best Practices

- **Server-Side API Key:** The Gemini API key is loaded only on the backend through `.env` and is never exposed in client scripts or HTML.
- **Input Sanitization & Validation:** All user inputs are strictly validated for length, whitespace, and schema constraints using Pydantic models. Output text is sanitized against HTML injection.
- **Fault-Tolerant Parsing:** Model outputs are stripped of markdown code blocks (` ```json `), verified, and protected by regex fallbacks.
- **Graceful Error Handling:** If the AI service is unreachable or rate-limited, user-friendly messages are returned rather than crashing or exposing internal stack traces.

---

## 🔧 Troubleshooting

| Issue | Cause | Resolution |
|---|---|---|
| `API Key Missing` on UI | `GEMINI_API_KEY` is not defined in `.env` | Ensure `.env` exists in the root folder with a valid key. |
| `429 Rate Limit Exceeded` | Gemini API quota exhausted | Wait 60 seconds before making additional requests. |
| `Static files not loading` | Running uvicorn from the wrong directory | Execute `uvicorn main:app --reload` directly from the project root. |
| `JSON Decode Error` | Gemini returned malformatted output | EduGenie automatically uses regex fallback; retry the prompt if needed. |

---

## 📄 License
This project is open-source and intended for educational and academic purposes.
