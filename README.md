# hackatoggl
or the more boring name, Hackatime to Toggl Track Sync. An automated Python script that fetches your daily coding summary from Hackatime and creates corresponding time entries under a hackatime project in Toggl Track. I made this cus unlike my homework (which i mainly use toggl for),, coding is something im fine with procrestinating in, and pausing the entry every time rly isn't fun. I also need an excuse to try out github actions, which I apparently have access to through the github student developer pack.    
Here it is in action:  



https://github.com/user-attachments/assets/9d1bf14a-e21d-4984-99fe-91eed3f0588d



# Installation
Either download and run sync.exe in releases (WINDOWS ONLY, _and can only fetch yesterday's entries_) or...  
clone the repo, then (preferably in a venv) run:
```
pip install -r reqirements.txt
```
fill in ur .env and keep it super secret.   

# Usage
By default, running:
```
python sync.py
```
will grab yesterday's entries. append YYYY-MM-DD or 'today' to get the respective entries. e.g.
```
python sync.py 2026-10-10
```

# Automation  
Please keep in mind there are limits to github actions you may have already used up.  
To run this every day, clone the repo (PRIVATE) and dont worry about uploading a .env file.  
Go to the repo settings -->  secrets and variables --> actions.
Add new repo secrets ```HACKATIME_USER_ID``` and  ```TOGGL_API_TOKEN```.  I haven't tested this yet, but it should work.  
If not, create a file called sync.yml in .github/workflows with the contents:
```
name: Daily Hackatime to Toggl Sync

on:
  schedule:
    - cron: '0 2 * * *' # run daily at like 2 am some timezone
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run sync script
        env:
          HACKATIME_USER_ID: ${{ secrets.HACKATIME_USER_ID }}
          TOGGL_API_TOKEN: ${{ secrets.TOGGL_API_TOKEN }}
        run: python sync.py

```
