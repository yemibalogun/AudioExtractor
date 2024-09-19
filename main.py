import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
from moviepy.editor import VideoFileClip
import requests
import json

# Load environm,ent variables from .env file
load_dotenv()

class AudioExtractor(QWidget):
    
    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
        
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Open the file dialog to select a video file 
        mp4_file_path, _ = QFileDialog.getOpenFileName(self, "Select MP4 file", "", "MP4 files (*.mp4)")
        
        # If a file is selected
        if mp4_file_path:
            mp3_file_path = mp4_file_path.replace(".mp4", ".mp3")
            self.extract_audio_from_video(mp4_file_path, mp3_file_path)
            print(f"Audio extracted and saved as: {mp3_file_path}")
            
            # Generate new audio with Eleven Labs voice
            new_mp3_file_path = mp3_file_path.replace("mp3", "_new_voice.mp3")
            self.generate_new_voice(mp3_file_path, new_mp3_file_path)
        else:
            self.show_message("Error", "No file selected.")
        
    def extract_audio_from_video(self, mp4_file, mp3_file):
        # Extract audio from the video file.
        try:
            video = VideoFileClip(mp4_file)
            audio = video.audio
            if audio:
                audio.write_audiofile(mp3_file, codec='mp3')
            else:
                self.show_message("Error", "No audio found in the video.")
        except Exception as e:
            self.show_message("Error", f"An error occured while extracting audio: {e}")
    
    def generate_new_voice(self, mp3_file, output_file):
        # Use Eleven Labs to generate new voice from the extracted audio.
        try:
            # Load the API key from environment variables
            XI_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
            if not XI_API_KEY:
                self.show_message("Error", "API key not found. Please check your .env file.")
                return
            
            # Define constants for the script
            CHUNK_SIZE = 1024  # Size of chunks to read/write at a time
            VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # ID of the voice model to use
            AUDIO_FILE_PATH = mp3_file  # Path to the input audio file
            OUTPUT_PATH = output_file  # Path to save the output audio file

            # Construct the URL for the Speech-to-Speech API request
            sts_url = f"https://api.elevenlabs.io/v1/speech-to-speech/{VOICE_ID}/stream"

            # Set up headers for the API request, including the API key for authentication
            headers = {
                "Accept": "application/json",
                "xi-api-key": XI_API_KEY
            }

            # Set up the data payload for the API request, including model ID and voice settings
            # Note: voice settings are converted to a JSON string
            data = {
                "model_id": "eleven_english_sts_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }

            # Set up the files to send with the request, including the input audio file
            
            with open(AUDIO_FILE_PATH, "rb") as audio_file:
                files = {"audio": audio_file}
                # Make the POST request to the STS API with headers, data, and files, enabling streaming response
                response = requests.post(sts_url, headers=headers, data=data, files=files, stream=True)

            # Check if the request was successful
            if response.ok:
                # Open the output file in write-binary mode
                with open(OUTPUT_PATH, "wb") as f:
                    # Read the response in chunks and write to the file
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        f.write(chunk)
                # Inform the user of success
                print("Audio stream saved successfully.")
            else:
                # Print the error message if the request was not successful
                self.show_message("Error", f"Request failed with status code {response.status_code}: {response.text}")
        except Exception as e:
            self.show_message("Error", f"Voice generation failed: {e}")
            
    
if __name__=='__main__':
    app = QApplication(sys.argv)
    window = AudioExtractor() # Run the Audio Extractor GUI
    window.show() # Show the widget
    sys.exit(app.exec_()) # Srart the application event loop