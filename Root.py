import speech_recognition as sr  #Handles speech input
import sounddevice as sd  #Records audio from the microphone
from scipy.io.wavfile import write  #Saves recorded audio to a .wav file
import pyttsx3  #Text-to-speech engine for vocal responses
import time  #Used for timing pauses between actions
import random  #Used for selecting a random greeting
import whisper  #Model for speech-to-text
from langchain_ollama import ChatOllama  #Framework that is compatible with Ollama
from langchain_core.tools import tool  #Allows agent to use tools
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage  #Defines instructions and input for the agent
from langchain_community.document_loaders.csv_loader import CSVLoader  #Loads in the CSV

#initialize variables for wake word detection and audio recording
WAKE_WORD = "alfred"
FREQ = 44100
DURATION = 10

#initialize engine for text-to-speech
engine = pyttsx3.init()

#instantiate speech-to-text model
model = whisper.load_model("tiny")

# Wake word detection which starts recording audio
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

# Record user input
def record_audio():
    """Records 10 seconds of audio and saves it to 'recording.wav'."""
    print("Recording for 10 seconds...")
    recording = sd.rec(int(DURATION * FREQ), samplerate=FREQ, channels=2)
    sd.wait()  # Wait until recording is complete
    write("recording.wav", FREQ, recording)
    #print("Saved as recording.wav")
    audio_file = "recording.wav"
    return audio_file

# Speech-to-text
def speech_to_text(audio_file):
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    #print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    # return the recognized text
    return result.text

# Agent logic


# Text-to-speech || NEEDS WORK
def text_to_speech(text):
    engine.say("{text}")
    engine.runAndWait()

# Main function that connects all our components together
def main():
    while True:
        listen_for_wake_word()                        # 1. Listen for wake word
        speech_input = record_audio()                 # 2. Record user's spoken input and return it as a .wav file called 'speech_input'
        text_input = speech_to_text(speech_input)     # 3. Convert 'speech_input' to a text and save it as 'text_input'

        #quick test mid-loop
        #print(text_input)

        #agent call goes here                         # 4. agent call
        #text_to_speech(agent_response)               # 5. Speak Alfred's text response back to the user



if __name__ == "__main__":
    main()