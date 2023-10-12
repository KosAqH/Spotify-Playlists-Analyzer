# Spotify playlist analyzer

A simple tool for visualizing summary of Spotify's playlist.

Made in Python v3.10.7. Used flask and plotly. List of packages required to run the app is in the requirements.txt file.

Used CSS framework Bulma: https://bulma.io/

Data source: Spotify API: https://developer.spotify.com/documentation/web-api

### Instruction
1. `git clone git@github.com:KosAqH/Spotify-Playlists-Analyzer.git`
2. `cd .\Spotify-Playlists-Analyzer\`
3. `python -m venv venv`
4. `.\venv\Scripts\activate`
5. `pip install -r .\requirements.txt`
6. `python .\webapp\run.py`
7. Create an app on Spotify developer page. Documentation: https://developer.spotify.com/documentation/web-api/concepts/apps
8. Create file `.env` in `Spotify-Playlists-Analyzer\webapp` directory. Retrieve client ID and client secret from settings page of your spotify app. Then put those informations in `.env` file (there is an example in repository: `Spotify-Playlists-Analyzer\webapp\.env.example`)
9. Change working directory to `Spotify-Playlists-Analyzer\`. Run app with command `python webapp\run.py`

>?Warning: for running notebooks from experiments directory you should also install notebook package

### Showcase
