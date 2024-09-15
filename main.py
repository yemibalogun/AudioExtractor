import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from moviepy.editor import VideoFileClip

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
    
if __name__=='__main__':
    app = QApplication(sys.argv)
    ex = AudioExtractor() # Run the Audio Extractor GUI
    ex.show() # Show the widget
    sys.exit(app.exec_()) # Srart the application event loop