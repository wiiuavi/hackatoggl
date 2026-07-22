import os
import sys
import base64
import requests
from datetime import datetime, timedelta, timezone

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

hackatimeUserId = os.getenv("HACKATIME_USER_ID")
togglApiToken = os.getenv("TOGGL_API_TOKEN")

targetTogglProject = "hackatime"

togglApiBase = "https://api.track.toggl.com/api/v9"
hackatimeApiBase = "https://hackatime.hackclub.com/api"

def getTogglHeaders():
    authString = f"{togglApiToken}:api_token".encode("ascii")
    authBase64 = base64.b64encode(authString).decode("ascii")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Basic {authBase64}"
    }

def getWorkspaceId():
    response = requests.get(f"{togglApiBase}/workspaces", headers=getTogglHeaders())
    response.raise_for_status()
    
    workspaces = response.json()
    if not workspaces:
        raise ValueError("No Toggl workspaces found on this account.")
    
    return workspaces[0]["id"]

def getOrCreateProject(workspaceId):
    response = requests.get(f"{togglApiBase}/workspaces/{workspaceId}/projects", headers=getTogglHeaders())
    response.raise_for_status()
    projects = response.json()
    
    for proj in projects:
        if proj.get("name", "").lower() == targetTogglProject.lower():
            return proj["id"]
            
    print(f"Project '{targetTogglProject}' not found in Toggl. Creating it...")
    payload = {
        "active": True,
        "name": targetTogglProject,
        "workspace_id": workspaceId
    }
    response = requests.post(f"{togglApiBase}/workspaces/{workspaceId}/projects", json=payload, headers=getTogglHeaders())
    response.raise_for_status()
    return response.json()["id"]

def getHackatimeSummary(targetDate):
    dateStr = targetDate.strftime("%Y-%m-%d")
    url = f"{hackatimeApiBase}/summary?user_id={hackatimeUserId}&start={dateStr}&end={dateStr}"
    
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def createTogglTimeEntry(workspaceId, projectId, description, durationSeconds, startTime):
    payload = {
        "billable": False,
        "created_with": "Hackatime-Sync-Script",
        "description": description,
        "duration": durationSeconds,
        "start": startTime.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_id": projectId,
        "workspace_id": workspaceId
    }
    
    response = requests.post(
        f"{togglApiBase}/workspaces/{workspaceId}/time_entries",
        json=payload,
        headers=getTogglHeaders()
    )
    
    if response.status_code not in (200, 201):
        print(f"Failed to create Toggl entry for {description}: {response.text}")
    else:
        print(f" -> Successfully logged {durationSeconds} seconds for '{description}'")

def main():
    if not hackatimeUserId or not togglApiToken:
        print("Error: HACKATIME_USER_ID and TOGGL_API_TOKEN environment variables must be set.")
        sys.exit(1)

    targetDate = datetime.now(timezone.utc) - timedelta(days=1)
    
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "today":
            targetDate = datetime.now(timezone.utc)
        else:
            try:
                targetDate = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                print("Error: Invalid date format. Use YYYY-MM-DD or 'today'.")
                sys.exit(1)

    dateStr = targetDate.strftime('%Y-%m-%d')
    print(f"=== Syncing Hackatime stats for {dateStr} ===")
    
    try:
        summary = getHackatimeSummary(targetDate)
        projects = summary.get("projects", [])
        
        if not projects:
            print(f"No coding activity found on Hackatime for {dateStr}.")
            return

        print("Authenticating with Toggl...")
        workspaceId = getWorkspaceId()
        projectId = getOrCreateProject(workspaceId)
        
        print("Creating time entries...")
        
        currentEntryStart = targetDate.replace(hour=9, minute=0, second=0, microsecond=0)
        
        for proj in projects:
            desc = proj.get("key", "Unknown Project")
            duration = int(proj.get("total", 0))
            
            if duration > 0:
                createTogglTimeEntry(workspaceId, projectId, desc, duration, currentEntryStart)
                currentEntryStart += timedelta(seconds=duration)
                
        print("=== Sync Complete ===")

    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()