import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from moviepy.editor import VideoFileClip
import whisper
from elevenlabs import generate, save

class AudioExtractor(QWidget):
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
            
            # Transcribe the audio to text
            transcript = self.transcribe_audio(mp3_file_path)
            print(f"Transcribed text: {transcript}")
            
            # Generate new audio with Eleven Labs voice
            new_mp3_file_path = mp3_file_path.replace("mp3", "_new_voice.mp3")
            self.generate_new_voice(transcript, new_mp3_file_path)
        else:
            print("No file selected.")
        
    def extract_audio_from_video(self, mp4_file, mp3_file):
        # Load the video file and extract audio
        try:
            video = VideoFileClip(mp4_file)
            audio = video.audio
            if audio:
                audio.write_audiofile(mp3_file, codec='mp3')
            else:
                print("No audio found in the video.")
        except Exception as e:
            print(f"An error occured: {e}")
            
    def transcribe_audio(self, mp3_file):
        # Using Whisper (from OpenAI) for local transcription
        try:
            model = whisper.load_model("base")
            result = model.transcribe(mp3_file)
            return result['text']
        except Exception as e:
            print(f"Transcription failed: {e}")
            return ""
        
    def generate_new_voice(self, text, output_file):
        # Use Eleven Labs to generate new voice
        try:
            api_key = "YOUR_ELEVEN_LABS_API_KEY" # Replace with your Eleven Labs API Key
            audio = generate(text=text, voice="Rachel", api_key=api_key)
            save(output_file, audio)
            print(f"New voice audio saved as: {output_file}")
        except Exception as e:
            print(f"Voice generation failed: {e}")
            
    
if __name__=='__main__':
    app = QApplication(sys.argv)
    ex = AudioExtractor() # Run the Audio Extractor GUI
    ex.show() # Show the widget
    sys.exit(app.exec_()) # Srart the application event loop