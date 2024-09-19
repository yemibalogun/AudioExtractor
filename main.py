import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtCore import QThread, pyqtSignal
from moviepy.editor import VideoFileClip
import requests

# Load environm,ent variables from .env file
load_dotenv()

class AudioExtractor(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Open the file dialog to select a video file 
        mp4_file_path, _ = QFileDialog.getOpenFileName(self, "Select MP4 file", "", "MP4 files (*.mp4)")
        
        # If a file is selected
        if mp4_file_path:
            # Generate MP3 filename from the MP4 filename
            base_name = os.path.basename(mp4_file_path) # Extract file name from the full path
            mp3_file_path = os.path.splitext(base_name)[0] + ".mp3" # Replace .mp4 with .mp3
            
            # Show progress dialog for audio extraction
            self.progress_dialog = QProgressDialog("Extracting audio...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowTitle("Please wait")
            self.progress_dialog.setAutoClose(True)
            self.progress_dialog.setAutoReset(True)
            self.progress_dialog.show()
            
            # Start audio extraction in a separate thread
            self.audio_thread = AudioExtractionThread(mp4_file_path, mp3_file_path)
            self.audio_thread.progress_signal.connect(self.update_progress)
            self.audio_thread.finished_signal.connect(self.on_audio_extraction_done)
            self.audio_thread.start()
        else:
            self.show_message("Error", "No file selected.")
            
    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()
        
    def update_progress(self, value):
        self.progress_dialog.setValue(value)
        
    def on_audio_extraction_done(self, mp3_file_path):
        # Close the progress dialog after extraction is done
        self.progress_dialog.close()
        self.show_message("Success", f"Audio extracted and saved as: {mp3_file_path}")
        
        # Proceed to generate new voice using the extracted MP3
        new_mp3_file_path = mp3_file_path.replace("mp3", "_new_voice.mp3")
        
        self.generate_new_voice(mp3_file_path, new_mp3_file_path)
        
    def generate_new_voice(self, mp3_file, output_file):
        
        # Show progress dialog for voice generation
        self.progress_dialog = QProgressDialog("Generating new voice...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Please wait")
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.show()
        
        # Start API request in a separate thread
        self.voice_thread = VoiceGenerationThread(mp3_file, output_file)
        self.voice_thread.progress_signal.connect(self.update_progress)
        self.voice_thread.finished_signal.connect(self.on_voice_generation_done)
        self.voice_thread.start()
        
    def on_voice_generation_done(self, success, message):
        self.progress_dialog.close()
        if success:
            self.show_message("Success", "Voice generated successfully.")
        else:
            self.show_message("Error", f"Voice generation failed: {message}")
            
class AudioExtractionThread(QThread):
    progress_signal = pyqtSignal(int) # Signal to update progress
    finished_signal = pyqtSignal(str) # Signal to notify when finished
    
    def __init__(self, mp4_file, mp3_file):
        super().__init__()
        self.mp4_file = mp4_file
        self.mp3_file = mp3_file
        
    def run(self):
        try:
            # Extract audio from the video
            video = VideoFileClip(self.mp4_file)
            
            # Ensure audio exists in the video
            audio = video.audio
            
            if audio:
                # Wrtie the audio to the correct mp3 file path
                audio.write_audiofile(self.mp3_file, codec='mp3')
                
            self.progress_signal.emit(100)
            self.finished_signal.emit(self.mp3_file)
        except Exception as e:
            self.finished_signal.emit(str(e))
            
            
class VoiceGenerationThread(QThread):
    progress_signal = pyqtSignal(int) # Signal to update progress
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, mp3_file, output_file):
        super().__init__()
        self.mp3_file = mp3_file
        self.output_file = output_file
        
    def run(self):
        try:
            
            XI_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
            if not XI_API_KEY:
                self.finished_signal.emit(False, "API key not found. Please check your .env file.")
                return
            
            VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
            CHUNK_SIZE = 1024
            sts_url = f"https://api.elevenlabs.io/v1/speech-to-speech/{VOICE_ID}/stream"
            headers = {
                "Accept": "application/json",
                "xi-api-key": XI_API_KEY
            }
            data = {
                "model_id": "eleven_english_sts_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }

            # Send request to API
            with open(self.mp3_file, "rb") as audio_file:
                files = {"audio": audio_file}
                response = requests.post(sts_url, headers=headers, data=data, files=files, stream=True)
                
                if response.ok:
                    total_size = int(response.headers.get('content-length', 0))
                    bytes_downloaded = 0
                    
                    with open(self.output_file, "wb") as f:
                        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                            if chunk:
                                f.write(chunk)
                                bytes_downloaded += len(chunk)
                                progress = int(bytes_downloaded * 100 / total_size)
                                self.progress_signal.emit(progress)
                    self.finished_signal.emit(True, "Audio stream saved successfully.")
                else:
                    self.finished_signal.emit(False, response.text)
        except Exception as e:
            self.finished_signal.emit(False, str(e))
      
    
if __name__=='__main__':
    app = QApplication(sys.argv)
    window = AudioExtractor() # Run the Audio Extractor GUI
    window.show() # Show the widget
    sys.exit(app.exec_()) # Start the application event loop