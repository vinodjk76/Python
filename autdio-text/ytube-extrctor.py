import os
import yt_dlp
import whisper

def download_and_extract_audio(youtube_url, output_audio_path="audio"):
    """
    Downloads YouTube audio and uses FFmpeg to convert it into a clean MP3.
    """
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_audio_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False
    }
    
    print("Downloading and processing audio with FFmpeg...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    # yt-dlp automatically appends the extension
    return f"{output_audio_path}.mp3"

def transcribe_audio(audio_file_path, output_text_path="transcript.txt"):
    """
    Loads the extracted audio file into Whisper and generates a transcript text file.
    """
    print("Loading Whisper model (this may take a moment)...")
    # 'base' is quick and accurate. Use 'small' or 'medium' for better punctuation.
    model = whisper.load_model("base")
    
    print("Transcribing audio to text...")
    result = model.transcribe(audio_file_path)
    
    # Save the output text
    with open(output_text_path, "w", encoding="utf-8") as f:
        f.write(result["text"])
        
    print(f"Success! Transcript saved to {output_text_path}")
    return result["text"]

if __name__ == "__main__":
    # Replace with your target YouTube URL
    video_url = "https://youtu.be/JUpZyOhI9iY?si=aXXV7dNUxo7W-ysX"
    
    # 1. Download and convert audio using FFmpeg
    audio_file = download_and_extract_audio(video_url)
    
    # 2. Extract transcript text
    transcript = transcribe_audio(audio_file)
    
    # Clean up the audio file if you only want the text
    if os.path.exists(audio_file):
        os.remove(audio_file)
