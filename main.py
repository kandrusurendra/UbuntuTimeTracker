import sys
import signal
import subprocess

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
        # --- Track screen lock state ---
        self.was_locked = False
        
        self.setWindowTitle("Ubuntu Productivity Tracker")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        
        # --- Setup screen lock checking timer ---
        self.lock_timer = QTimer(self)
        self.lock_timer.timeout.connect(self.check_screen_state)
        self.lock_timer.start(5000)  # Checks every 5000 milliseconds (5 seconds)

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

    def toggle_timer(self, name, category):
        now = datetime.now()
        
        # Stop previous timer if one is already running
        if self.current_activity and self.start_time:
            self.engine.log_entry(self.current_activity, self.category, self.start_time, now)
        
        # Start new timer
        self.current_activity = name
        self.category = category
        self.start_time = now
        
        # Update UI
        self.status_label.setText(f"Currently Tracking: {name}")
        self.status_label.setStyleSheet(f"color: #2ecc71; font-size: 18px; font-weight: bold; padding: 10px;")
        self.refresh_table()
        
    def setup_dashboard(self):
        layout = QVBoxLayout(self.dash_tab)
        
        self.status_label = QLabel("Currently: Idle")
        self.status_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.status_label)

        # Activity Buttons
        btn_layout = QHBoxLayout()
        activities = [
            ("Development", "Work", "#2980b9"),
            ("Learning", "Work", "#27ae60"),
            ("Explore", "Entertainment", "#e67e22"),
            ("Personal", "Entertainment", "#c0392b"),
            ("Break", "Relaxation", "#f1c40f")
        ]

        for name, cat, color in activities:
            btn = QPushButton(name)
            btn.setStyleSheet(f"background-color: {color}; color: white; padding: 15px; font-weight: bold;")
            btn.clicked.connect(lambda ch, n=name, c=cat: self.toggle_timer(n, c))
            btn_layout.addWidget(btn)
        
        layout.addLayout(btn_layout)

        self.stop_btn = QPushButton("⏹ Stop Current Timer")
        self.stop_btn.setStyleSheet("background-color: #7f8c8d; color: white; padding: 10px; font-weight: bold;")
        self.stop_btn.clicked.connect(self.stop_timer)
        layout.addWidget(self.stop_btn)
        
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
        
        # Add a horizontal layout for multiple buttons
        btn_layout = QHBoxLayout()
        
        daily_btn = QPushButton("Show Daily View")
        daily_btn.clicked.connect(lambda: self.refresh_charts('Daily'))
        btn_layout.addWidget(daily_btn)
        
        weekly_btn = QPushButton("Show Weekly View")
        weekly_btn.clicked.connect(lambda: self.refresh_charts('Weekly'))
        btn_layout.addWidget(weekly_btn)
        
        layout.addLayout(btn_layout)
        
        
    def refresh_table(self):
        df = self.engine.get_data().tail(10)
        self.log_table.setRowCount(len(df))
        for i, row in enumerate(df.values):
            for j, val in enumerate(row):
                self.log_table.setItem(i, j, QTableWidgetItem(str(val)))

    def refresh_charts(self, timeframe='Daily'):
        df = self.engine.get_data()
        self.canvas.update_chart(df, timeframe=timeframe)

    def check_screen_state(self):
        try:
            # Query Ubuntu/GNOME for screen lock status
            result = subprocess.run(
                ["gdbus", "call", "-e", "-d", "org.gnome.ScreenSaver", 
                 "-o", "/org/gnome/ScreenSaver", "-m", "org.gnome.ScreenSaver.GetActive"],
                capture_output=True, text=True, timeout=2
            )
            
            # gdbus returns '(true,)' if locked, and '(false,)' if unlocked
            is_locked = "(true,)" in result.stdout.strip().lower()

            if is_locked and not self.was_locked:
                # State changed to Locked -> Stop whatever is currently running
                print("Screen locked. Automatically stopping timer.")
                self.stop_timer()
                self.was_locked = True
                
            elif not is_locked and self.was_locked:
                # State changed to Unlocked -> Start Development task
                print("Screen unlocked. Automatically starting 'Development'.")
                self.toggle_timer("Development", "Work")
                self.was_locked = False
                
        except Exception as e:
            # Silently ignore errors (e.g., if gdbus is temporarily busy)
            pass
            
    def closeEvent(self, event):
        """This runs automatically when the window is closed."""
        if self.current_activity and self.start_time:
            now = datetime.now()
            self.engine.log_entry(self.current_activity, self.category, self.start_time, now)
            print(f"Saved final session: {self.current_activity}")
        event.accept()
        
    def stop_timer(self):
        if self.current_activity and self.start_time:
            now = datetime.now()
            self.engine.log_entry(self.current_activity, self.category, self.start_time, now)
            
            # Reset the app state
            self.current_activity = None
            self.start_time = None
            self.status_label.setText("Currently: Idle")
            self.status_label.setStyleSheet("color: #7f8c8d; font-size: 18px; font-weight: bold;")
            self.refresh_table()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setApplicationName("TimeTracker")
    app.setDesktopFileName("timetracker")
    
    # Forces PyQt to respect Ctrl+C (SIGINT) from the terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    window = TimeTrackerApp()
    window.show()
    sys.exit(app.exec())
