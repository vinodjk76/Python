import speech_recognition as sr

def speech_1():
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Initializing... Please stay quiet for a moment.")
        # Adjust for background noise to improve accuracy
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("Ready! Start speaking...")
        
        try:
            # Listen for the user's input
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Transcribing...")
            
            # Convert speech to text using Google's engine
            text = recognizer.recognize_google(audio_data)
            print(f"You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

if __name__ == "__main__":
    speech_1()
