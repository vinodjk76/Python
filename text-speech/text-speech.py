import os
from gtts import gTTS

# Text to be converted
text = "Hello! This is a natural sounding text to speech example using Google API. vinod"

# Generate the audio (lang='en' for English)
tts = gTTS(text=text, lang='en', slow=False)

# Save the audio file
output_file = "google_output.mp3"
tts.save(output_file)

print(f"Audio saved successfully as {output_file}")

# Optional: Play the audio file automatically using the system default player
os.system(f"start {output_file}")  # For Windows
# os.system(f"open {output_file}")   # For macOS
# os.system(f"xdg-open {output_file}") # For Linux
