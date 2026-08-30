import os
from gtts import gTTS

# Telugu text input (can accept native script or English phonetics)
text = "నమస్కారం!  ఓం శుక్లాంబరధరం విష్ణుం శశివర్ణం చతుర్భుజమ్ । ప్రసన్నవదనం ధ్యాయేత్ సర్వవిఘ్నోపశాంతయే"

# Set the language to 'te' for Telugu
tts = gTTS(text=text, lang='te', slow=False)

# Save the generated audio file
output_file = "telugu_output.mp3"
tts.save(output_file)

print(f"Audio saved successfully as {output_file}")

# Play the audio file automatically (Windows example)
os.system(f"start {output_file}")
