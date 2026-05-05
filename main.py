import sys
import signal

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                             QTableWidgetItem, QTabWidget)
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime
from tracker_engine import TrackerEngine
from visuals import AnalyticsCanvas

class TimeTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = TrackerEngine()
        self.current_activity = None
        self.start_time = None
        
        self.setWindowTitle("Ubuntu Productivity Tracker")
        self.setMinimumSize(800, 600)
        
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Dashboard
        self.dash_tab = QWidget()
        self.setup_dashboard()
        self.tabs.addTab(self.dash_tab, "Tracker")

        # Tab 2: Insights
        self.insight_tab = QWidget()
        self.setup_insights()
        self.tabs.addTab(self.insight_tab, "Insights")

    def setup_dashboard(self):
        layout = QVBoxLayout(self.dash_tab)
        
        self.status_label = QLabel("Currently: Idle")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.status_label)

        # Activity Buttons
        btn_layout = QHBoxLayout()
        activities = [
            ("Coding", "Work", "#2980b9"),
            ("Learning", "Work", "#27ae60"),
            ("YouTube", "Entertainment", "#e67e22"),
            ("Gaming", "Entertainment", "#c0392b"),
            ("Break", "Relaxation", "#f1c40f")
        ]

        for name, cat, color in activities:
            btn = QPushButton(name)
            btn.setStyleSheet(f"background-color: {color}; color: white; padding: 15px; font-weight: bold;")
            btn.clicked.connect(lambda ch, n=name, c=cat: self.toggle_timer(n, c))
            btn_layout.addWidget(btn)
        
        layout.addLayout(btn_layout)

        # Manual Correction Section
        self.log_table = QTableWidget(10, 6)
        self.log_table.setHorizontalHeaderLabels(["Date", "Activity", "Category", "Start", "End", "Min"])
        layout.addWidget(QLabel("Recent Sessions:"))
        layout.addWidget(self.log_table)
        self.refresh_table()

    def setup_insights(self):
        layout = QVBoxLayout(self.insight_tab)
        self.canvas = AnalyticsCanvas(self)
        layout.addWidget(self.canvas)
        
        refresh_btn = QPushButton("Refresh Charts")
        refresh_btn.clicked.connect(self.refresh_charts)
        layout.addWidget(refresh_btn)

    def toggle_timer(self, name, category):
        now = datetime.now()
        
        # Stop previous
        if self.current_activity:
            self.engine.log_entry(self.current_activity, self.category, self.start_time, now)
        
        # Start new
        self.current_activity = name
        self.category = category
        self.start_time = now
        self.status_label.setText(f"Currently Tracking: {name}")
        self.status_label.setStyleSheet(f"color: #2ecc71; font-size: 18px; font-weight: bold;")
        self.refresh_table()

    def refresh_table(self):
        df = self.engine.get_data().tail(10)
        self.log_table.setRowCount(len(df))
        for i, row in enumerate(df.values):
            for j, val in enumerate(row):
                self.log_table.setItem(i, j, QTableWidgetItem(str(val)))

    def refresh_charts(self):
        df = self.engine.get_data()
        self.canvas.update_chart(df, timeframe='Daily')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("TimeTracker")
    app.setDesktopFileName("timetracker.desktop")
    
    # Forces PyQt to respect Ctrl+C (SIGINT) from the terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())
