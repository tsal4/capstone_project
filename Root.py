import speech_recognition as sr       # Handles speech input
import sounddevice as sd              # Records audio from the microphone
from scipy.io.wavfile import write    # Saves recorded audio to a .wav file
import openai                         # Connects to OpenAI API for Whisper + GPT
import pyttsx3                        # Text-to-speech engine for vocal responses
import time                           # Used for timing pauses between actions
import random                         # Used for selecting a random greeting


# CONFIGURE THE SPECIFICS


WAKE_WORD = "alfred"      # Trigger word activates the assistant
FREQ = 44100              # Audio recording frequency
DURATION = 10             # Recording duration in seconds


# OpenAI API Key for securit & to monitor access to the data
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"


# STEP 1 — Wake Word Detection

def listen_for_wake_word():
    """Continuously listens through the microphone until the wake word is detected."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    print("Listening for wake word... say 'Alfred' to start recording.")
   
    greetings = [
        "Hello, I'm Alfred. How can I help you?",
        "Hi there, Alfred here. What can I do for you today?",
        "Greetings! This is Alfred. How may I assist you?",
        "Hey! I'm Alfred. How can I help you today?"
    ]
   
    while True:
        # Capture audio from microphone
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)       # Reduce background noise
            audio = recognizer.listen(source, phrase_time_limit=3)  # Listen for up to 3 seconds
       
        try:
            # Convert spoken audio to text using Google Speech Recognition
            text = recognizer.recognize_google(audio).lower()
            print(f"Heard: {text}")
           
            # Check if the wake word was said
            if WAKE_WORD in text:
                print("Wake word detected!")


                # NEW FEATURE: Randomized Voice Greeting

                engine = pyttsx3.init()
                greeting = random.choice(greetings)
                engine.say(greeting)
                engine.runAndWait()


                # Optional short pause before recording starts
                time.sleep(1.5)
                return


        except sr.UnknownValueError:
            # Speech was unclear or not recognized
            pass
        except sr.RequestError:
            # API request failed
            print("Speech recognition service error")


# STEP 2 — Record Audio


def record_audio():
    """Records 10 seconds of audio and saves it to 'recording.wav'."""
    print("Recording for 10 seconds...")
    recording = sd.rec(int(DURATION * FREQ), samplerate=FREQ, channels=2)
    sd.wait()  # Wait until recording is complete
    write("recording.wav", FREQ, recording)
    print("Saved as recording.wav")

# MAIN FUNCTION


def main():
    """Main loop that connects all steps into a continuous voice assistant pipeline."""
    while True:
        listen_for_wake_word()                       # 1. Wait for the wake word
        record_audio()                               # 2. Record user's voice
        user_text = speech_to_text("recording.wav")  # 3. Transcribe to text
        response = get_response(user_text)           # 4. Get GPT response
        speak(response)                              # 5. Speak the response aloud
        print("\nListening again...\n")              # Loop back to wait for wake word


# Entry point
if __name__ == "__main__":
    main()