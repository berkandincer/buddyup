# BuddyUp AI - Student Community Matching PoC

### *Find your people. Build your community.*

BuddyUp AI is an AI-powered student matching platform developed as a Proof-of-Concept (PoC) for an Entrepreneurship curriculum. It demonstrates how Large Language Models (LLMs) and intelligent local databases can help university students integrate into new cities, reduce loneliness, and establish study or social circles.

The design and features of this MVP are directly shaped by student user interviews and a structured **Value Proposition Canvas (VPC)**.

---

## 📌 Problem Statement & Interview Insights

Every year, millions of students move to new cities or countries for university. Many arrive knowing no one and experience a period of social isolation. Through our user interviews, we discovered:
- 📸 **Social Channels**: Students mostly coordinate social events via Instagram and WhatsApp.
- 🗺️ **Fragmentation**: Finding events is highly fragmented across many platforms.
- 😔 **First-Month Loneliness**: Many students feel lonely during their first few months in a new city.
- 🛹 **Shared Hobbies**: Having shared hobbies makes meeting people much easier.
- 🛡️ **Profile Trust**: Students highly value verified profiles to increase trust.
- ⚡ **Spontaneity**: Students actively seek spontaneous, low-pressure activities.

---

## 💡 The Solution: BuddyUp AI

BuddyUp AI addresses these findings by offering:
1. **Rich Preference Profiling**: Captures not just interests and goals, but also the student's **Current Situation** (e.g. looking for study partners vs. new in the city), **Preferred Activity Style** (e.g. coffee, sports, gaming), and **Personality Type** (Introverted, Balanced, Extroverted).
2. **Deterministic Matching Engine**: Evaluates a local database of 25 student communities (`communities.json`) using overlap between student preferences, personality styles, and community size parameters.
3. **Structured AI Recommendations**: Instead of generic listings, BuddyUp generates a structured 3-card roadmap:
   - 🥇 **Best Community**: The top student association or club fit.
   - ⚡ **Best Activity**: A concrete, action-oriented event tailored to the preferred activity style.
   - 👥 **Best Type of People to Meet**: A descriptor of the ideal peer profile compatibility.
4. **Verified Community Badge**: Displays a trust shield (🛡️) simulating verification, addressing the safety and trust needs uncovered in interviews.

---

## 🛠️ Architecture & AI Workflow

BuddyUp AI utilizes a lightweight **Retrieval-Augmented Generation (RAG)** concept:

```
[Student Profile Form] 
       │ (Situation, Activity, Personality)
       ▼
[matcher.py (Scoring Engine)] ───> Filters ───> [communities.json (25 Database)]
       │
       ▼ (Sorted matching results)
[llm.py (Gemini API or Mock AI)]
       │
       ▼ (Generates: Best Community, Best Activity, Best Peer Profile)
[Streamlit UI Display]
```

1. **Information Retrieval (IR)**: A heuristic scoring algorithm evaluates the student profile against the database of 25 local communities.
2. **Context Synthesis**: The top matching communities and the student profile are fed into the LLM system.
3. **Roadmap Generation**: The LLM analyzes the data and produces three distinct recommendation cards with personalized explanations, copyable icebreakers, and proposed meeting plans. If the API key is missing, the system uses a local template engine (**Mock AI Mode**) to guarantee instant, zero-setup pitch presentations.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Pip (Python Package Installer)
- *(Optional)* Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

---

### Running Locally

1. **Navigate to the Directory**:
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
- **Vector Database**: Storing and searching communities using dense embeddings (e.g., ChromaDB, Pinecone).
- **Dynamic Scrapers**: Ingesting university club listings and active Discord server directories.
- **Identity Verification**: Restricting community postings to university email domains (`.edu`).
- **Student-to-Student Matching**: Supporting secure one-on-one matches for peer coffee chats or homework study duos.

---

*Disclaimer: This is a university project Proof-of-Concept. It is not intended for commercial production use in its current form.*
