# Splash Map

**Live Demo:** [https://splash-map.streamlit.app/](https://splash-map.streamlit.app/)

Splash Map is an interactive Streamlit dashboard that generates shot-selection heatmaps for each of the NBA’s Top 100 players from the 2024–25 regular season.

## Features

- Retrieves live shot-attempt data via `nba_api`.
- Uses kernel-density estimation to draw a clean, black-background half-court with transparent low-density zones.
- Allows selection of any of the Top 100 players (pre-mapped to NBA.com player IDs) to instantly view their heatmap.

## Main Files

### `dashboard.py`

The entry point of the application. It initializes the Streamlit interface, loads player data, and renders the heatmap visualization.

### `data_scraper.py`

Handles the retrieval of live shot-attempt data using the `nba_api`. It processes the data to be used in the heatmap generation.

### `headshot.py`

Manages the retrieval and display of player headshots. It ensures that each player's image is correctly fetched and displayed alongside their heatmap.

### `heatmap.py`

Contains the logic for generating the shot-selection heatmap. It utilizes kernel-density estimation to create a visual representation of a player's shot attempts.

## Screenshots

![Dashboard View](https://github.com/matthewcendana/splash-map/blob/76697af231826321833ffe61ac0e7afac31cd1c6/dashboard.png)  
*Dashboard showing player selection and overall layout.*

![Heatmap Example](https://github.com/matthewcendana/splash-map/blob/76697af231826321833ffe61ac0e7afac31cd1c6/heatmap.png)  
*Example of a player’s shot heatmap.*

![Show Location Map Example](https://github.com/matthewcendana/splash-map/blob/76697af231826321833ffe61ac0e7afac31cd1c6/shot_location_map.png) 
*Example of a player’s shot location map.*

## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/matthewcendana/splash-map.git
cd splash-map
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run dashboard.py


