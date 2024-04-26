
# Audio Clicker App

This application is a PyQt5 desktop app that listens to the audio input to trigger mouse clicks based on the detected audio levels exceeding a specified threshold. It is particularly useful for automating clicks in response to audio cues.

## Features

- Select audio input device.
- Set the number of clicks to perform.
- Collect screen coordinates by clicking on the screen.
- Start and stop audio monitoring.
- GUI updates safely from different threads using signals.

## Installation

Before running the application, ensure you have Python installed along with the following packages:
- PyQt5
- PyAudio
- numpy
- pynput
- pyautogui

You can install the required packages using pip:

```
pip install PyQt5 numpy pynput pyautogui pyaudio
```

## Usage

Run the application by executing the Python script:

```
python audio_clicker_app.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or feature requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.
