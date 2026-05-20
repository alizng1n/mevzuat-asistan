import httpx

UBOM_BASE_URL = "https://ubom.iste.edu.tr"

def ubom_login(username, password):
    """
    UBOM sistemine Moodle Mobile App servisi üzerinden giriş yapar ve token döner.
    """
    params = {
        "username": username,
        "password": password,
        "service": "moodle_mobile_app"
    }
    try:
        # url parameter must be properly encoded, httpx handles this in params
        response = httpx.get(f"{UBOM_BASE_URL}/login/token.php", params=params, timeout=10)
        data = response.json()
        
        if "token" in data:
            return data["token"]
        elif "error" in data:
            raise Exception(data["error"])
        else:
            raise Exception("UBOM giriş hatası: Beklenmeyen yanıt formatı.")
    except Exception as e:
        raise Exception(f"UBOM bağlantı hatası: {str(e)}")

def fetch_ubom_deadlines(token):
    """
    Moodle token kullanarak içinde bulunduğumuz ayın tüm etkinliklerini çeker (geçmiş günler dahil).
    """
    from datetime import datetime
    now = datetime.now()
    params = {
        "wstoken": token,
        "wsfunction": "core_calendar_get_calendar_monthly_view",
        "moodlewsrestformat": "json",
        "year": now.year,
        "month": now.month
    }
    
    try:
        response = httpx.post(f"{UBOM_BASE_URL}/webservice/rest/server.php", data=params, timeout=15)
        data = response.json()
        
        if "exception" in data:
            raise Exception(data.get("message", "Moodle API hatası"))
            
        events = []
        # Flatten the weeks -> days -> events structure
        for week in data.get("weeks", []):
            for day in week.get("days", []):
                for ev in day.get("events", []):
                    # Prevent duplicates if any
                    if not any(e.get("id") == ev.get("id") for e in events):
                        events.append(ev)
        
        deadlines = []
        for ev in events:
            dt = datetime.fromtimestamp(ev.get("timestart", 0))
            
            deadlines.append({
                "id": ev.get("id"),
                "name": ev.get("name"),
                "description": ev.get("description", ""),
                "url": ev.get("url", ""),
                "timestart": ev.get("timestart"),
                "deadline": dt.isoformat(),
                "course_name": ev.get("course", {}).get("fullname", ""),
                "eventtype": ev.get("eventtype", "")
            })
            
        # Sort by timestart ascending
        deadlines.sort(key=lambda x: x["timestart"])
        return deadlines
    except Exception as e:
        raise Exception(f"UBOM etkinlikleri alınamadı: {str(e)}")
