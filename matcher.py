import json
import os
from typing import List, Dict, Any

def load_communities(json_path: str = "communities.json") -> List[Dict[str, Any]]:
    """Loads communities from a JSON file. Fallbacks to default data if file is missing."""
    if not os.path.exists(json_path):
        # Fallback inline list just in case
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def match_communities(student_profile: Dict[str, Any], json_path: str = "communities.json") -> List[Dict[str, Any]]:
    """
    Ranks communities based on the student's profile and returns the top 3 matches
    with calculated score details.
    
    student_profile format:
    {
        "university_city": str,
        "student_type": str,
        "primary_goal": str,
        "preferred_group_size": str,
        "interests": List[str]
    }
    """
    communities = load_communities(json_path)
    if not communities:
        return []

    scored_communities = []
    
    for comm in communities:
        score = 0
        max_possible_score = 100
        
        # 1. Interests & Category Match (Max 50 points)
        # Interest overlap with community tags or matching the category
        matching_interests = 0
        for interest in student_profile.get("interests", []):
            # Normalise comparison
            interest_lower = interest.lower().strip()
            
            # Check category
            if interest_lower in comm.get("category", "").lower():
                matching_interests += 1.5  # Category match has higher weight
                
            # Check tags
            comm_tags = [t.lower().strip() for t in comm.get("tags", [])]
            if interest_lower in comm_tags:
                matching_interests += 1
                
        # Calculate interest score contribution
        interest_score = min(50, matching_interests * 15)
        score += interest_score
        
        # 2. Goal Match (Max 30 points)
        # Check if student's primary goal is one of the community's primary goals
        goal_match = False
        comm_goals = [g.lower().strip() for g in comm.get("primary_goals", [])]
        student_goal = student_profile.get("primary_goal", "").lower().strip()
        
        if student_goal in comm_goals:
            score += 30
            goal_match = True
        else:
            # Partial goals overlap
            score += 10
            
        # 3. Group Size Match (Max 20 points)
        preferred_size = student_profile.get("preferred_group_size", "").lower().strip()
        target_size = comm.get("target_group_size", "").lower().strip()
        
        if preferred_size == target_size:
            score += 20
        else:
            # If they prefer Medium, and it is Small or Large, it's a minor match
            if preferred_size == "medium" or target_size == "medium":
                score += 10
            else:
                score += 5
                
        # 4. Contextual Student Type Bonus (Max 10 points)
        # e.g., Erasmus or International students get a bonus for international/language communities
        student_type = student_profile.get("student_type", "").lower()
        comm_name_lower = comm.get("name", "").lower()
        comm_desc_lower = comm.get("description", "").lower()
        
        bonus = 0
        if "international" in student_type or "erasmus" in student_type:
            if "international" in comm_name_lower or "erasmus" in comm_name_lower or "language" in comm_name_lower or "exchange" in comm_name_lower:
                bonus += 10
        elif "first semester" in student_type:
            if "social" in comm_desc_lower or "meetup" in comm_name_lower or "game" in comm_name_lower:
                bonus += 10
        elif "master" in student_type:
            if "startup" in comm_name_lower or "ai" in comm_name_lower or "professional" in comm_desc_lower:
                bonus += 10
                
        score += bonus
        
        # Clamp score between 0 and 100
        final_score = int(min(100, max(0, score)))
        
        scored_communities.append({
            "community": comm,
            "match_score": final_score
        })
        
    # Sort by match_score descending
    scored_communities.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Return top 3 matches
    return scored_communities[:3]
