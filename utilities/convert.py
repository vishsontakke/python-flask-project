def secondsToTime(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    time = ""
    if hour:
        time += f"{hour}h "
    if minutes:
        time += f"{minutes:02d}m "
    if seconds:
        time += f"{seconds:02d}s"
    
    return time.strip()
