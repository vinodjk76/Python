import whisper

file_path = "audio.mp3"  # Replace with your audio file path
model = whisper.load_model("base")  # You can choose other models like "tiny", "small", "medium", "large"
result = model.transcribe(file_path)["text"]

with open("transcription.txt", "w") as f:
    f.write(result)

print("\n Transcription completed. The text has been saved to 'transcription.txt'.",result )


