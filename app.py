import sys
import threading
import numpy as np
import pyaudio
import pyautogui
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox, QLineEdit, QLabel, QTextEdit
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from pynput.mouse import Listener as MouseListener

class AudioClickerApp(QWidget):
    update_log_signal = pyqtSignal(str)  # Signal to update log

    def __init__(self):
        super().__init__()
        self.initUI()
        self.audio_stream = None
        self.coordinates = []
        self.num_clicks = 0
        self.wait_time = 3  # Default wait time
        self.monitoring_active = False
        self.monitoring_thread = None
        self.threshold = 1000  # Default threshold
        self.update_log_signal.connect(self.update_log)  # Connect signal to slot

    def initUI(self):
        self.setWindowTitle("Audio Clicker Setup")
        layout = QVBoxLayout()
        self.device_combo = QComboBox()
        pa = pyaudio.PyAudio()
        for i in range(pa.get_device_count()):
            dev_info = pa.get_device_info_by_index(i)
            self.device_combo.addItem(f"{dev_info['name']} (Index: {dev_info['index']})")
        layout.addWidget(QLabel("Select Audio Device:"))
        layout.addWidget(self.device_combo)
        self.clicks_input = QLineEdit()
        layout.addWidget(QLabel("Enter number of clicks (1-9):"))
        layout.addWidget(self.clicks_input)
        self.wait_time_input = QLineEdit()
        layout.addWidget(QLabel("Enter wait time in seconds:"))
        layout.addWidget(self.wait_time_input)
        self.threshold_input = QLineEdit()
        layout.addWidget(QLabel("Enter detection threshold:"))
        layout.addWidget(self.threshold_input)
        self.set_device_button = QPushButton("Set Audio Device")
        self.set_device_button.clicked.connect(self.setup_audio)
        layout.addWidget(self.set_device_button)
        self.set_clicks_button = QPushButton("Confirm Number of Clicks")
        self.set_clicks_button.clicked.connect(self.set_number_of_clicks)
        layout.addWidget(self.set_clicks_button)
        self.set_wait_time_button = QPushButton("Set Wait Time")
        self.set_wait_time_button.clicked.connect(self.set_wait_time)
        layout.addWidget(self.set_wait_time_button)
        self.set_threshold_button = QPushButton("Set Threshold")
        self.set_threshold_button.clicked.connect(self.set_threshold)
        layout.addWidget(self.set_threshold_button)
        self.collect_coords_button = QPushButton("Collect Coordinates")
        self.collect_coords_button.clicked.connect(self.collect_coordinates)
        layout.addWidget(self.collect_coords_button)
        self.start_button = QPushButton("Start Monitoring")
        self.start_button.clicked.connect(self.toggle_monitoring)
        self.start_button.setStyleSheet("background-color: red")
        layout.addWidget(self.start_button)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        self.setLayout(layout)
        self.resize(500, 600)

    def setup_audio(self):
        device_index = self.device_combo.currentIndex()
        pa = pyaudio.PyAudio()
        self.audio_stream = pa.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=device_index, frames_per_buffer=1024)

    def set_number_of_clicks(self):
        try:
            num = int(self.clicks_input.text())
            if 1 <= num <= 9:
                self.num_clicks = num
            else:
                raise ValueError("Number of clicks must be between 1 and 9.")
        except ValueError as e:
            print(e)

    def set_wait_time(self):
        try:
            wait_time = int(self.wait_time_input.text())
            if wait_time > 0:
                self.wait_time = wait_time
            else:
                raise ValueError("Wait time must be a positive integer.")
        except ValueError as e:
            print(e)

    def set_threshold(self):
        try:
            threshold = int(self.threshold_input.text())
            if threshold > 0:
                self.threshold = threshold
            else:
                raise ValueError("Threshold must be a positive integer.")
        except ValueError as e:
            print(e)

    def collect_coordinates(self):
        self.coordinates = []
        print("Click on the desired locations on the screen.")
        def on_click(x, y, button, pressed):
            if pressed:
                self.coordinates.append((x, y))
                if len(self.coordinates) >= self.num_clicks:
                    return False  # Stop listener
        with MouseListener(on_click=on_click) as listener:
            listener.join()
        pyautogui.alert('Coordinates collection complete.')

    def toggle_monitoring(self):
        if not self.monitoring_active:
            self.monitoring_active = True
            self.start_button.setText("Stop Monitoring")
            self.start_button.setStyleSheet("background-color: green")
            self.monitoring_thread = threading.Thread(target=self.monitor_audio)
            self.monitoring_thread.start()
        else:
            self.monitoring_active = False
            self.start_button.setText("Start Monitoring")
            self.start_button.setStyleSheet("background-color: red")
            if self.monitoring_thread is not None:
                self.monitoring_thread.join()

    def monitor_audio(self):
        previous_level_below_threshold = True
        try:
            while self.monitoring_active:
                data = np.frombuffer(self.audio_stream.read(1024), dtype=np.int16)
                current_level = np.max(data)
                if current_level > self.threshold:
                    if previous_level_below_threshold:
                        previous_level_below_threshold = False
                        for x, y in self.coordinates:
                            pyautogui.click(x, y)
                            self.update_log_signal.emit("Click")  # Emit signal instead of direct call
                else:
                    if not previous_level_below_threshold:
                        previous_level_below_threshold = True
                        threading.Timer(self.wait_time, self.perform_clicks).start()
        except Exception as e:
            print(f"Error: {e}")

    def perform_clicks(self):
        for x, y in self.coordinates:
            pyautogui.click(x, y)
            self.update_log_signal.emit("Click")  # Emit signal for click messages

    def update_log(self, text):
        self.log_output.append(text)
        self.log_output.moveCursor(self.log_output.textCursor().End)

    def closeEvent(self, event):
        self.monitoring_active = False
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.monitoring_thread:
            self.monitoring_thread.join()
        event.accept()

# Main function to run the application
def main():
    app = QApplication(sys.argv)
    ex = AudioClickerApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
