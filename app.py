import streamlit as st
import os
import json
from matcher import match_communities
from llm import generate_gemini_recommendations, generate_mock_recommendations

# Page Configuration
st.set_page_config(
    page_title="BuddyUp AI - Student Community Matching",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Load Custom Styles for Startup Pitch Look
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');

/* Apply clean fonts globally */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif;
}

/* Custom styles for pitch header card */
.hero-container {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #064E3B 100%);
    padding: 35px;
    border-radius: 20px;
    margin-bottom: 30px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: white;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.hero-title {
    margin: 0;
    font-family: 'Outfit', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(to right, #38BDF8, #34D399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    margin-top: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 1.35rem;
    font-weight: 400;
    color: #E2E8F0;
}

.hero-desc {
    margin-top: 15px;
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: #94A3B8;
    max-width: 600px;
    line-height: 1.5;
}

.poc-badge {
    display: inline-block;
    margin-top: 15px;
    padding: 6px 14px;
    background: rgba(56, 189, 248, 0.15);
    color: #38BDF8;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid rgba(56, 189, 248, 0.3);
}

/* Premium styled Recommendation Cards */
.custom-card {
    background-color: var(--background-color);
    color: var(--text-color);
    border: 1px solid var(--secondary-background-color);
    border-radius: 18px;
    padding: 28px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
    margin-bottom: 28px;
    border-left: 6px solid #2563EB;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.custom-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.03);
    border-color: #2563EB;
}

.card-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 12px;
}

.card-score-container {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 20px;
}

.score-bar-bg {
    background-color: var(--secondary-background-color);
    border-radius: 9999px;
    height: 12px;
    flex-grow: 1;
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.05);
}

.score-bar-fill {
    background: linear-gradient(90deg, #2563EB 0%, #10B981 100%);
    height: 100%;
    border-radius: 9999px;
}

.score-text {
    font-size: 1rem;
    font-weight: 700;
    color: #2563EB;
    min-width: 55px;
}

.card-label {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #64748B;
    margin-top: 15px;
    margin-bottom: 6px;
    letter-spacing: 0.06em;
}

.card-text {
    font-size: 1rem;
    line-height: 1.5;
    margin-bottom: 15px;
}

.icebreaker-box {
    background-color: var(--secondary-background-color);
    border-left: 4px solid #10B981;
    border-radius: 4px 14px 14px 4px;
    padding: 18px;
    margin-top: 15px;
    margin-bottom: 15px;
    box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.02);
}

.icebreaker-title {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #059669;
    margin-bottom: 8px;
    letter-spacing: 0.05em;
}

.icebreaker-content {
    font-style: italic;
    font-size: 0.98rem;
    line-height: 1.4;
}

.tag-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
}

.tag {
    background-color: var(--secondary-background-color);
    color: #2563EB;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid rgba(37, 99, 235, 0.15);
}

/* Sidebar stylings */
.sidebar-disclaimer {
    font-size: 0.85rem;
    line-height: 1.45;
    padding: 15px;
    border-radius: 12px;
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(0, 0, 0, 0.05);
    margin-top: 25px;
}

/* Workflow step cards */
.workflow-step {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 12px;
    padding: 16px;
    font-size: 0.95rem;
}

.workflow-arrow {
    text-align: center;
    font-size: 1.5rem;
    color: #94A3B8;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

# 1. Pitch Header / Hero Container
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">BuddyUp AI</h1>
    <h3 class="hero-subtitle">Find your community. Build your network.</h3>
    <p class="hero-desc">
        AI-powered community recommendations for university students moving to a new city.
        Discover local groups, receive personalized matching insights, and copy customized ice-breakers.
    </p>
    <div class="poc-badge">
        Proof-of-Concept using public Large Language Models
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/conference-call.png", width=80)
    st.header("Settings")
    
    st.subheader("AI Mode")
    ai_mode = st.radio(
        "Choose recommendation engine:",
        options=["Demo Mode (Mock AI)", "Gemini API"],
        index=0
    )
    
    gemini_key = ""
    if ai_mode == "Gemini API":
        gemini_key = st.text_input(
            "Gemini API Key:",
            type="password",
            placeholder="AIzaSy..."
        )
        st.markdown(
            "[Get a free Gemini API Key from Google AI Studio](https://aistudio.google.com/)",
            unsafe_allow_html=True
        )
        
    st.markdown("""
    <div class="sidebar-disclaimer">
        <strong>About BuddyUp AI</strong><br><br>
        This application is a Proof-of-Concept developed for an Entrepreneurship course.<br><br>
        It demonstrates how Large Language Models (LLMs) can support student integration and community building by matching profiles to a local knowledge base.
    </div>
    """, unsafe_allow_html=True)

# 3. Main Form
st.subheader("Start Matching")
st.write("Tell us about yourself and we will find the best communities for you.")

# Wrap the form
with st.form("matching_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        university_city = st.text_input(
            "University / City",
            value="Munich",
            placeholder="e.g., Munich, Berlin, Paris"
        )
        
        student_type = st.selectbox(
            "Student Type",
            options=[
                "First Semester",
                "International Student",
                "Erasmus Student",
                "Master Student"
            ]
        )
        
    with col2:
        primary_goal = st.selectbox(
            "Primary Goal",
            options=[
                "Make Friends",
                "Find Events",
                "Practice German",
                "Build Professional Network",
                "Reduce Loneliness"
            ]
        )
        
        preferred_group_size = st.radio(
            "Preferred Group Size",
            options=["Small", "Medium", "Large"],
            index=1,
            horizontal=True
        )

    interests = st.multiselect(
        "Interests",
        options=[
            "AI & Technology",
            "Gaming",
            "Sports",
            "Music",
            "Language Exchange",
            "Cooking",
            "Hiking",
            "Volunteering",
            "Startups",
            "Reading"
        ],
        default=["AI & Technology", "Startups"]
    )
    
    # Form submission
    submit_button = st.form_submit_button("Find my community 🚀", use_container_width=True)

# 4. Processing Recommendations
if submit_button:
    if not interests:
        st.warning("Please select at least one interest to help us match you.")
    else:
        # Build student profile
        student_profile = {
            "university_city": university_city,
            "student_type": student_type,
            "primary_goal": primary_goal,
            "preferred_group_size": preferred_group_size,
            "interests": interests
        }
        
        with st.spinner("Analyzing profile and searching database..."):
            # Step 1: Query Matcher algorithm
            matched_results = match_communities(student_profile, json_path="communities.json")
            
            # Step 2: Query LLM for explanations & icebreakers
            if ai_mode == "Gemini API" and gemini_key:
                recommendations = generate_gemini_recommendations(student_profile, matched_results, gemini_key)
            else:
                if ai_mode == "Gemini API" and not gemini_key:
                    st.info("No Gemini API key provided. Using Mock AI fallback.")
                recommendations = generate_mock_recommendations(student_profile, matched_results)
                
        # 5. Display Recommendations
        st.success(f"We found the top 3 communities for you in {university_city}!")
        
        for idx, rec in enumerate(recommendations):
            name = rec["name"]
            score = rec["match_score"]
            why_fits = rec["why_it_fits"]
            icebreaker = rec["suggested_icebreaker"]
            tags = rec["tags"]
            
            # Construct Tags HTML
            tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in tags])
            
            # Render styled card
            st.markdown(f"""
            <div class="custom-card">
                <div class="card-title">💡 {idx+1}. {name}</div>
                <div class="card-score-container">
                    <div class="score-text">{score}% Match</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width: {score}%;"></div>
                    </div>
                </div>
                <div class="card-label">Why it fits you</div>
                <div class="card-text">{why_fits}</div>
                <div class="icebreaker-box">
                    <div class="icebreaker-title">Suggested Icebreaker</div>
                    <div class="icebreaker-content">"{icebreaker}"</div>
                </div>
                <div class="card-label" style="margin-bottom: 8px;">Tags</div>
                <div class="tag-container">
                    {tags_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
# 6. Mini AI Workflow Section (Always Visible)
st.markdown('<hr style="border: 0; height: 1px; background: rgba(0,0,0,0.1); margin: 50px 0 30px 0;">', unsafe_allow_html=True)
st.subheader("How BuddyUp Works")

col_w1, col_w2, col_w3, col_w4 = st.columns(4)

with col_w1:
    st.markdown("""
    <div class="workflow-step">
        <strong>1. Profile Input</strong><br>
        Student enters city, type, goals, preferred group size, and interests.
    </div>
    """, unsafe_allow_html=True)

with col_w2:
    st.markdown("""
    <div class="workflow-step">
        <strong>2. Match Retrieval</strong><br>
        System scoring engine retrieves the top matching communities from database.
    </div>
    """, unsafe_allow_html=True)

with col_w3:
    st.markdown("""
    <div class="workflow-step">
        <strong>3. AI Reasoning</strong><br>
        AI checks compatibility of selected student profile and matching groups.
    </div>
    """, unsafe_allow_html=True)

with col_w4:
    st.markdown("""
    <div class="workflow-step">
        <strong>4. Final Output</strong><br>
        AI formats personalized justifications and community ice-breakers.
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="margin-top: 20px; font-size: 0.9rem; text-align: center; color: #64748B;">
    💡 <em>This prototype follows a lightweight Retrieval-Augmented Generation (RAG) approach by combining a local knowledge base with a Large Language Model.</em>
</div>
""", unsafe_allow_html=True)
