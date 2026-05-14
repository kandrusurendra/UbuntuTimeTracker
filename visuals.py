import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd

class AnalyticsCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        super().__init__(self.fig)

    def update_chart(self, df, timeframe='Daily'):
        self.ax.clear()
        if df.empty:
            self.draw()
            return

        df['Date'] = pd.to_datetime(df['Date'])
        today = pd.Timestamp.now().normalize()
        
        # Define a consistent color map so activities keep the same colors
        colors = {'Development': '#2980b9', 'Learning': '#27ae60', 'Explore': '#e67e22', 
                  'Personal': '#c0392b', 'Break': '#f1c40f'}

        if timeframe == 'Daily':
            # Daily View: Single bar per activity
            df = df[df['Date'] == today]
            if not df.empty:
                summary = df.groupby('Activity')['Duration_Min'].sum()
                # Apply colors based on the activity index
                bar_colors = [colors.get(act, '#bdc3c7') for act in summary.index]
                summary.plot(kind='bar', ax=self.ax, color=bar_colors)
                self.ax.set_xlabel("Activity")

        elif timeframe == 'Weekly':
            # Weekly View: Grouped bars showing days on X-axis and activities as separate bars
            df = df[df['Date'] >= today - pd.Timedelta(days=7)]
            if not df.empty:
                # Group by Date AND Activity, then unstack to create side-by-side bars
                summary = df.groupby([df['Date'].dt.strftime('%m-%d'), 'Activity'])['Duration_Min'].sum().unstack().fillna(0)
                
                # Plot grouped bars
                plot_colors = [colors.get(col, '#bdc3c7') for col in summary.columns]
                summary.plot(kind='bar', ax=self.ax, stacked=False, color=plot_colors)
                
                self.ax.set_xlabel("Date")
                # Move legend outside the plot area
                self.ax.legend(title='Activity', bbox_to_anchor=(1.05, 1), loc='upper left')

        self.ax.set_title(f"{timeframe} Usage (Minutes)")
        self.ax.set_ylabel("Minutes")
        
        # Fix layout so labels and legends aren't cut off
        self.fig.tight_layout()
        self.draw()
