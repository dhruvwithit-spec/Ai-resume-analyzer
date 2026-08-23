# 🚀 AI Resume Analyzer

An intelligent, AI-powered resume analysis and ATS scoring platform built with **Python**, **Streamlit**, **spaCy**, **Sentence Transformers**, and **Plotly**.

---

## 🌟 Key Features

- 📄 **Multi-Format Resume Parsing**: Supports PDF (`.pdf`) and Word (`.docx`) file extraction with fallback text preprocessing.
- 🎯 **Skill Extraction & Matching**: Automatically identifies technical skills, programming languages, databases, cloud tools, and frameworks from a CSV dataset and maps matched vs. missing requirements.
- 🧠 **Semantic Alignment**: Utilizes `SentenceTransformer("all-MiniLM-L6-v2")` cosine similarity (with token-overlap fallback) to measure how deeply your experience matches the job description.
- 📊 **ATS Score Breakdown**: Calculates a transparent 100-point ATS score weighted across:
  - **35%** Semantic Similarity
  - **30%** Skill Coverage
  - **20%** Section Completeness
  - **15%** Keyword Match Overlap
- 📋 **Section Detection & Heuristics**: Automatically checks for Summary, Skills, Experience, Education, Projects, Certifications, and Contact Info.
- 💡 **Actionable Suggestions & Download**: Generates tailored priority suggestions and allows users to export a full Markdown summary report.

---

## 🛠️ Tech Stack

- **Frontend & Dashboard**: Streamlit, Custom Glassmorphism CSS, Plotly
- **NLP & Parsing**: spaCy, PyPDF, Python-DOCX, Sentence-Transformers
- **Data Engineering**: Pandas, Python `re`, `csv`, `collections`

---

## 💻 Local Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dhruvwithit-spec/Ai-resume-analyzer.git
   cd Ai-resume-analyzer
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

5. **Open in browser**: Navigate to `http://localhost:8501`.

---

## 📄 License & Author

Developed by **[Dhruv Rana](https://github.com/dhruvwithit-spec)** — BCA Artificial Intelligence Student & Full Stack AI Developer.
