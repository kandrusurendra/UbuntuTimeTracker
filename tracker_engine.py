import pandas as pd
import os
from datetime import datetime

class TrackerEngine:
    def __init__(self, filename="data/time_log.csv"):
        self.filename = filename
        if not os.path.exists("data"):
            os.makedirs("data")
            
        # Check if file doesn't exist OR if it is completely empty (0 bytes)
        if not os.path.exists(self.filename) or os.path.getsize(self.filename) == 0:
            self._initialize_csv()
        else:
            # Test read to catch edge cases (like a file with only blank spaces)
            try:
                pd.read_csv(self.filename)
            except pd.errors.EmptyDataError:
                self._initialize_csv()

    def _initialize_csv(self):
        """Creates a fresh CSV with the correct headers."""
        df = pd.DataFrame(columns=["Date", "Activity", "Category", "Start", "End", "Duration_Min"])
        df.to_csv(self.filename, index=False)

    def log_entry(self, activity, category, start_dt, end_dt):
        duration = (end_dt - start_dt).total_seconds() / 60
        new_row = {
            "Date": start_dt.strftime("%Y-%m-%d"),
            "Activity": activity,
            "Category": category,
            "Start": start_dt.strftime("%H:%M:%S"),
            "End": end_dt.strftime("%H:%M:%S"),
            "Duration_Min": round(duration, 2)
        }
        
        # Read, append, and save
        try:
            df = pd.read_csv(self.filename)
        except pd.errors.EmptyDataError:
            self._initialize_csv()
            df = pd.read_csv(self.filename)
            
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.filename, index=False)

    def get_data(self):
        try:
            return pd.read_csv(self.filename)
        except pd.errors.EmptyDataError:
            self._initialize_csv()
            return pd.read_csv(self.filename)
