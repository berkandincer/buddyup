import json
import os
from typing import List, Dict, Any

def load_communities(json_path: str = "communities.json") -> List[Dict[str, Any]]:
    """Loads communities from a JSON file. Fallbacks to default data if file is missing."""
    if not os.path.exists(json_path):
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def match_communities(student_profile: Dict[str, Any], json_path: str = "communities.json") -> List[Dict[str, Any]]:
    """
    Ranks communities based on the updated student profile (including Situation, Activity Preference, and Personality).
    
    student_profile format:
    {
        "university_city": str,
        "student_type": str,
        "primary_goal": str,
        "preferred_group_size": str,
        "interests": List[str],
        "current_situations": List[str],
        "preferred_activity": str,
        "personality": str
    }
    """
    communities = load_communities(json_path)
    if not communities:
        return []

    scored_communities = []
    
    for comm in communities:
        score = 0
        
        # 1. Interests & Category Match (Max 35 points)
        # Interest overlap with community tags or matching the category
        matching_interests = 0
        category_lower = comm.get("category", "").lower().strip()
        comm_tags = [t.lower().strip() for t in comm.get("tags", [])]
        
        for interest in student_profile.get("interests", []):
            interest_lower = interest.lower().strip()
            
            # Category match weight
            if interest_lower in category_lower:
                matching_interests += 1.5
                
            # Tags match weight
            if interest_lower in comm_tags:
                matching_interests += 1.0
                
        interest_score = min(35, matching_interests * 10)
        score += interest_score
        
        # 2. Preferred Activity Match (Max 25 points)
        # Check if student's preferred activity matches category or tags
        pref_activity = student_profile.get("preferred_activity", "").lower().strip()
        
        if pref_activity in category_lower:
            score += 25
        elif any(pref_activity in tag for tag in comm_tags):
            score += 20
        else:
            # Partial or category association
            # e.g., Sports preferred activity matches "Running" or "Volleyball" or "Football"
            if pref_activity == "sports" and comm.get("category", "") in ["Sports", "Hiking"]:
                score += 15
            elif pref_activity == "study session" and comm.get("category", "") == "Study Session":
                score += 25
            elif pref_activity == "language exchange" and comm.get("category", "") == "Language Exchange":
                score += 25
            elif pref_activity == "hiking" and comm.get("category", "") == "Hiking":
                score += 25
            elif pref_activity == "gaming" and comm.get("category", "") == "Gaming":
                score += 25
            elif pref_activity == "coffee" and ("coffee" in comm_tags or "social" in comm_tags or comm.get("category", "") == "Language Exchange"):
                score += 15
                
        # 3. Goal Match (Max 20 points)
        comm_goals = [g.lower().strip() for g in comm.get("primary_goals", [])]
        student_goal = student_profile.get("primary_goal", "").lower().strip()
        
        if student_goal in comm_goals:
            score += 20
        else:
            # Check other situation-based overlaps
            score += 5
            
        # 4. Group Size & Personality Match (Max 12 points)
        preferred_size = student_profile.get("preferred_group_size", "").lower().strip()
        target_size = comm.get("target_group_size", "").lower().strip()
        personality = student_profile.get("personality", "").lower().strip()
        
        # Check size agreement
        size_match = (preferred_size == target_size)
        
        if size_match:
            score += 7
        
        # Personality compatibility check
        if personality == "introverted":
            # Introverts prefer Small/Medium groups, less intense socialization (Reading, Gaming, Study, Cooking)
            if target_size in ["small", "medium"]:
                score += 5
            if category_lower in ["reading", "gaming", "study session", "cooking"]:
                score += 3
        elif personality == "extroverted":
            # Extroverts prefer Large/Medium groups, active socialization (Sports, Volunteering, Startups, Language Exchange)
            if target_size in ["large", "medium"]:
                score += 5
            if category_lower in ["sports", "volunteering", "startups", "hiking"]:
                score += 3
        else: # Balanced
            score += 5  # Fits anywhere reasonably
            
        # 5. Situation Match (Max 8 points)
        situations = [s.lower().strip() for s in student_profile.get("current_situations", [])]
        comm_desc_lower = comm.get("description", "").lower()
        
        sit_bonus = 0
        if "looking for study partners" in situations:
            if "study" in category_lower or "study" in comm_desc_lower or "coding" in comm_tags:
                sit_bonus += 4
        if "erasmus student" in situations or "international student" in situations:
            if "erasmus" in comm_desc_lower or "international" in comm_desc_lower or "exchange" in comm_desc_lower or "language" in category_lower:
                sit_bonus += 4
        if "new in the city" in situations or "looking for new friends" in situations:
            if "social" in comm_desc_lower or "meetup" in comm_desc_lower or "friends" in comm_desc_lower:
                sit_bonus += 4
                
        score += min(8, sit_bonus)
        
        # Clamp score between 0 and 100
        final_score = int(min(100, max(0, score)))
        
        scored_communities.append({
            "community": comm,
            "match_score": final_score
        })
        
    # Sort by match_score descending
    scored_communities.sort(key=lambda x: x["match_score"], reverse=True)
    
    return scored_communities
