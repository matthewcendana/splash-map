# Splash Map

**Status: Work in Progress** – Splash Map is an interactive Streamlit dashboard that generates shot-selection heatmaps for each of the NBA’s Top 100 players from the 2024-25 regular season.

## What It Does
- Retrieves live shot-attempt data via `nba_api`.
- Uses kernel-density estimation to draw a clean, black-background half-court with transparent low-density zones.
- Lets you choose any of the Top 100 players (pre-mapped to NBA.com player IDs) and instantly view their heatmap.


