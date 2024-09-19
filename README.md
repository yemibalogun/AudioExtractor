Sure! Here’s a detailed documentation for the provided code:

```markdown
# Audio Extractor and Voice Generation

This application extracts audio from MP4 video files and generates new voice audio using the extracted MP3 files. It utilizes PyQt5 for the GUI and MoviePy for audio extraction, along with an external API for voice generation.

## Requirements

- Python 3.x
- PyQt5
- MoviePy
- Requests
- `python-dotenv` for environment variable management

## Setup

1. Install the required libraries:
   ```bash
   pip install PyQt5 moviepy requests python-dotenv
   ```

2. Create a `.env` file in the project root directory and add your Eleven Labs API key:
   ```
   ELEVEN_LABS_API_KEY=your_api_key_here
   ```

## Main Classes

### `AudioExtractor`

This is the main widget for the application, responsible for the GUI and handling audio extraction.

#### Methods

- `__init__(self)`: Initializes the widget and sets up the user interface.
- `initUI(self)`: Creates the file dialog for selecting an MP4 file, generates the corresponding MP3 filename, and initiates the audio extraction process.
- `show_message(self, title, message)`: Displays a message box with a specified title and message.
- `update_progress(self, value)`: Updates the progress dialog based on the provided value.
- `on_audio_extraction_done(self, mp3_file_path)`: Closes the progress dialog and triggers voice generation upon successful audio extraction.
- `generate_new_voice(self, mp3_file, output_file)`: Initiates the voice generation process in a separate thread.
- `on_voice_generation_done(self, success, message)`: Closes the progress dialog and displays success or error messages after voice generation.

### `AudioExtractionThread`

A separate thread for handling audio extraction from the video file.

#### Signals

- `progress_signal`: Emits the current progress as an integer (0 to 100).
- `finished_signal`: Emits the path of the extracted MP3 file upon completion.

#### Methods

- `__init__(self, mp4_file, mp3_file)`: Initializes the thread with the input MP4 and output MP3 file paths.
- `run(self)`: Extracts audio from the video file and saves it as an MP3. Emits progress and completion signals.

### `VoiceGenerationThread`

A separate thread for generating voice audio from the extracted MP3 file using an external API.

#### Signals

- `progress_signal`: Emits the current progress as an integer (0 to 100).
- `finished_signal`: Emits a success flag and message upon completion.

#### Methods

- `__init__(self, mp3_file, output_file)`: Initializes the thread with the input MP3 file and output file paths.
- `run(self)`: Sends a request to the voice generation API and streams the audio output. Emits progress and completion signals.

## Running the Application

To run the application, execute the following command:

```bash
python main.py
```

This will open a file dialog to select an MP4 file, and the audio extraction process will begin. Once completed, the application will attempt to generate a new voice file using the extracted audio.

## Notes

- Ensure that the MP4 video files selected have audio tracks; otherwise, the application will notify the user of the failure to extract audio.
- The generated audio files will be saved in the same directory as the selected MP4 file, with appropriate naming conventions.

## Error Handling

Error messages will be displayed through message boxes for any failures during audio extraction or voice generation. Ensure that the API key is valid and correctly set in the `.env` file to avoid authorization errors.
```

This documentation covers the functionality, classes, methods, and usage of your code. Let me know if you need any adjustments or additional details!
