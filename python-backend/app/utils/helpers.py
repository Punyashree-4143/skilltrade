import math
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import re
from geopy.distance import geodesic


def calculate_distance(coords1: List[float], coords2: List[float]) -> float:
    """
    Calculate distance between two coordinates in kilometers.
    
    Args:
        coords1: [longitude, latitude] for first point
        coords2: [longitude, latitude] for second point
    
    Returns:
        Distance in kilometers
    """
    try:
        # Use geopy for accurate distance calculation
        point1 = (coords1[1], coords1[0])  # (lat, lon)
        point2 = (coords2[1], coords2[0])  # (lat, lon)
        
        distance = geodesic(point1, point2).kilometers
        return round(distance, 2)
        
    except Exception:
        # Fallback to Haversine formula
        return haversine_distance(coords1, coords2)


def haversine_distance(coords1: List[float], coords2: List[float]) -> float:
    """
    Calculate distance using Haversine formula.
    
    Args:
        coords1: [longitude, latitude] for first point
        coords2: [longitude, latitude] for second point
    
    Returns:
        Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert coordinates to radians
    lon1, lat1 = math.radians(coords1[0]), math.radians(coords1[1])
    lon2, lat2 = math.radians(coords2[0]), math.radians(coords2[1])
    
    # Differences
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return round(distance, 2)


def calculate_match_score(
    user1_offers: List[str], 
    user1_wants: List[str],
    user2_offers: List[str], 
    user2_wants: List[str],
    user2_rating: float = 0.0,
    distance: Optional[float] = None,
    max_distance: float = 50.0
) -> float:
    """
    Calculate skill matching score between two users.
    
    Args:
        user1_offers: Skills user 1 can teach
        user1_wants: Skills user 1 wants to learn
        user2_offers: Skills user 2 can teach
        user2_wants: Skills user 2 wants to learn
        user2_rating: User 2's rating (0-5)
        distance: Distance between users in km
        max_distance: Maximum distance for scoring
    
    Returns:
        Match score (0-100)
    """
    score = 0.0
    
    # Convert to lowercase for comparison
    user1_offers_lower = [skill.lower() for skill in user1_offers]
    user1_wants_lower = [skill.lower() for skill in user1_wants]
    user2_offers_lower = [skill.lower() for skill in user2_offers]
    user2_wants_lower = [skill.lower() for skill in user2_wants]
    
    # Direct match: user1 offers what user2 wants AND user2 offers what user1 wants
    direct_match = (
        any(offer in user2_wants_lower for offer in user1_offers_lower) and
        any(offer in user1_wants_lower for offer in user2_offers_lower)
    )
    
    if direct_match:
        score += 50.0
    
    # Partial matches
    user1_to_user2_match = any(offer in user2_wants_lower for offer in user1_offers_lower)
    user2_to_user1_match = any(offer in user1_wants_lower for offer in user2_offers_lower)
    
    if user1_to_user2_match:
        score += 25.0
    if user2_to_user1_match:
        score += 25.0
    
    # Rating factor (0-25 points)
    score += min(user2_rating, 5.0) * 5.0
    
    # Distance factor (0-25 points, closer is better)
    if distance is not None:
        distance_score = max(0.0, 25.0 * (1.0 - distance / max_distance))
        score += distance_score
    
    return min(100.0, round(score))


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format (basic validation)"""
    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's mostly digits and reasonable length
    pattern = r'^\+?[1-9]\d{6,14}$'
    return re.match(pattern, cleaned) is not None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    
    return filename


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def time_ago(dt: datetime) -> str:
    """Get human readable time ago string"""
    now = datetime.utcnow()
    diff = now - dt
    
    minutes = int(diff.total_seconds() / 60)
    hours = int(diff.total_seconds() / 3600)
    days = int(diff.total_seconds() / 86400)
    
    if minutes < 1:
        return "just now"
    elif minutes < 60:
        return f"{minutes}m ago"
    elif hours < 24:
        return f"{hours}h ago"
    elif days < 7:
        return f"{days}d ago"
    else:
        return dt.strftime("%b %d")


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    
    # Replace spaces and special characters
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    if len(slug) > 50:
        slug = slug[:50].rstrip('-')
    
    return slug


def paginate_query(
    page: int = 1, 
    limit: int = 20, 
    max_limit: int = 100
) -> Tuple[int, int]:
    """
    Calculate skip and limit for pagination.
    
    Args:
        page: Page number (1-based)
        limit: Items per page
        max_limit: Maximum allowed items per page
    
    Returns:
        Tuple of (skip, limit)
    """
    # Validate and normalize inputs
    page = max(1, page)
    limit = min(max(1, limit), max_limit)
    
    skip = (page - 1) * limit
    
    return skip, limit


def calculate_pagination_info(
    total: int, 
    page: int, 
    limit: int
) -> dict:
    """
    Calculate pagination information.
    
    Args:
        total: Total number of items
        page: Current page (1-based)
        limit: Items per page
    
    Returns:
        Dictionary with pagination info
    """
    pages = (total + limit - 1) // limit  # Ceiling division
    
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
        "next_page": page + 1 if page < pages else None,
        "prev_page": page - 1 if page > 1 else None
    }


def extract_skills_from_text(text: str) -> List[str]:
    """Extract potential skills from text using basic patterns"""
    # Common skill keywords and patterns
    skill_patterns = [
        r'\b(javascript|python|react|vue|angular|node\.js|express|django|flask)\b',
        r'\b(guitar|piano|violin|drums|singing|music)\b',
        r'\b(spanish|french|german|chinese|japanese|english)\b',
        r'\b(photography|design|illustration|photoshop|illustrator)\b',
        r'\b(marketing|sales|business|finance|accounting)\b',
        r'\b(yoga|meditation|fitness|nutrition|cooking)\b'
    ]
    
    skills = set()
    text_lower = text.lower()
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        skills.update(matches)
    
    return list(skills)


def is_valid_coordinate(coords: List[float]) -> bool:
    """Validate geographic coordinates"""
    if len(coords) != 2:
        return False
    
    longitude, latitude = coords
    
    # Longitude: -180 to 180
    # Latitude: -90 to 90
    return (-180 <= longitude <= 180) and (-90 <= latitude <= 90)
