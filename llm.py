import json
import random
import logging
from typing import List, Dict, Any
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BuddyUp-LLM")

def generate_mock_recommendations(student_profile: Dict[str, Any], matched_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generates realistic, natural-sounding AI matching responses locally.
    Simulates LLM output with custom text generation tailored to the user profile.
    """
    city = student_profile.get("university_city", "your university")
    student_type = student_profile.get("student_type", "student")
    primary_goal = student_profile.get("primary_goal", "Make Friends").lower()
    group_size = student_profile.get("preferred_group_size", "Medium").lower()
    interests = student_profile.get("interests", ["Socializing"])
    
    interests_phrase = ", ".join(interests[:-1]) + (" and " + interests[-1] if len(interests) > 1 else interests[0]) if interests else "student activities"
    first_interest = interests[0] if interests else "extracurriculars"
    
    recommendations = []
    
    # Generic templates for fallback, but we will specialize based on categories below
    for item in matched_results:
        comm = item["community"]
        score = item["match_score"]
        name = comm["name"]
        category = comm["category"]
        desc = comm["description"]
        tags = comm["tags"]
        
        # 1. Custom 'Why it fits' generation based on student goal and student type
        why_fits_templates = [
            f"As an {student_type} adapting to {city}, you highlighted a desire to {primary_goal}. '{name}' is a stellar match because it offers a {group_size}-sized ecosystem built around {category}. It brings together peers sharing interests in {interests_phrase}, allowing you to bypass typical social friction and build connections in a structured, friendly environment.",
            
            f"You mentioned your main objective is to {primary_goal} while studying in {city}. Since you are interested in {first_interest}, '{name}' provides the exact community you need. The group's size and focus are ideal for {student_type}s looking to settle in quickly and engage in meaningful shared activities.",
            
            f"'{name}' naturally aligns with your profile as a {student_type}. It directly addresses your goal to {primary_goal} by hosting active gatherings themed around {category}. The community is highly welcoming to newcomers in {city} who share your enthusiasm for {interests_phrase}."
        ]
        why_fits = random.choice(why_fits_templates)
        
        # Customize 'Why it fits' depending on specific goals/types to make it feel extremely human
        if "german" in primary_goal:
            why_fits = f"Since your main goal is to practice German, '{name}' is an ideal fit. It creates a low-pressure environment for a {student_type} in {city} to speak the language in real-life contexts. Engaging with this group will help you build conversational confidence rapidly while sharing your interests in {first_interest}."
        elif "loneliness" in primary_goal:
            why_fits = f"Moving to a new city can be isolating, but joining a {group_size}-sized community like '{name}' is one of the fastest ways to reduce loneliness. Because they focus on active participation in {category}, you will find welcoming student peers who share your passion for {first_interest}, helping you build a support network in {city}."
        elif "network" in primary_goal:
            why_fits = f"For a {student_type} looking to build a professional network, '{name}' represents a key hub in the local student ecosystem. It connects you with career-minded individuals and events in the field of {category}, offering outstanding opportunities to exchange ideas and gain early mentorship in {city}."

        # 2. Custom Icebreaker generation based on category/interests
        icebreaker = f"Hi everyone! I just moved to {city} as a {student_type} and would love to join your next meetup. I'm really interested in {first_interest}—hope to chat soon!"
        
        category_lower = category.lower()
        if "sport" in category_lower:
            icebreaker = f"Hi! I'm a {student_type} in {city} and I'm really keen to join the next session of '{name}'. What skill levels do you usually play at, and do I need to bring any specific gear? Looking forward to meeting you guys!"
        elif "game" in category_lower or "gaming" in category_lower:
            icebreaker = f"Hey players! I just saw '{name}' online and love gaming. I'm new in town and would love to drop by for the next session. What games or platforms are you currently focusing on? Count me in!"
        elif "tech" in category_lower or "ai" in category_lower:
            icebreaker = f"Hi there! I'm a {student_type} interested in technology and AI. I'd love to join the next workshop or hackathon hosted by '{name}'. Is there a Discord server or group chat I can join to keep up with projects?"
        elif "language" in category_lower:
            icebreaker = f"Hallo! I'm an international student here in {city} looking to practice my German. Is '{name}' open to beginners? I'd love to drop by, practice conversational skills, and grab a coffee together!"
        elif "cook" in category_lower:
            icebreaker = f"Hi everyone! I love cooking and discovering new recipes. I'm new to the university and would love to attend the next kitchen meetup or workshop. What country's cuisine are we exploring next?"
        elif "hike" in category_lower or "outdoor" in category_lower:
            icebreaker = f"Hey hikers! I'm a {student_type} looking to explore the trails around {city}. I'd love to tag along on your next weekend hiking trip. How strenuous is the route, and what gear would you recommend bringing?"
        elif "volunteer" in category_lower:
            icebreaker = f"Hi! I'm looking to get involved in local volunteering while studying here. The sustainability work you do at '{name}' sounds amazing. How can I sign up for the next session?"
        elif "music" in category_lower:
            icebreaker = f"Hey everyone! I play a bit of instrument and would love to join the next session. What kind of music do you usually cover or jam to? Can't wait to play together!"
        elif "startup" in category_lower:
            icebreaker = f"Hi team! I'm a {student_type} looking to get plugged into the local startup scene here in {city}. I'm excited to attend the next pitch event or networking evening. Who should I contact to get started?"
            
        recommendations.append({
            "name": name,
            "match_score": score,
            "why_it_fits": why_fits,
            "suggested_icebreaker": icebreaker,
            "tags": tags
        })
        
    return recommendations


def generate_gemini_recommendations(student_profile: Dict[str, Any], matched_results: List[Dict[str, Any]], api_key: str) -> List[Dict[str, Any]]:
    """
    Queries the Gemini API to get highly personalized recommendations based on the student's profile
    and the top 3 communities retrieved by the matching engine.
    """
    if not api_key:
        logger.warning("No API key provided for Gemini. Falling back to Mock AI.")
        return generate_mock_recommendations(student_profile, matched_results)

    try:
        # Configure the Google Generative AI library
        genai.configure(api_key=api_key)
        
        # We will use gemini-1.5-flash which is fast, cheap and highly capable
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Convert matched communities structure for prompt
        communities_prompt_info = []
        for item in matched_results:
            comm = item["community"]
            score = item["match_score"]
            communities_prompt_info.append({
                "name": comm["name"],
                "category": comm["category"],
                "description": comm["description"],
                "tags": comm["tags"],
                "match_score": score
            })
            
        prompt = f"""
You are an expert student integration assistant and community matcher.
Your goal is to help a newly arrived student feel welcomed and find their community.

We have a student profile:
- University/City: {student_profile.get('university_city')}
- Student Type: {student_profile.get('student_type')}
- Primary Goal: {student_profile.get('primary_goal')}
- Preferred Group Size: {student_profile.get('preferred_group_size')}
- Interests: {", ".join(student_profile.get('interests', []))}

We have retrieved the top 3 matching communities from our database:
{json.dumps(communities_prompt_info, indent=2)}

For each of these 3 communities, please write:
1. "why_it_fits": A highly personalized explanation of why this community is a great match for this specific student, addressing their student type, goals, city, and interests. Write 2-3 sentences. Make it sound warm, professional, encouraging, and intelligent.
2. "suggested_icebreaker": A ready-to-copy, friendly icebreaker message the student can send to this community's group chat or organizer. Tailor it to the community's theme and the student's background. Include a placeholder or keep it simple.

Return your response strictly as a valid JSON array of 3 elements with the exact keys: "name", "match_score", "why_it_fits", "suggested_icebreaker", "tags".
Ensure the "match_score" corresponds to the score provided in the input, and the "tags" corresponds to the tags in the input.

Example JSON output structure:
[
  {{
    "name": "Community Name",
    "match_score": 95,
    "why_it_fits": "Personalized explanation here...",
    "suggested_icebreaker": "Hi! I am...",
    "tags": ["Tag1", "Tag2"]
  }}
]
"""
        
        # Set configuration for JSON output if supported, else query normally
        # In newer versions of the SDK, you can pass response_mime_type
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        
        # Clean response text in case markdown block surrounds it
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        parsed_data = json.loads(response_text)
        
        # Validate elements have the correct keys, fallback if parsing is malformed
        validated_data = []
        for idx, item in enumerate(parsed_data):
            # Check if fields exist, otherwise pull from original matched results
            name = item.get("name", matched_results[idx]["community"]["name"])
            score = item.get("match_score", matched_results[idx]["match_score"])
            why_fits = item.get("why_it_fits", "")
            icebreaker = item.get("suggested_icebreaker", "")
            tags = item.get("tags", matched_results[idx]["community"]["tags"])
            
            if not why_fits or not icebreaker:
                # If fields are empty, raise error to trigger fallback
                raise ValueError("Incomplete fields returned by Gemini API")
                
            validated_data.append({
                "name": name,
                "match_score": int(score),
                "why_it_fits": why_fits,
                "suggested_icebreaker": icebreaker,
                "tags": tags
            })
            
        return validated_data
        
    except Exception as e:
        logger.error(f"Gemini API matching failed: {str(e)}. Falling back to Mock AI.")
        return generate_mock_recommendations(student_profile, matched_results)
