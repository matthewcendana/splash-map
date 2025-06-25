import streamlit as st
import matplotlib.pyplot as plt
from data_scraper import NBADataScraper
from heatmap import ShotHeatmapGenerator
import pandas as pd
from PIL import Image


# Configure Streamlit page
st.set_page_config(
    page_title="NBA Shot Heatmap Dashboard",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px 0;
        color: #FF6B35;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .player-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stat-metric {
        text-align: center;
        padding: 10px;
        background-color: #e9ecef;
        border-radius: 5px;
        margin: 5px 0;
    }
    
    .stSelectbox > div > div > select {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data_scraper():
    """Load the data scraper with caching"""
    return NBADataScraper()


@st.cache_data
def load_heatmap_generator():
    """Load the heatmap generator with caching"""
    return ShotHeatmapGenerator()


@st.cache_data
def get_player_shot_data(player_id, season):
    """Get player shot data with caching"""
    scraper = load_data_scraper()
    return scraper.get_player_shot_data(player_id, season)


@st.cache_data
def get_player_headshot(player_id):
    """Get player headshot with caching"""
    scraper = load_data_scraper()
    return scraper.get_player_headshot(player_id)


def main():
    """Main dashboard function"""
    
    # Initialize components
    scraper = load_data_scraper()
    heatmap_gen = load_heatmap_generator()
    
    # Header
    st.markdown('<div class="main-header">🏀 NBA Shot Heatmap Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Sidebar for player selection
    with st.sidebar:
        st.header("Player Selection")
        
        # Get player list
        players = scraper.get_player_list()
        
        # Player dropdown
        selected_player = st.selectbox(
            "Choose a player:",
            players,
            index=players.index("Stephen Curry") if "Stephen Curry" in players else 0,
            help="Select any of the top 100 NBA players"
        )
        
        # Season selection (fixed to 2024-25 as requested)
        season = "2024-25"
        st.info(f"**Season:** {season} Regular Season")
        
        # Additional options
        st.subheader("Heatmap Options")
        
        resolution = st.slider(
            "Resolution", 
            min_value=50, 
            max_value=200, 
            value=150,
            help="Higher resolution = more detailed heatmap"
        )
        
        bandwidth = st.slider(
            "Smoothing", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.3, 
            step=0.1,
            help="Lower values = more detailed, higher values = smoother"
        )
        
        # Cache management
        st.subheader("Cache Management")
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
            st.rerun()
    
    # Main content area
    if selected_player:
        # Get player ID
        player_id = scraper.get_player_id(selected_player)
        
        if player_id:
            # Create columns for layout
            col1, col2 = st.columns([3, 1])
            
            with col2:
                # Player info card
                st.markdown('<div class="player-card">', unsafe_allow_html=True)
                st.subheader(selected_player)
                
                # Get and display player headshot
                with st.spinner("Loading player image..."):
                    headshot = get_player_headshot(player_id)
                    
                if headshot:
                    st.image(headshot, use_column_width=True)
                else:
                    st.info("Player image not available")
                
                # Player stats placeholder
                st.markdown("**Season:** 2024-25")
                st.markdown("**Data Source:** NBA.com")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col1:
                # Generate heatmap
                st.subheader(f"{selected_player} - Shot Heatmap")
                
                # Load shot data
                with st.spinner("Loading shot data..."):
                    shot_data = get_player_shot_data(player_id, season)
                
                if not shot_data.empty:
                    # Display shot statistics
                    total_shots = len(shot_data)
                    made_shots = len(shot_data[shot_data['SHOT_MADE_FLAG'] == 1])
                    fg_percentage = (made_shots / total_shots * 100) if total_shots > 0 else 0
                    
                    # Stats metrics
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        st.metric("Total Shots", f"{total_shots:,}")
                    
                    with metric_col2:
                        st.metric("Made Shots", f"{made_shots:,}")
                    
                    with metric_col3:
                        st.metric("FG%", f"{fg_percentage:.1f}%")
                    
                    # Generate heatmap
                    with st.spinner("Generating heatmap..."):
                        fig, ax = heatmap_gen.generate_heatmap_for_player(
                            player_id=player_id,
                            shot_data=shot_data,
                            player_name=selected_player,
                            season=season,
                            resolution=resolution,
                            bandwidth_factor=bandwidth
                        )
                        
                        # Display the heatmap
                        st.pyplot(fig, use_container_width=True)
                        
                        # Close the figure to free memory
                        plt.close(fig)
                    
                    # Additional shot data insights
                    with st.expander("Shot Data Breakdown"):
                        # Shot type breakdown
                        if 'SHOT_TYPE' in shot_data.columns:
                            shot_types = shot_data['SHOT_TYPE'].value_counts()
                            st.write("**Shot Types:**")
                            for shot_type, count in shot_types.items():
                                percentage = (count / total_shots * 100)
                                st.write(f"- {shot_type}: {count} shots ({percentage:.1f}%)")
                        
                        # Shot zone breakdown
                        if 'SHOT_ZONE_BASIC' in shot_data.columns:
                            shot_zones = shot_data['SHOT_ZONE_BASIC'].value_counts()
                            st.write("**Shot Zones:**")
                            for zone, count in shot_zones.head(5).items():
                                percentage = (count / total_shots * 100)
                                st.write(f"- {zone}: {count} shots ({percentage:.1f}%)")
                
                else:
                    st.warning(f"No shot data available for {selected_player} in the {season} season.")
                    st.info("This could mean:")
                    st.write("- The player hasn't played in the 2024-25 season yet")
                    st.write("- The data hasn't been updated recently")
                    st.write("- There was an issue fetching the data")
        
        else:
            st.error(f"Player ID not found for {selected_player}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            <p>Built with Streamlit | Data from NBA.com via nba_api</p>
            <p>Shot heatmaps show shooting frequency across court locations</p>
        </div>
        """, 
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()