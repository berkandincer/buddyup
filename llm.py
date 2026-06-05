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
    Produces exactly three cards:
    1. Best Community (matching the top community from matcher)
    2. Best Activity (an action-oriented event tailored to preferred_activity)
    3. Best Type of People to Meet (tailored to personality and goals)
    """
    city = student_profile.get("university_city", "your university")
    student_type = student_profile.get("student_type", "student")
    primary_goal = student_profile.get("primary_goal", "Make Friends")
    group_size = student_profile.get("preferred_group_size", "Medium")
    interests = student_profile.get("interests", ["Socializing"])
    situations = student_profile.get("current_situations", ["New in the city"])
    pref_activity = student_profile.get("preferred_activity", "Coffee")
    personality = student_profile.get("personality", "Balanced")

    # Helper text variables
    interests_phrase = ", ".join(interests[:-1]) + (" and " + interests[-1] if len(interests) > 1 else interests[0]) if interests else "student activities"
    first_interest = interests[0] if interests else "extracurriculars"
    situations_phrase = ", ".join([s.lower() for s in situations])

    recommendations = []

    # ----------------------------------------------------
    # CARD 1: BEST COMMUNITY
    # ----------------------------------------------------
    top_comm_item = matched_results[0] if matched_results else {
        "community": {
            "name": "Erasmus & International Meetup",
            "category": "Volunteering",
            "description": "Social gatherings and tours.",
            "tags": ["International", "Social"]
        },
        "match_score": 90
    }
    
    comm = top_comm_item["community"]
    comm_score = top_comm_item["match_score"]
    
    why_fits_comm = (
        f"You indicated that you are {situations_phrase}, identify as {personality.lower()}, and want to {primary_goal.lower()}. "
        f"The '{comm['name']}' fits you perfectly as it specializes in {comm['category'].lower()}. "
        f"It provides a structured environment where you can connect with students sharing your interests in {interests_phrase}."
    )
    
    # Custom icebreaker for community
    comm_icebreaker = f"Hi everyone! I just moved to {city} and saw this group. I'm really interested in {first_interest}. Are there any events coming up this week?"
    comm_category = comm["category"].lower()
    if "study" in comm_category:
        comm_icebreaker = "Hey study partners! I'm looking to work on some course materials and prepare for exams. Anyone up for a study session at the library this week?"
    elif "sports" in comm_category or "hiking" in comm_category:
        comm_icebreaker = f"Hey! I'm a {student_type} and love staying active. I'd love to join the next session/run of '{comm['name']}'. What skill level is it?"
    
    recommendations.append({
        "recommendation_type": "Best Community",
        "name": comm["name"],
        "match_score": comm_score,
        "why_it_fits": why_fits_comm,
        "suggested_icebreaker": comm_icebreaker,
        "suggested_meeting": f"Meet outside the main campus building 10 minutes before their next session.",
        "tags": comm["tags"]
    })

    # ----------------------------------------------------
    # CARD 2: BEST ACTIVITY
    # ----------------------------------------------------
    # Search database for a community matching preferred_activity, otherwise pick the second match
    activity_comm = None
    for item in matched_results[1:]:
        comm_cat = item["community"]["category"].lower()
        if pref_activity.lower() in comm_cat or any(pref_activity.lower() in t.lower() for t in item["community"]["tags"]):
            activity_comm = item
            break
    if not activity_comm and len(matched_results) > 1:
        activity_comm = matched_results[1]
    elif not activity_comm:
        activity_comm = top_comm_item
        
    act_comm_data = activity_comm["community"]
    act_score = min(98, activity_comm["match_score"] + 2) # activities feel more direct, boost score slightly
    
    # Map preferred activity to dynamic activity titles
    activity_titles = {
        "coffee": "Informal Café Coffee Chat",
        "sports": f"Friendly {act_comm_data['name']} Match",
        "study session": "Collaborative Library Study Sprint",
        "gaming": f"Weekly {act_comm_data['name']} Session",
        "hiking": "Weekend Trail Exploration Hike",
        "language exchange": "Intercultural Language Café Session",
        "networking event": "Pitch Night & Professional Networking Mixer"
    }
    
    activity_title = activity_titles.get(pref_activity.lower(), f"Spontaneous {act_comm_data['name']} Gathering")
    
    why_fits_act = (
        f"Since your preferred activity style is a {pref_activity.lower()} and you want to {primary_goal.lower()}, "
        f"participating in this event is a highly effective step. It features a {act_comm_data['target_group_size'].lower()} group setting "
        f"which aligns with your {personality.lower()} personality, making interactions feel natural and low-pressure."
    )
    
    act_icebreaker = f"Hi! I see you are organizing the next {pref_activity.lower()} meetup for {act_comm_data['name']}. I'd love to tag along. Is there space for one more?"
    if pref_activity.lower() == "coffee":
        act_icebreaker = f"Hi there! I'm new in the city and looking to meet students for a coffee. Anyone free to check out that new café near the campus library tomorrow?"
    
    recommendations.append({
        "recommendation_type": "Best Activity",
        "name": activity_title,
        "match_score": act_score,
        "why_it_fits": why_fits_act,
        "suggested_icebreaker": act_icebreaker,
        "suggested_meeting": f"Meet at a central student café or the library foyer before heading over together.",
        "tags": [pref_activity, act_comm_data["category"], "Spontaneous"]
    })

    # ----------------------------------------------------
    # CARD 3: BEST TYPE OF PEOPLE TO MEET
    # ----------------------------------------------------
    # Determine peer profile names based on personality and goals
    peer_title = "Friendly Explorer Students"
    peer_tags = ["Open-minded", "Student-focused"]
    
    if personality.lower() == "introverted":
        if "study" in situations_phrase or "network" in primary_goal.lower():
            peer_title = "Focused & Analytical Tech Peers"
            peer_tags = ["Thoughtful", "Goal-oriented", "Quiet Co-working"]
            why_fits_peer = (
                f"As an introverted student looking to {primary_goal.lower()}, you will find comfort and productivity "
                f"among career-driven, tech-minded peers. They prefer small study sessions and deep topic discussions, "
                f"allowing you to build trust and professional connections without social burnout."
            )
        else:
            peer_title = "Cozy Gamers & Creative Minds"
            peer_tags = ["Cozy", "Creative", "Low-pressure"]
            why_fits_peer = (
                f"Since you identify as introverted and enjoy {first_interest.lower()}, you would thrive by connecting "
                f"with students who enjoy relaxed, small-scale activities like board games, cooking, or reading. "
                f"This peer group values deeper, one-on-one relationships over loud group settings."
            )
    elif personality.lower() == "extroverted":
        if "sports" in [i.lower() for i in interests] or pref_activity.lower() == "sports":
            peer_title = "High-Energy Sports & Outdoor Enthusiasts"
            peer_tags = ["Active", "Outgoing", "Fitness-focused"]
            why_fits_peer = (
                f"Being extroverted and interested in sports, you match best with high-energy students who love "
                f"outdoor activities and spontaneous matches. They are outgoing, easy to approach on the field, "
                f"and constantly organizing group outings in the city."
            )
        else:
            peer_title = "Social Event Organizers & Networkers"
            peer_tags = ["Extroverted", "Expressive", "Well-connected"]
            why_fits_peer = (
                f"Your outgoing nature and goal to {primary_goal.lower()} mean you will synergize perfectly with "
                f"highly social students, event hosts, and student representatives. They can introduce you "
                f"to multiple circles quickly and get you plugged into the local student culture."
            )
    else: # Balanced
        peer_title = "Multilingual Culturally-Curious Explorers"
        peer_tags = ["Intercultural", "Adaptable", "English Friendly"]
        why_fits_peer = (
            f"With a balanced personality, you fit well with international and Erasmus students who are also "
            f"new to the city. They are open, adaptable, and eager to try different activities, "
            f"whether it's a quick coffee, a study session, or exploring the city together."
        )

    peer_icebreaker = f"Hey! I saw your post in the student channel. I'm also studying here and interested in {first_interest.lower()}. Would you be down to grab lunch at the canteen sometime this week?"
    
    recommendations.append({
        "recommendation_type": "Best Type of People to Meet",
        "name": peer_title,
        "match_score": 92,
        "why_it_fits": why_fits_peer,
        "suggested_icebreaker": peer_icebreaker,
        "suggested_meeting": "Arrange a casual lunch or a coffee catchup at the university canteen.",
        "tags": peer_tags
    })

    return recommendations


def generate_gemini_recommendations(student_profile: Dict[str, Any], matched_results: List[Dict[str, Any]], api_key: str) -> List[Dict[str, Any]]:
    """
    Queries the Gemini API to get three personalized cards: Best Community, Best Activity, and Best Type of People to Meet.
    """
    if not api_key:
        logger.warning("No API key provided for Gemini. Falling back to Mock AI.")
        return generate_mock_recommendations(student_profile, matched_results)

    try:
        # Configure Gemini SDK
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Take top communities to feed into the prompt context
        top_comms_context = []
        for item in matched_results[:5]: # Send top 5 to give Gemini enough context to choose
            comm = item["community"]
            score = item["match_score"]
            top_comms_context.append({
                "name": comm["name"],
                "category": comm["category"],
                "description": comm["description"],
                "tags": comm["tags"],
                "match_score": score
            })

        prompt = f"""
You are an expert student integration assistant and community matcher.
Your goal is to help a student who has recently moved or is struggling to build social circles.

We have a student profile:
- University/City: {student_profile.get('university_city')}
- Student Type: {student_profile.get('student_type')}
- Current Situations: {", ".join(student_profile.get('current_situations', []))}
- Primary Goal: {student_profile.get('primary_goal')}
- Preferred Activity Style: {student_profile.get('preferred_activity')}
- Personality Type: {student_profile.get('personality')}
- Interests: {", ".join(student_profile.get('interests', []))}

We have retrieved the top matching student communities from our database:
{json.dumps(top_comms_context, indent=2)}

Please generate exactly 3 recommendations of different types:
1. "Best Community": Select the single best matching community from the retrieved list. Use the community name as the name.
2. "Best Activity": A specific action-oriented event or gathering related to their preferred activity style (e.g. "Library Study Sprint" for Study, "Sunday Alpine hike" for hiking, "Canteen Coffee meetup"). Make it sound exciting and tailored to their personality.
3. "Best Type of People to Meet": A description of the ideal peer profile they should look for (e.g. "Quiet tech-minded creators", "Extroverted outdoor adventurers", "Culturally curious international explorers").

For each of the 3 recommendations, provide:
- "recommendation_type": Must be exactly "Best Community", "Best Activity", or "Best Type of People to Meet".
- "name": The title of this recommendation.
- "match_score": An integer (0-100) representing how well this fits the profile. For "Best Community", use its score from the matched list.
- "why_it_fits": A highly personalized 2-3 sentence explanation explaining why this fits their personality, current situation, and goals.
- "suggested_icebreaker": A copyable ready-to-send message they can use to initiate contact.
- "suggested_meeting": A short suggestion on where or how they should meet (e.g., "Grab coffee after the event", "Meet at the university gate").
- "tags": A list of 3 relevant tags.

Return your response strictly as a valid JSON array of 3 elements with keys: "recommendation_type", "name", "match_score", "why_it_fits", "suggested_icebreaker", "suggested_meeting", "tags".
Ensure there are no markdown blocks or backticks in the raw API response other than the JSON itself.

Example JSON output structure:
[
  {{
    "recommendation_type": "Best Community",
    "name": "TUM Math & CS Study Group",
    "match_score": 92,
    "why_it_fits": "Since you are looking for study partners and identify as introverted...",
    "suggested_icebreaker": "Hi! I saw your study group...",
    "suggested_meeting": "Meet at the main library lobby.",
    "tags": ["Study Session", "Coding", "Mathematics"]
  }},
  ...
]
"""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        parsed_data = json.loads(response_text)
        
        # Verify schema elements and return
        validated_data = []
        for item in parsed_data:
            validated_data.append({
                "recommendation_type": item.get("recommendation_type", "Best Community"),
                "name": item.get("name", "Student Meetup"),
                "match_score": int(item.get("match_score", 85)),
                "why_it_fits": item.get("why_it_fits", "Matches your interests."),
                "suggested_icebreaker": item.get("suggested_icebreaker", "Hello!"),
                "suggested_meeting": item.get("suggested_meeting", "Meet on campus."),
                "tags": item.get("tags", ["Student", "Social"])
            })
            
        return validated_data
        
    except Exception as e:
        logger.error(f"Gemini API query failed: {str(e)}. Falling back to Mock AI.")
        return generate_mock_recommendations(student_profile, matched_results)
