# BuddyUp AI - Student Community Matching PoC

### *Find your community. Build your network.*

BuddyUp AI is a Proof-of-Concept (PoC) web application developed as part of an Entrepreneurship curriculum. It demonstrates how Large Language Models (LLMs) and intelligent retrieval mechanisms can help university students integrate into new cities, combat isolation, and discover local communities.

---

## 📌 Problem Statement

Every year, millions of students move to new cities or countries for university. Many arrive knowing no one and experience a period of social isolation. They face key challenges:
- **Fragmentation**: Relevant groups, clubs, and events are scattered across WhatsApp, Discord, Facebook groups, Meetup, and university websites.
- **High Entry Barrier**: Reaching out to active circles can feel intimidating for newcomers, particularly international or first-semester students.
- **Unstructured Search**: Students often do not know which clubs fit their specific goals (e.g., meeting close friends vs. professional networking).

---

## 💡 The Solution: BuddyUp AI

BuddyUp AI simplifies community discovery by offering:
1. **Unified Preferences**: A clean profile builder capturing the student's city, academic status, goals, preferred group size, and personal interests.
2. **Deterministic Matching Engine**: Scores local student communities (`communities.json`) using overlap between student preferences and community properties.
3. **AI-Powered Explanations**: Custom matching justifications telling the student *why* a group fits them.
4. **Instant Icebreakers**: Custom copy-pasteable messages to make starting the conversation effortless.

---

## 🛠️ Architecture & AI Workflow

BuddyUp AI utilizes a lightweight **Retrieval-Augmented Generation (RAG)** concept:

```
[Student Profile Form] 
       │
       ▼
[matcher.py (Scoring Engine)] ───> Filters ───> [communities.json (Database)]
       │
       ▼ (Top 3 Communities)
[llm.py (Gemini API or Mock AI)]
       │
       ▼ (Generates Contextual Explanations & Icebreakers)
[Streamlit UI Display]
```

1. **Information Retrieval (IR)**: A heuristic scoring algorithm evaluates the student profile against the local database (`communities.json`) and sorts by relevance.
2. **Context Synthesis**: The top 3 matching communities and the student profile are fed into the LLM system.
3. **Structured Generation**: The LLM analyzes the data and produces personalized feedback and icebreakers. If the API key is missing or fails, a rule-based generative template engine (**Mock AI Mode**) takes over automatically to ensure instant demonstration capability.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Pip (Python Package Installer)
- *(Optional)* Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

---

### Running Locally

1. **Clone or Navigate to the Directory**:
   ```bash
   cd buddyup
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit App**:
   ```bash
   streamlit run app.py
   ```
   Open your browser to `http://localhost:8501`.

---

### Running with Docker 🐳

You can containerize and run BuddyUp AI in seconds using Docker:

1. **Build the Docker Image**:
   ```bash
   docker build -t buddyup-ai .
   ```

2. **Run the Docker Container**:
   ```bash
   docker run -p 8501:8501 buddyup-ai
   ```
   Access the application in your browser at `http://localhost:8501`.

---

## 🔮 Future Work

For a full-scale product implementation, the next steps include:
- **Vector Database**: Storing and searching communities using dense embeddings (e.g., ChromaDB, Pinecone) instead of key-value matches.
- **Dynamic Scrapers**: Automating the ingestion of university club listings, Discord links, and local meetup channels.
- **Student Verification**: Secure sign-in restricted to university email domains (`.edu`, `.ac.uk`, etc.).
- **Inter-Student Matching**: Expanding matching to connect students with each other directly for coffee chats or project collaboration, in addition to matching them with communities.

---

*Disclaimer: This is a university project Proof-of-Concept. It is not intended for commercial production use in its current form.*
