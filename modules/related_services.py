"""
Related Services Tracking Dashboard for SPARK
Summary view of all students' related services with minutes tracking.
"""

import json
import os
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SERVICES_DIR = os.path.join(DATA_DIR, 'related_services')


def ensure_services_dir():
    """Ensure the services data directory exists."""
    os.makedirs(SERVICES_DIR, exist_ok=True)


# Standard related service types
SERVICE_TYPES = [
    "Speech/Language Therapy",
    "Occupational Therapy",
    "Physical Therapy",
    "Behavioral Services",
    "Vision Services",
    "Hearing/Audiology",
    "Counseling",
    "Adapted PE",
    "Assistive Technology",
    "Transportation",
    "Nursing Services",
    "Other",
]


def get_student_services(student_id):
    """Get all related services for a student."""
    ensure_services_dir()
    filepath = os.path.join(SERVICES_DIR, f"{student_id}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {"services": [], "log": []}


def save_student_services(student_id, data):
    """Save related services configuration for a student."""
    ensure_services_dir()
    filepath = os.path.join(SERVICES_DIR, f"{student_id}.json")
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def add_service(student_id, service_type, provider_name, frequency, minutes_per_session, notes=""):
    """Add a related service to a student.
    
    Args:
        student_id: Student identifier
        service_type: Type from SERVICE_TYPES
        provider_name: Name of the provider
        frequency: e.g., "2x/week", "1x/month", "30 min/week"
        minutes_per_session: Integer minutes
        notes: Optional notes
    """
    data = get_student_services(student_id)
    
    service = {
        "id": f"svc_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "type": service_type,
        "provider": provider_name,
        "frequency": frequency,
        "minutes_per_session": minutes_per_session,
        "required_minutes_monthly": _calculate_monthly_minutes(frequency, minutes_per_session),
        "notes": notes,
        "active": True,
        "added_date": datetime.now().strftime("%Y-%m-%d"),
    }
    
    data["services"].append(service)
    save_student_services(student_id, data)
    return service


def log_session(student_id, service_id, date, minutes_delivered, notes=""):
    """Log a delivered service session.
    
    Args:
        student_id: Student identifier
        service_id: Service identifier
        date: Date of session (YYYY-MM-DD)
        minutes_delivered: Actual minutes delivered
        notes: Optional session notes
    """
    data = get_student_services(student_id)
    
    entry = {
        "service_id": service_id,
        "date": date,
        "minutes": minutes_delivered,
        "notes": notes,
        "logged_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    
    data["log"].append(entry)
    save_student_services(student_id, data)
    return entry


def get_monthly_summary(student_id, year=None, month=None):
    """Get a monthly summary of service delivery vs requirements.
    
    Returns dict with per-service delivered vs required minutes.
    """
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    data = get_student_services(student_id)
    
    summary = []
    for service in data.get("services", []):
        if not service.get("active", True):
            continue
        
        # Calculate delivered minutes this month
        delivered = 0
        for entry in data.get("log", []):
            if entry.get("service_id") == service.get("id"):
                entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
                if entry_date.year == year and entry_date.month == month:
                    delivered += entry.get("minutes", 0)
        
        required = service.get("required_minutes_monthly", 0)
        
        # Determine status
        if delivered >= required:
            status = "on_track"
        elif delivered >= required * 0.75:
            status = "warning"
        else:
            status = "behind"
        
        summary.append({
            "service_id": service.get("id"),
            "type": service.get("type"),
            "provider": service.get("provider"),
            "frequency": service.get("frequency"),
            "required_monthly": required,
            "delivered_monthly": delivered,
            "remaining": max(0, required - delivered),
            "percent_complete": round((delivered / required * 100) if required > 0 else 0, 1),
            "status": status,
        })
    
    return summary


def get_dashboard_data(students):
    """Get dashboard-level overview of all students' services.
    
    Args:
        students: List of student dicts
    
    Returns:
        dict with overall stats and per-student summaries
    """
    now = datetime.now()
    dashboard = {
        "month": now.strftime("%B %Y"),
        "total_students": len(students),
        "students_with_services": 0,
        "total_services": 0,
        "alerts": [],
        "student_summaries": [],
    }
    
    for student in students:
        student_id = student.get("id", "")
        services_data = get_student_services(student_id)
        active_services = [s for s in services_data.get("services", []) if s.get("active", True)]
        
        if active_services:
            dashboard["students_with_services"] += 1
            dashboard["total_services"] += len(active_services)
            
            monthly = get_monthly_summary(student_id, now.year, now.month)
            
            student_summary = {
                "name": student.get("name", "Unknown"),
                "student_id": student_id,
                "service_count": len(active_services),
                "services": monthly,
            }
            
            # Check for alerts
            for svc in monthly:
                if svc["status"] == "behind":
                    dashboard["alerts"].append({
                        "student": student.get("name", "Unknown"),
                        "service": svc["type"],
                        "provider": svc["provider"],
                        "delivered": svc["delivered_monthly"],
                        "required": svc["required_monthly"],
                        "message": f"{student.get('name', 'Student')} - {svc['type']}: {svc['delivered_monthly']}/{svc['required_monthly']} minutes delivered"
                    })
            
            dashboard["student_summaries"].append(student_summary)
    
    return dashboard


def get_service_types():
    """Return available service types."""
    return SERVICE_TYPES


def _calculate_monthly_minutes(frequency, minutes_per_session):
    """Estimate monthly required minutes from frequency string.
    
    Handles: "2x/week", "1x/week", "3x/month", "daily", etc.
    """
    freq_lower = frequency.lower().strip()
    
    if "/week" in freq_lower or "per week" in freq_lower:
        try:
            times = int(freq_lower.split("x")[0].strip())
            return times * minutes_per_session * 4  # ~4 weeks/month
        except (ValueError, IndexError):
            pass
    
    if "/month" in freq_lower or "per month" in freq_lower:
        try:
            times = int(freq_lower.split("x")[0].strip())
            return times * minutes_per_session
        except (ValueError, IndexError):
            pass
    
    if "daily" in freq_lower:
        return minutes_per_session * 20  # ~20 school days
    
    if "weekly" in freq_lower:
        return minutes_per_session * 4
    
    if "biweekly" in freq_lower or "bi-weekly" in freq_lower:
        return minutes_per_session * 2
    
    # Default: assume weekly
    return minutes_per_session * 4
