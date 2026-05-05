# UbuntuTimeTracker
Work Time Tracker 
Prerequisites
# Install system dependencies for Qt6 and Wayland
sudo apt update
sudo apt install qt6-base-dev libqt6gui6 libqt6widgets6 -y

# Use pip to install the Python bindings
pip install PyQt6 pandas matplotlib

# Update system and install python dependencies
sudo apt update
sudo apt install python3-pip python3-pyqt6 -y

# Install required Python libraries
pip install pandas matplotlib pyqt6

sudo apt update
sudo apt install libxcb-cursor0 libxkbcommon-x11-0 -y

Location desktop shrotcut is (copy the .desktop to this location)
~/.local/share/applications/timetracker.desktop

Note: Ensure PYTHON PATH and packages path are updated properly for it to work.
Check python location using : which python3
Check PyQt6 lcoation using  : pip show PyQt6 | grep Location

To show in applications
chmod +x ~/.local/share/applications/timetracker.desktop
update-desktop-database ~/.local/share/applications/

