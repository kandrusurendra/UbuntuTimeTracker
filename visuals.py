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
            return

        df['Date'] = pd.to_datetime(df['Date'])
        
        # Filter logic
        today = pd.Timestamp.now().normalize()
        if timeframe == 'Daily':
            df = df[df['Date'] == today]
        elif timeframe == 'Weekly':
            df = df[df['Date'] >= today - pd.Timedelta(days=7)]

        if not df.empty:
            summary = df.groupby('Activity')['Duration_Min'].sum()
            summary.plot(kind='bar', ax=self.ax, color=['#3498db', '#2ecc71', '#e74c3c', '#9b59b6'])
            self.ax.set_title(f"{timeframe} Usage (Minutes)")
            self.ax.set_ylabel("Minutes")
            self.fig.tight_layout()
        
        self.draw()
