import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
from nba_api.stats.endpoints import shotchartdetail
import time


class NBADataScraper:
    def __init__(self, cache_dir="nba_cache"):
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        
        # Top 100 players list with their accurate NBA API player IDs for 2024-25 season
        self.top_100_players = {
            "Aaron Gordon": 203932,
            "Al Horford": 201143,
            "Alperen Sengun": 1630578,
            "Amen Thompson": 1630602,
            "Anthony Davis": 203076,
            "Anthony Edwards": 1630162,
            "Austin Reaves": 1630559,
            "Bam Adebayo": 1628389,
            "Bradley Beal": 203078,
            "Brandon Ingram": 1627742,
            "Brandon Miller": 1641458,
            "Brook Lopez": 201572,
            "Cade Cunningham": 1630595,
            "Cam Thomas": 1630216,
            "Chet Holmgren": 1641751,
            "Chris Paul": 101108,
            "CJ McCollum": 203468,
            "Coby White": 1629632,
            "Damian Lillard": 203081,
            "Daniel Gafford": 1629657,
            "Darius Garland": 1629636,
            "De'Aaron Fox": 1628368,
            "Dereck Lively II": 1641854,
            "Derrick White": 1628401,
            "Desmond Bane": 1630217,
            "Devin Booker": 1626164,
            "Dillon Brooks": 1628415,
            "Domantas Sabonis": 1627734,
            "Donovan Mitchell": 1628378,
            "Draymond Green": 203110,
            "Evan Mobley": 1630596,
            "Franz Wagner": 1630532,
            "Fred VanVleet": 1627832,
            "Giannis Antetokounmpo": 203507,
            "Gradey Dick": 1641705,
            "Grayson Allen": 1628960,
            "Herbert Jones": 1630573,
            "Immanuel Quickley": 1630193,
            "Isaiah Hartenstein": 1628392,
            "Ja Morant": 1629630,
            "Jabari Smith Jr.": 1630596,
            "Jaden McDaniels": 1630165,
            "Jaime Jaquez Jr.": 1641735,
            "Jalen Brunson": 1628973,
            "Jalen Duren": 1630583,
            "Jalen Green": 1630224,
            "Jalen Johnson": 1630550,
            "Jalen Suggs": 1630591,
            "Jalen Williams": 1630554,
            "Jamal Murray": 1627750,
            "Jaren Jackson Jr.": 1628991,
            "Jarrett Allen": 1628386,
            "Jason Tatum": 1628369,
            "Jaylen Brown": 1627759,
            "Jayson Tatum": 1628369,
            "Jerami Grant": 203924,
            "Jericho Sims": 1630595,
            "Jimmy Butler": 202710,
            "Jock Landale": 1629677,
            "Joel Embiid": 203954,
            "Jonas Valanciunas": 202685,
            "Jonathan Kuminga": 1630228,
            "Jordan Poole": 1629673,
            "Josh Giddey": 1630581,
            "Josh Green": 1630193,
            "Josh Hart": 1628404,
            "Julius Randle": 203944,
            "Karl-Anthony Towns": 1626157,
            "Kawhi Leonard": 202695,
            "Keegan Murray": 1630568,
            "Kentavious Caldwell-Pope": 203484,
            "Kevin Durant": 201142,
            "Khris Middleton": 203114,
            "Klay Thompson": 202691,
            "Kristaps Porzingis": 204001,
            "Kyle Kuzma": 1628398,
            "Kyrie Irving": 202681,
            "Lauri Markkanen": 1628374,
            "LeBron James": 2544,
            "Luka Dončić": 1629029,
            "Luguentz Dort": 1629216,
            "Malik Monk": 1627774,
            "Marcus Smart": 203935,
            "Mark Williams": 1630576,
            "Michael Porter Jr.": 1629718,
            "Mikal Bridges": 1628969,
            "Mike Conley": 201144,
            "Mitchell Robinson": 1629011,
            "Myles Turner": 1626167,
            "Naz Reid": 1630222,
            "Nikola Jokić": 203999,
            "Nikola Vučević": 202696,
            "Norman Powell": 1626181,
            "OG Anunoby": 1628384,
            "Paolo Banchero": 1630596,
            "Pascal Siakam": 1627783,
            "Paul George": 202331,
            "Reed Sheppard": 1641742,
            "RJ Barrett": 1629628,
            "Rudy Gobert": 203497,
            "Russell Westbrook": 201566,
            "Scottie Barnes": 1630567,
            "Shai Gilgeous-Alexander": 1628983,
            "Stephen Curry": 201939,
            "Trae Young": 1629027,
            "Tyler Herro": 1629639,
            "Tyrese Haliburton": 1630169,
            "Tyrese Maxey": 1630178,
            "Victor Wembanyama": 1641705,
            "Zach LaVine": 203897,
            "Zion Williamson": 1629627
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
    
    # Print available players
    players = scraper.get_player_list()
    print(f"Available players: {len(players)}")
    print("First 5 players:", players[:5])