import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde


class ShotHeatmapGenerator:
    def __init__(self):
        """Initialize the heatmap generator"""
        pass
    
    def draw_full_half_court(self, ax=None, color="white", lw=2):
        """Draw a clean half-court with essential NBA markings including connected three-point line"""
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

        # Three-point line straight sections (corners) - connect to the arc
        # Left corner three-point line
        ax.plot([-220, -220], [-47.5, 92.5], color=color, linewidth=lw)
        # Right corner three-point line
        ax.plot([220, 220], [-47.5, 92.5], color=color, linewidth=lw)

        for e in elements:
            ax.add_patch(e)
        return ax

    def create_kde_heatmap(self, x_data, y_data, x_range, y_range, resolution=100, bandwidth_factor=1.0):
        """Create KDE heatmap with full control over transparency"""
        # Create coordinate grid
        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)

        # Calculate KDE
        positions = np.vstack([X.ravel(), Y.ravel()])
        values = np.vstack([x_data, y_data])
        kernel = gaussian_kde(values)

        # Adjust bandwidth
        kernel.covariance_factor = lambda: bandwidth_factor
        kernel._compute_covariance()

        # Calculate density
        Z = np.reshape(kernel(positions).T, X.shape)

        return X, Y, Z

    def create_alpha_colormap(self, base_cmap='inferno_r'):
        """Create colormap where low values are transparent"""
        base = plt.cm.get_cmap(base_cmap)
        colors = base(np.linspace(0, 1, 256))

        # Set alpha based on intensity
        alphas = np.linspace(0, 0.85, 256)
        colors[:, 3] = alphas

        return mcolors.ListedColormap(colors)

    def create_shot_heatmap(self, player_data, player_name=None, season="2024-25",
                          resolution=150, bandwidth_factor=0.3, threshold=0.05,
                          figsize=(12, 11), colormap='inferno_r'):
        """
        Create a shot heatmap for any player

        Parameters:
        -----------
        player_data : pd.DataFrame
            DataFrame containing shot data with LOC_X and LOC_Y columns
        player_name : str, optional
            Player name for the title
        season : str
            Season for the title
        resolution : int
            Grid resolution for KDE calculation
        bandwidth_factor : float
            KDE bandwidth adjustment
        threshold : float
            Transparency threshold for low-density areas
        figsize : tuple
            Figure size
        colormap : str
            Base colormap name

        Returns:
        --------
        fig, ax : matplotlib figure and axis objects
        """
        
        # Check if data is empty
        if player_data.empty or len(player_data) == 0:
            # Create empty plot with message
            fig, ax = plt.subplots(figsize=figsize)
            fig.patch.set_facecolor('black')
            ax.set_facecolor("black")
            
            # Draw court
            self.draw_full_half_court(ax, color="white", lw=2)
            
            # Add no data message
            ax.text(0, 200, "No shot data available", 
                   ha='center', va='center', fontsize=20, color='white')
            
            # Set clean bounds
            ax.set_xlim(-250, 250)
            ax.set_ylim(422.5, -47.5)
            ax.set_xticks([])
            ax.set_yticks([])
            
            # Remove axis spines
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            title = f"Shot Density ({season})"
            if player_name:
                title = f"{player_name} — {title}"
            ax.set_title(title, y=1.05, fontsize=18, color="white")
            
            plt.tight_layout()
            return fig, ax

        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor('black')
        ax.set_facecolor("black")

        # Draw court FIRST
        self.draw_full_half_court(ax, color="white", lw=2)

        # Calculate KDE manually
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

        # Plot with pcolormesh for clean edges
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

        # Add title
        title = f"Shot Density ({season})"
        if player_name:
            title = f"{player_name} — {title}"
        ax.set_title(title, y=1.05, fontsize=18, color="white")

        # Add shot count and data attribution
        total_shots = len(player_data)
        ax.text(-250, 445, f"Total Shots: {total_shots:,} | Data: stats.nba.com",
                fontsize=11, color="white")

        # Add colorbar with actual shot frequency
        # Calculate shot frequency per unit area for colorbar
        max_density = Z.max()
        total_area = 500 * 470  # Court dimensions
        grid_area = total_area / (resolution * resolution)
        max_shots_per_area = max_density * total_shots * grid_area

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Shot Frequency", color="white", labelpad=15)

        # Set colorbar ticks to show actual shot frequency
        cbar_ticks = np.linspace(0, 1, 6)
        cbar_labels = [f"{int(tick * max_shots_per_area)}" for tick in cbar_ticks]
        cbar.set_ticks(cbar_ticks)
        cbar.set_ticklabels(cbar_labels)

        cbar.ax.yaxis.set_tick_params(color="white")
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        cbar.outline.set_visible(False)

        plt.tight_layout()
        return fig, ax
    
    def generate_heatmap_for_player(self, player_id, shot_data, player_name=None, 
                                   season="2024-25", **kwargs):
        """
        Convenience method to generate heatmap for a specific player
        
        Parameters:
        -----------
        player_id : int
            NBA API player ID
        shot_data : pd.DataFrame
            Shot data for the player
        player_name : str, optional
            Player name for the title
        season : str
            Season for the title
        **kwargs : additional arguments passed to create_shot_heatmap
        
        Returns:
        --------
        fig, ax : matplotlib figure and axis objects
        """
        return self.create_shot_heatmap(
            player_data=shot_data,
            player_name=player_name,
            season=season,
            **kwargs
        )


if __name__ == "__main__":
    # Test the heatmap generator
    from data_scraper import NBADataScraper
    
    # Initialize components
    scraper = NBADataScraper()
    heatmap_gen = ShotHeatmapGenerator()
    
    # Test with Stephen Curry
    curry_id = scraper.get_player_id("Stephen Curry")
    if curry_id:
        # Get shot data
        shot_data = scraper.get_player_shot_data(curry_id, "2024-25")
        
        # Generate heatmap
        fig, ax = heatmap_gen.generate_heatmap_for_player(
            player_id=curry_id,
            shot_data=shot_data,
            player_name="Stephen Curry",
            season="2024-25"
        )
        
        plt.show()