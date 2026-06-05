import streamlit as st
import os
import json
import textwrap
from matcher import match_communities
from llm import generate_gemini_recommendations, generate_mock_recommendations

# Page Configuration
st.set_page_config(
    page_title="BuddyUp AI",
    page_icon="🤝",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Helper function to prevent Markdown parser from converting HTML to raw text code blocks
def render_html(html_code: str):
    cleaned_lines = [line.strip() for line in html_code.splitlines()]
    st.markdown("\n".join(cleaned_lines), unsafe_allow_html=True)

# Inject modern, welcoming premium DARK THEME styles
render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;700;800&display=swap');

/* Apply clean fonts globally */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
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

.badge-container {
    margin-top: 15px;
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.badge-item {
    font-size: 0.85rem;
    font-weight: 600;
    color: #38BDF8;
    background: rgba(56, 189, 248, 0.15);
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid rgba(56, 189, 248, 0.3);
}

/* Find My Community submit button styling */
div[data-testid="stForm"] button[kind="primaryFormSubmit"], 
div[data-testid="stForm"] button[kind="secondaryFormSubmit"] {
    height: 64px !important;
    border-radius: 18px !important;
    background: linear-gradient(90deg, #7C3AED, #8B5CF6) !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 22px !important;
    box-shadow: 0 4px 14px rgba(124, 58, 237, 0.15) !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    margin-top: 15px !important;
    width: 100% !important;
}

div[data-testid="stForm"] button[kind="primaryFormSubmit"]:hover, 
div[data-testid="stForm"] button[kind="secondaryFormSubmit"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124, 58, 237, 0.25) !important;
    background: linear-gradient(90deg, #6D28D9, #7C3AED) !important;
}

/* Premium styled Recommendation Cards */
.custom-card {
    background-color: #1E293B !important;
    border: 1px solid #334155 !important;
    border-radius: 18px !important;
    padding: 28px !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1) !important;
    margin-bottom: 25px !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
}

.custom-card:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2) !important;
    border-color: #7C3AED !important;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.card-type-badge {
    display: inline-block;
    padding: 4px 10px;
    background-color: rgba(124, 58, 237, 0.2);
    color: #C084FC;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
}

.score-text {
    font-size: 0.95rem;
    font-weight: 700;
    color: #14B8A6;
}

.score-bar-bg {
    background-color: #334155;
    border-radius: 9999px;
    height: 8px;
    overflow: hidden;
    margin-bottom: 15px;
    border: 1px solid #475569;
}

.score-bar-fill {
    background: linear-gradient(90deg, #7C3AED 0%, #06B6D4 100%);
    height: 100%;
    border-radius: 9999px;
}

.card-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 12px;
    color: #FFFFFF;
}

.card-label {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #94A3B8;
    margin-top: 15px;
    margin-bottom: 4px;
    letter-spacing: 0.06em;
}

.card-text {
    font-size: 0.95rem;
    line-height: 1.5;
    color: #E2E8F0;
}

.icebreaker-box {
    background-color: #0F172A;
    border-left: 4px solid #10B981;
    border-radius: 4px 14px 14px 4px;
    padding: 16px;
    margin-top: 15px;
    margin-bottom: 15px;
    box-shadow: inset 0 2px 4px 0 rgba(0,0,0,0.2);
}

.icebreaker-title {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    color: #34D399;
    margin-bottom: 6px;
    letter-spacing: 0.05em;
}

.icebreaker-content {
    font-style: italic;
    font-size: 0.95rem;
    line-height: 1.4;
    color: #F1F5F9;
}

.meeting-activity {
    font-size: 0.95rem;
    font-weight: 600;
    color: #A78BFA;
}

.tag-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 15px;
}

.tag-pill {
    background-color: rgba(124, 58, 237, 0.15) !important;
    color: #C084FC !important;
    padding: 6px 14px !important;
    border-radius: 999px !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    display: inline-block !important;
    border: 1px solid rgba(124, 58, 237, 0.3) !important;
}

/* Verified Community Banner style */
.verified-banner {
    display: flex;
    align-items: center;
    gap: 12px;
    background-color: rgba(20, 184, 166, 0.1);
    border: 1px solid rgba(20, 184, 166, 0.3);
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 25px;
    color: #14B8A6;
}

/* Interview Insights Card styles */
.insight-card {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px;
    text-align: left;
    height: 100%;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}

.insight-icon {
    font-size: 1.6rem;
    margin-bottom: 8px;
}

.insight-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 4px;
}

.insight-text {
    font-size: 0.88rem;
    line-height: 1.4;
    font-weight: 500;
    color: #94A3B8;
}

/* About Card Sidebar styling */
.about-card {
    background-color: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px;
    margin-top: 25px;
}

.about-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 8px;
    font-family: 'Outfit', sans-serif;
}

.about-text {
    font-size: 0.85rem;
    color: #94A3B8;
    line-height: 1.4;
}

.about-footer {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 12px;
    text-align: center;
    border-top: 1px solid #334155;
    padding-top: 8px;
}
</style>
""")

# 1. Pitch Header / Hero Container (Dark gradient hero banner)
render_html("""
<div class="hero-container">
    <div class="hero-title">BuddyUp AI</div>
    <div class="hero-subtitle">Find your people. Build your community.</div>
    <p class="hero-desc">
        Helping students discover friends, communities and local activities.
    </p>
    <div class="badge-container">
        <span class="badge-item">• Student Matching</span>
        <span class="badge-item">• Verified Communities</span>
        <span class="badge-item">• AI Recommendations</span>
    </div>
</div>
""")

# 2. Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/conference-call.png", width=65)
    st.markdown("### BuddyUp AI")
    st.caption("Find your people. Build your community.")
    st.markdown("---")
    
    st.markdown("**AI Recommendation Engine**")
    st.caption("BuddyUp uses Google's Gemini model to generate personalized recommendations.")
    
    # Hide the choice selection but keep it internally configured
    st.radio(
        "Active Engine",
        options=["Gemini AI"],
        index=0,
        label_visibility="collapsed"
    )
    
    gemini_key = st.text_input(
        "Gemini API Key:",
        type="password",
        placeholder="AIzaSy..."
    )
    st.markdown(
        "<a href='https://aistudio.google.com/' style='color:#A78BFA; font-size:0.8rem; font-weight:600; text-decoration:none;'>Get a Gemini API Key from Google AI Studio</a>",
        unsafe_allow_html=True
    )
    
    # Sidebar About Card (Polished dark card)
    render_html("""
    <div class="about-card">
        <div class="about-title">About BuddyUp AI</div>
        <div class="about-text">
            BuddyUp AI helps students discover new friends, communities and activities based on shared interests.
        </div>
        <div class="about-footer">Made with ❤️ for students.</div>
    </div>
    """)

# 3. Main Form Container
with st.form("matching_form"):
    # Render premium onboarding title inside the container
    render_html("""
    <div style="margin-bottom: 30px;">
        <h2 style="font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 700; color: #FFFFFF; margin: 0;">✨ Tell us about yourself</h2>
        <p style="font-family: 'Inter', sans-serif; font-size: 0.95rem; color: #94A3B8; margin: 6px 0 0 0;">Help BuddyUp find the perfect communities for you.</p>
    </div>
    """)
    
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
        
        current_situations = st.multiselect(
            "Current Situation",
            options=[
                "New in the city",
                "International Student",
                "Erasmus Student",
                "Looking for Study Partners",
                "Looking for New Friends"
            ],
            default=["New in the city", "Looking for New Friends"]
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
        
        preferred_activity = st.selectbox(
            "Preferred Activity",
            options=[
                "Coffee",
                "Sports",
                "Study Session",
                "Gaming",
                "Hiking",
                "Language Exchange",
                "Networking Event"
            ],
            index=0
        )
        
        personality = st.radio(
            "Personality Type",
            options=["Introverted", "Balanced", "Extroverted"],
            index=1,
            horizontal=True
        )

    # Full-width lower form elements
    col3, col4 = st.columns([1, 2])
    with col3:
        preferred_group_size = st.radio(
            "Preferred Group Size",
            options=["Small", "Medium", "Large"],
            index=1,
            horizontal=True
        )
    with col4:
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
    
    # Onboarding Form Button
    submit_button = st.form_submit_button("✨ Find My Community", use_container_width=True)

# 4. Processing Recommendations
if submit_button:
    if not interests:
        st.warning("Please select at least one interest to help us match you.")
    elif not current_situations:
        st.warning("Please select at least one current situation aspect.")
    else:
        # Build student profile
        student_profile = {
            "university_city": university_city,
            "student_type": student_type,
            "primary_goal": primary_goal,
            "preferred_group_size": preferred_group_size,
            "interests": interests,
            "current_situations": current_situations,
            "preferred_activity": preferred_activity,
            "personality": personality
        }
        
        with st.spinner("Analyzing profile and generating recommendations..."):
            # Step 1: Query Matcher algorithm
            matched_results = match_communities(student_profile, json_path="communities.json")
            
            # Step 2: Query LLM for explanations & icebreakers
            if gemini_key:
                recommendations = generate_gemini_recommendations(student_profile, matched_results, gemini_key)
            else:
                recommendations = generate_mock_recommendations(student_profile, matched_results)
                
        # 5. Display Recommendations
        st.success(f"We generated your personalized BuddyUp roadmap in {university_city}!")
        
        # Display Verified Community Banner
        render_html("""
        <div class="verified-banner">
            <span class="verified-icon">🛡️</span>
            <div class="verified-text">
                <strong style="color: #14B8A6;">Verified Student Community</strong><br>
                <span style="color: #E2E8F0; font-size: 0.88rem;">Only verified university communities and student profiles are recommended.</span>
            </div>
        </div>
        """)
        
        for idx, rec in enumerate(recommendations):
            rec_type = rec.get("recommendation_type", "Best Choice")
            name = rec["name"]
            score = rec["match_score"]
            why_fits = rec["why_it_fits"]
            icebreaker = rec["suggested_icebreaker"]
            meeting = rec.get("suggested_meeting", "Meet on campus")
            tags = rec["tags"]
            
            # Icon styling based on recommendation type
            icon_badge = "🥇"
            if "Activity" in rec_type:
                icon_badge = "⚡"
            elif "People" in rec_type:
                icon_badge = "👥"
                
            # Build Tags HTML
            tags_html = " ".join([f'<span class="tag-pill">{tag}</span>' for tag in tags])
            
            # Render custom HTML card
            render_html(f"""
            <div class="custom-card">
                <div class="card-header">
                    <span class="card-type-badge">{icon_badge} {rec_type}</span>
                    <span class="score-text">{score}% Match</span>
                </div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill" style="width: {score}%;"></div>
                </div>
                <div class="card-title">{name}</div>
                
                <div class="card-label">Why this matches you</div>
                <div class="card-text">{why_fits}</div>
                
                <div class="icebreaker-box">
                    <div class="icebreaker-title">💬 Suggested Icebreaker</div>
                    <div class="icebreaker-content">"{icebreaker}"</div>
                </div>
                
                <div class="card-label">🤝 Suggested Meeting Activity</div>
                <div class="meeting-activity">{meeting}</div>
                
                <div class="tag-container">
                    {tags_html}
                </div>
            </div>
            """)

# Space divider
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# 5. Interview Insights Section (Optimistic & Premium 3-card layout)
st.subheader("✨ Built from real student feedback")
st.write("Insights gathered from interviews with international and local students.")

col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    render_html("""
    <div class="insight-card">
        <div class="insight-icon">🤝</div>
        <div class="insight-title">Shared Interests</div>
        <div class="insight-text">Students prefer meeting people through common hobbies and activities.</div>
    </div>
    """)

with col_in2:
    render_html("""
    <div class="insight-card">
        <div class="insight-icon">🛡️</div>
        <div class="insight-title">Trusted Community</div>
        <div class="insight-text">Verified profiles help students feel safer when meeting new people.</div>
    </div>
    """)

with col_in3:
    render_html("""
    <div class="insight-card">
        <div class="insight-icon">⚡</div>
        <div class="insight-title">Spontaneous Activities</div>
        <div class="insight-text">Students want to quickly find people to join activities together.</div>
    </div>
    """)
