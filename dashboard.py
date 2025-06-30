import streamlit as st
import matplotlib.pyplot as plt
from data_scraper import NBADataScraper
from heatmap import ShotHeatmapGenerator
from headshot import HeadshotManager
import pandas as pd
import numpy as np
import matplotlib.patches as patches


# Configure Streamlit page
st.set_page_config(
    page_title="SPLASH MAP - NBA Shot Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with black background and white text
st.markdown("""
<style>
    .splash-header {
        color: white;
        text-align: left;
        font-size: 3.5rem;
        font-weight: 900;
        letter-spacing: 2px;
        margin-bottom: 10px;
        padding: 0;
    }
    
    .splash-subheading {
        color: #cccccc;
        text-align: left;
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 0;
        margin-bottom: 0;
        padding: 0;
    }
    
    .header-section {
        background-color: transparent;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
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
    
    .stats-table {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .frequency-section {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)


class ShotDotsGenerator:
    """Generate shot dots visualization on basketball court with color coding"""
    
    def draw_half_court_white_bg(self, ax=None, color="white", lw=2):
        """Draw a clean half-court with white lines on black background"""
        if ax is None:
            ax = plt.gca()

        elements = [
            # Outer boundary
            patches.Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False),

            # Three-point arc
            patches.Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color),

            # Free throw circle
            patches.Circle((0, 142.5), radius=60, linewidth=lw, color=color, fill=False),

            # Free throw lane (key/paint)
            patches.Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False),

            # Restricted area
            patches.Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color),

            # Basket
            patches.Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False),

            # Free throw line
            patches.Rectangle((-80, 142.5), 160, 0, linewidth=lw, color=color),
        ]

        # Three-point line straight sections (corners)
        ax.plot([-220, -220], [-47.5, 92.5], color=color, linewidth=lw)
        ax.plot([220, 220], [-47.5, 92.5], color=color, linewidth=lw)

        for e in elements:
            ax.add_patch(e)
        return ax
    
    def create_shot_dots_plot(self, shot_data, player_name=None, season="2024-25", 
                             figsize=(12, 11), dot_size=25, alpha=0.7):
        """
        Create shot dots visualization with color coding for makes/misses
        
        Parameters:
        -----------
        shot_data : pd.DataFrame
            Shot data with LOC_X, LOC_Y, and SHOT_MADE_FLAG columns
        player_name : str, optional
            Player name for title
        season : str
            Season for title
        figsize : tuple
            Figure size
        dot_size : int
            Size of shot dots
        alpha : float
            Transparency of dots
        
        Returns:
        --------
        fig, ax : matplotlib figure and axis objects
        """
        
        # Create figure with black background
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        # Draw court with white lines on black background
        self.draw_half_court_white_bg(ax, color="white", lw=2)
        
        if not shot_data.empty and 'SHOT_MADE_FLAG' in shot_data.columns:
            # Separate made and missed shots
            made_shots = shot_data[shot_data['SHOT_MADE_FLAG'] == 1]
            missed_shots = shot_data[shot_data['SHOT_MADE_FLAG'] == 0]
            
            # Plot missed shots as red dots
            if not missed_shots.empty:
                ax.scatter(
                    missed_shots['LOC_X'], 
                    missed_shots['LOC_Y'],
                    c='#FF4444',  # Red for misses
                    s=dot_size,
                    alpha=alpha,
                    edgecolors='white',
                    linewidth=0.3,
                    label='Missed'
                )
            
            # Plot made shots as blue dots
            if not made_shots.empty:
                ax.scatter(
                    made_shots['LOC_X'], 
                    made_shots['LOC_Y'],
                    c='#00BFFF',  # Blue for makes
                    s=dot_size,
                    alpha=alpha,
                    edgecolors='white',
                    linewidth=0.3,
                    label='Made'
                )
        
        # Add legend in the center bottom
        if not shot_data.empty and 'SHOT_MADE_FLAG' in shot_data.columns:
            legend = ax.legend(
                loc='lower center',
                bbox_to_anchor=(0.5, -0.05),
                frameon=True,
                facecolor='black',
                edgecolor='white',
                fontsize=12,
                ncol=2
            )
            # Set legend text color to white
            for text in legend.get_texts():
                text.set_color('white')
        
        # Set bounds and remove axes
        ax.set_xlim(-250, 250)
        ax.set_ylim(422.5, -47.5)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Remove axis spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        return fig, ax


@st.cache_data
def load_data_scraper():
    """Load the data scraper with caching"""
    return NBADataScraper()


@st.cache_data
def load_heatmap_generator():
    """Load the heatmap generator with caching"""
    return ShotHeatmapGenerator()


@st.cache_data
def load_headshot_manager():
    """Load the headshot manager with caching"""
    return HeadshotManager()


@st.cache_data
def get_player_shot_data(player_id, season):
    """Get player shot data with caching"""
    scraper = load_data_scraper()
    return scraper.get_player_shot_data(player_id, season)


def get_player_headshot_path(player_id):
    """Get player headshot file path"""
    headshot_manager = load_headshot_manager()
    return headshot_manager.get_headshot(player_id)


def create_enhanced_heatmap_generator():
    """Create enhanced heatmap generator with simplified colorbar"""
    
    class EnhancedShotHeatmapGenerator(ShotHeatmapGenerator):
        def create_shot_heatmap(self, player_data, player_name=None, season="2024-25",
                              resolution=150, bandwidth_factor=0.3, threshold=0.05,
                              figsize=(12, 11), colormap='inferno_r'):
            """Enhanced heatmap with simplified colorbar"""
            
            # Check if data is empty
            if player_data.empty or len(player_data) == 0:
                fig, ax = plt.subplots(figsize=figsize)
                fig.patch.set_facecolor('black')
                ax.set_facecolor("black")
                
                self.draw_full_half_court(ax, color="white", lw=2)
                ax.text(0, 200, "No shot data available", 
                       ha='center', va='center', fontsize=20, color='white')
                
                ax.set_xlim(-250, 250)
                ax.set_ylim(422.5, -47.5)
                ax.set_xticks([])
                ax.set_yticks([])
                
                for spine in ax.spines.values():
                    spine.set_visible(False)
                
                plt.tight_layout()
                return fig, ax

            # Create figure
            fig, ax = plt.subplots(figsize=figsize)
            fig.patch.set_facecolor('black')
            ax.set_facecolor("black")

            # Draw court FIRST
            self.draw_full_half_court(ax, color="white", lw=2)

            # Calculate KDE
            X, Y, Z = self.create_kde_heatmap(
                player_data['LOC_X'].values,
                player_data['LOC_Y'].values,
                x_range=(-250, 250),
                y_range=(-47.5, 422.5),
                resolution=resolution,
                bandwidth_factor=bandwidth_factor
            )

            # Create custom colormap with alpha
            alpha_cmap = self.create_alpha_colormap(colormap)

            # Normalize and apply threshold
            Z_normalized = Z / Z.max()
            Z_masked = np.ma.masked_where(Z_normalized < threshold, Z_normalized)

            # Plot heatmap
            im = ax.pcolormesh(
                X, Y, Z_masked,
                cmap=alpha_cmap,
                shading='gouraud',
                edgecolors='none',
                linewidth=0,
                antialiased=True,
                rasterized=True
            )

            # Set clean bounds
            ax.set_xlim(-250, 250)
            ax.set_ylim(422.5, -47.5)
            ax.set_xticks([])
            ax.set_yticks([])

            # Remove axis spines
            for spine in ax.spines.values():
                spine.set_visible(False)

            # Add simplified colorbar with "Less" to "More" labels
            cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label("Shot Density", color="white", labelpad=15)

            # Set simple ticks
            cbar.set_ticks([0, 0.5, 1])
            cbar.set_ticklabels(['Less', '', 'More'])

            cbar.ax.yaxis.set_tick_params(color="white")
            plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
            cbar.outline.set_visible(False)

            plt.tight_layout()
            return fig, ax
    
    return EnhancedShotHeatmapGenerator()


def clear_cache_for_new_player():
    """Clear relevant caches when a new player is selected"""
    if 'current_player' in st.session_state:
        # Clear specific cache functions
        get_player_shot_data.clear()


def main():
    """Main dashboard function"""
    
    # Header Section with SPLASH MAP title and subheading in black background
    st.markdown("""
    <div class="header-section">
        <h1 class="splash-header">SPLASH MAP</h1>
        <p class="splash-subheading">A dashboard visualizing shot data from the top 100 NBA players during the 2024–2025 season</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    scraper = load_data_scraper()
    heatmap_gen = create_enhanced_heatmap_generator()
    shot_dots_gen = ShotDotsGenerator()
    
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
        
        # Check if player changed and clear cache
        if 'current_player' not in st.session_state:
            st.session_state.current_player = selected_player
        elif st.session_state.current_player != selected_player:
            clear_cache_for_new_player()
            st.session_state.current_player = selected_player
        
        # Season selection (fixed to 2024-25 as requested)
        season = "2024-25"
    
    # Main content area
    if selected_player:
        # Get player ID
        player_id = scraper.get_player_id(selected_player)
        
        if player_id:
            # Create columns for layout - SWAPPED: col1 is now narrow (for player info), col2 is now wide (for charts)
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # Player info section - NOW ON THE LEFT
                st.subheader(selected_player)
                
                # Get and display player headshot
                with st.spinner("Loading player image..."):
                    headshot_path = get_player_headshot_path(player_id)
                    
                if headshot_path:
                    st.image(headshot_path, use_container_width=True)
                else:
                    st.info("Player image not available")
                
                # Load shot data for calculations
                with st.spinner("Loading shot data..."):
                    shot_data = get_player_shot_data(player_id, season)
                
                if not shot_data.empty:
                    # Calculate stats for frequency breakdown
                    total_shots = len(shot_data)
                    
                    # Shot frequency breakdown on the left side
                    st.markdown("---")
                    st.markdown("### Shot Breakdown")
                    
                    # Shot type breakdown
                    if 'SHOT_TYPE' in shot_data.columns:
                        shot_types = shot_data['SHOT_TYPE'].value_counts()
                        st.markdown("**Shot Types:**")
                        for shot_type, count in shot_types.items():
                            percentage = (count / total_shots * 100)
                            st.write(f"• {shot_type}: {count} ({percentage:.1f}%)")
                    
                    st.markdown("")  # Add spacing
                    
                    # Shot zone breakdown
                    if 'SHOT_ZONE_BASIC' in shot_data.columns:
                        shot_zones = shot_data['SHOT_ZONE_BASIC'].value_counts()
                        st.markdown("**Shot Zones:**")
                        for zone, count in shot_zones.head(5).items():
                            percentage = (count / total_shots * 100)
                            st.write(f"• {zone}: {count} ({percentage:.1f}%)")
                    
                    st.markdown("")  # Add spacing
                    
                    # Shot distance breakdown
                    if 'SHOT_DISTANCE' in shot_data.columns:
                        shot_data_copy = shot_data.copy()
                        shot_data_copy['DISTANCE_RANGE'] = pd.cut(
                            shot_data_copy['SHOT_DISTANCE'], 
                            bins=[0, 3, 10, 16, 23, 50], 
                            labels=['0-3ft', '4-10ft', '11-16ft', '17-23ft', '24+ft']
                        )
                        distance_counts = shot_data_copy['DISTANCE_RANGE'].value_counts()
                        st.markdown("**Shot Distance:**")
                        for distance, count in distance_counts.items():
                            percentage = (count / total_shots * 100)
                            st.write(f"• {distance}: {count} ({percentage:.1f}%)")
            
            with col2:
                # Load shot data - NOW ON THE RIGHT
                with st.spinner("Loading shot data..."):
                    shot_data = get_player_shot_data(player_id, season)
                
                if not shot_data.empty:
                    # Calculate stats
                    total_shots = len(shot_data)
                    made_shots = len(shot_data[shot_data['SHOT_MADE_FLAG'] == 1])
                    fg_percentage = (made_shots / total_shots * 100) if total_shots > 0 else 0
                    
                    # Shooting summary in clean table format
                    st.markdown("### Shooting Summary")
                    summary_col1, summary_col2, summary_col3 = st.columns(3)
                    
                    with summary_col1:
                        st.metric("Total Shots", f"{total_shots:,}")
                    
                    with summary_col2:
                        st.metric("Made Shots", f"{made_shots:,}")
                    
                    with summary_col3:
                        st.metric("FG%", f"{fg_percentage:.1f}%")
                    
                    # Shot heatmap title
                    st.subheader("Shot Heatmap")
                    
                    # Heatmap Settings directly below the title
                    st.markdown("**Heatmap Settings**")
                    heatmap_col1, heatmap_col2 = st.columns(2)
                    
                    with heatmap_col1:
                        # Resolution slider
                        resolution = st.slider(
                            "Resolution",
                            min_value=50,
                            max_value=200,
                            value=74,
                            step=5,
                            help="Higher values create more detailed heatmaps but take longer to generate"
                        )
                    
                    with heatmap_col2:
                        # Smoothing slider (bandwidth factor)
                        smoothing = st.slider(
                            "Smoothing",
                            min_value=0.1,
                            max_value=1.0,
                            value=0.4,
                            step=0.05,
                            help="Lower values create more focused hot spots, higher values create broader patterns"
                        )
                    
                    # Generate heatmap with user-controlled settings
                    with st.spinner("Generating heatmap..."):
                        fig, ax = heatmap_gen.generate_heatmap_for_player(
                            player_id=player_id,
                            shot_data=shot_data,
                            player_name=None,  # No title on the image
                            season=season,
                            resolution=resolution,
                            bandwidth_factor=smoothing
                        )
                        
                        # Display the heatmap
                        st.pyplot(fig, use_container_width=True)
                        plt.close(fig)
                    
                    # Shot dots chart with color coding
                    st.subheader("Shot Locations")
                    with st.spinner("Generating shot locations..."):
                        dots_fig, dots_ax = shot_dots_gen.create_shot_dots_plot(
                            shot_data=shot_data,
                            player_name=None,
                            season=season,
                            dot_size=20,
                            alpha=0.7
                        )
                        
                        # Display the shot dots
                        st.pyplot(dots_fig, use_container_width=True)
                        plt.close(dots_fig)
                
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
        </div>
        """, 
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()