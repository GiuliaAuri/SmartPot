from datetime import datetime


def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    if not timestamp_str:
        return "N/A"
    
    try:
        # Try to parse as Unix timestamp first
        if timestamp_str.isdigit():
            dt = datetime.fromtimestamp(int(timestamp_str))
            return dt.strftime("%H:%M")
        
        # Try to parse ISO format timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%H:%M")
    except:
        return timestamp_str
