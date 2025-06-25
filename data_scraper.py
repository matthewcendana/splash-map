import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
from nba_api.stats.endpoints import shotchartdetail, commonallplayers
import time
import requests
from PIL import Image
from io import BytesIO


class NBADataScraper:
    def __init__(self, cache_dir="nba_cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        
        # Top 100 players list with their NBA API player IDs
        self.top_100_players = {
            "Al Horford": 201143,
            "Alex Caruso": 1628294,
            "Alperen Sengun": 1630578,
            "Amen Thompson": 1641705,
            "Andrew Wiggins": 203952,
            "Anfernee Simons": 1629014,
            "Anthony Davis": 203076,
            "Austin Reaves": 1630559,
            "Bradley Beal": 203078,
            "Brandon Miller": 1641458,
            "Brandin Podziemski": 1641712,
            "Brook Lopez": 201572,
            "Cade Cunningham": 1630595,
            "Chet Holmgren": 1641705,
            "Chris Paul": 101108,
            "CJ McCollum": 203468,
            "Coby White": 1629632,
            "Damian Lillard": 203081,
            "Darius Garland": 1629636,
            "Dereck Lively II": 1641854,
            "Desmond Bane": 1630217,
            "Devin Booker": 1626164,
            "Dillon Brooks": 1628415,
            "Donte DiVincenzo": 1628978,
            "Donovan Mitchell": 1628378,
            "Draymond Green": 203110,
            "Franz Wagner": 1630532,
            "Fred VanVleet": 1627832,
            "Giannis Antetokounmpo": 203507,
            "Herbert Jones": 1630573,
            "Immanuel Quickley": 1630193,
            "Isaiah Hartenstein": 1628392,
            "Ja Morant": 1629630,
            "Jabari Smith Jr.": 1630596,
            "Jaden McDaniels": 1630165,
            "Jaime Jaquez Jr.": 1641705,
            "Jalen Brunson": 1628973,
            "Jalen Green": 1630224,
            "Jalen Suggs": 1630591,
            "Jamal Murray": 1627750,
            "Jaren Jackson Jr.": 1628991,
            "Jarrett Allen": 1628386,
            "Jayson Tatum": 1628369,
            "Jerami Grant": 203924,
            "Jimmy Butler": 202710,
            "Joel Embiid": 203954,
            "Jonas Valanciunas": 202685,
            "Josh Hart": 1628404,
            "Julius Randle": 203944,
            "Karl-Anthony Towns": 1626157,
            "Kawhi Leonard": 202695,
            "Keegan Murray": 1630568,
            "Kentavious Caldwell-Pope": 203484,
            "Khris Middleton": 203114,
            "Klay Thompson": 202691,
            "LeBron James": 2544,
            "Luka Dončić": 1629029,
            "Luguentz Dort": 1629216,
            "Malik Monk": 1627774,
            "Marcus Smart": 203935,
            "Michael Porter Jr.": 1629718,
            "Mikal Bridges": 1628969,
            "Mike Conley": 201144,
            "Mitchell Robinson": 1629011,
            "Myles Turner": 1626167,
            "Naz Reid": 1630222,
            "Nikola Jokić": 203999,
            "Norman Powell": 1626181,
            "OG Anunoby": 1628384,
            "Pascal Siakam": 1627783,
            "Paul George": 202331,
            "RJ Barrett": 1629628,
            "Rudy Gobert": 203497,
            "Shai Gilgeous-Alexander": 1628983,
            "Stephen Curry": 201939,
            "Trae Young": 1629027,
            "Tyler Herro": 1629639,
            "Tyrese Haliburton": 1630169,
            "Zach LaVine": 203897
        }
    
    def ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_path(self, player_id, season, data_type="shots"):
        """Generate cache file path"""
        return os.path.join(self.cache_dir, f"{player_id}_{season}_{data_type}.pkl")
    
    def is_cache_valid(self, cache_path, max_age_hours=24):
        """Check if cache file exists and is recent enough"""
        if not os.path.exists(cache_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        return datetime.now() - file_time < timedelta(hours=max_age_hours)
    
    def get_player_shot_data(self, player_id, season="2024-25", season_type="Regular Season"):
        """
        Fetch shot data for a specific player with caching
        
        Parameters:
        -----------
        player_id : int
            NBA API player ID
        season : str
            NBA season (e.g., "2024-25")
        season_type : str
            Season type ("Regular Season", "Playoffs", etc.)
            
        Returns:
        --------
        pd.DataFrame : Shot data for the player
        """
        cache_path = self.get_cache_path(player_id, season)
        
        # Try to load from cache first
        if self.is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Cache read error for player {player_id}: {e}")
        
        # Fetch fresh data from API
        try:
            print(f"Fetching shot data for player ID {player_id}...")
            df = shotchartdetail.ShotChartDetail(
                team_id=0,
                player_id=player_id,
                season_nullable=season,
                season_type_all_star=season_type,
                context_measure_simple="FGA"
            ).get_data_frames()[0]
            
            # Cache the data
            with open(cache_path, 'wb') as f:
                pickle.dump(df, f)
            
            print(f"Cached shot data for player ID {player_id}")
            time.sleep(0.6)  # Rate limiting
            return df
            
        except Exception as e:
            print(f"Error fetching shot data for player {player_id}: {e}")
            return pd.DataFrame()
    
    def get_player_headshot(self, player_id, size=(90, 90)):
        """
        Fetch and resize player headshot with caching
        
        Parameters:
        -----------
        player_id : int
            NBA API player ID
        size : tuple
            Target size for the image (width, height)
            
        Returns:
        --------
        PIL.Image or None : Resized player headshot
        """
        cache_path = self.get_cache_path(player_id, "headshot", "image")
        
        # Try to load from cache first
        if self.is_cache_valid(cache_path, max_age_hours=168):  # Cache images for a week
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Image cache read error for player {player_id}: {e}")
        
        # Fetch fresh image from NBA CDN
        try:
            url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Open and resize image
                img = Image.open(BytesIO(response.content))
                img = img.resize(size, Image.Resampling.LANCZOS)
                
                # Cache the resized image
                with open(cache_path, 'wb') as f:
                    pickle.dump(img, f)
                
                return img
            else:
                print(f"Failed to fetch headshot for player {player_id}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching headshot for player {player_id}: {e}")
            return None
    
    def get_player_list(self):
        """
        Get sorted list of available players
        
        Returns:
        --------
        list : Sorted list of player names
        """
        return sorted(self.top_100_players.keys())
    
    def get_player_id(self, player_name):
        """
        Get player ID from player name
        
        Parameters:
        -----------
        player_name : str
            Player's full name
            
        Returns:
        --------
        int or None : Player ID if found, None otherwise
        """
        return self.top_100_players.get(player_name)
    
    def clear_cache(self, player_id=None, older_than_days=7):
        """
        Clear cache files
        
        Parameters:
        -----------
        player_id : int, optional
            Clear cache for specific player only
        older_than_days : int
            Clear files older than this many days
        """
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.pkl'):
                file_path = os.path.join(self.cache_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                # Check if we should delete this file
                should_delete = False
                
                if player_id is not None:
                    # Delete specific player's cache
                    if filename.startswith(f"{player_id}_"):
                        should_delete = True
                else:
                    # Delete old files
                    if file_time < cutoff_time:
                        should_delete = True
                
                if should_delete:
                    try:
                        os.remove(file_path)
                        print(f"Deleted cache file: {filename}")
                    except Exception as e:
                        print(f"Error deleting {filename}: {e}")


if __name__ == "__main__":
    # Test the scraper
    scraper = NBADataScraper()
    
    # Test with Stephen Curry
    curry_id = scraper.get_player_id("Stephen Curry")
    if curry_id:
        print(f"Stephen Curry ID: {curry_id}")
        
        # Get shot data
        shot_data = scraper.get_player_shot_data(curry_id, "2024-25")
        print(f"Shot data shape: {shot_data.shape}")
        
        # Get headshot
        headshot = scraper.get_player_headshot(curry_id)
        if headshot:
            print(f"Headshot size: {headshot.size}")
    
    # Print available players
    players = scraper.get_player_list()
    print(f"Available players: {len(players)}")
    print("First 5 players:", players[:5])