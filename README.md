# hackatoggl
or the more boring name, Hackatime to Toggl Track Sync. An automated Python script that fetches your daily coding summary from Hackatime and creates corresponding time entries under a hackatime project in Toggl Track. I made this cus unlike my homework (which i mainly use toggl for),, coding is something im fine with procrestinating in, and pausing the entry every time rly isn't fun. I also need an excuse to try out github actions, which I apparently have access to through the github student developer pack.    

# Installation
clone the repo, then (preferably in a venv) run:
```
pip install -r reqirements.txt
```
dill in ur .env and keep it super secret.   

# Usage
By default, running:
```
python sync.py
```
will grab yesterdays entries. append YYYY-MM-DD or 'today' to get the respective entries. e.g.
```
python sync.py 2026-10-10
```