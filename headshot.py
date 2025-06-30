import os
import requests
from PIL import Image
from io import BytesIO


class HeadshotManager:
    def __init__(self, headshots_dir="static/headshots"):
        self.headshots_dir = headshots_dir
        self.ensure_headshots_dir()
    
    def ensure_headshots_dir(self):
        """Create headshots directory if it doesn't exist"""
        if not os.path.exists(self.headshots_dir):
            os.makedirs(self.headshots_dir)
    
    def get_headshot_path(self, player_id):
        """Get the file path for a player's headshot"""
        return os.path.join(self.headshots_dir, f"{player_id}.jpg")
    
    def download_headshot(self, player_id):
        """
        Download and save player headshot
        
        Parameters:
        -----------
        player_id : int
            NBA API player ID
            
        Returns:
        --------
        str or None : File path if successful, None if failed
        """
        file_path = self.get_headshot_path(player_id)
        
        # Skip if already exists
        if os.path.exists(file_path):
            return file_path
        
        # Try to download from NBA API
        url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Open and convert image
                img = Image.open(BytesIO(response.content))
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    else:
                        img = img.convert('RGB')
                
                # Save as JPEG
                img.save(file_path, 'JPEG', quality=90)
                print(f"Downloaded headshot for player {player_id}")
                return file_path
                
        except Exception as e:
            print(f"Error downloading headshot for player {player_id}: {e}")
        
        return None
    
    def get_headshot(self, player_id):
        """
        Get player headshot (download if not exists)
        
        Parameters:
        -----------
        player_id : int
            NBA API player ID
            
        Returns:
        --------
        str or None : File path if available, None if not found
        """
        file_path = self.get_headshot_path(player_id)
        
        # Return existing file
        if os.path.exists(file_path):
            return file_path
        
        # Try to download
        return self.download_headshot(player_id)