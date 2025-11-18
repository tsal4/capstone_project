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

#SECOND ROOT THAT IS FULLY OFFLINE

#initialize variables for wake word detection and audio recording
WAKE_WORD = "alfred"
FREQ = 44100
DURATION = 10


#initialize engine for text-to-speech
engine = pyttsx3.init()


#instantiate speech-to-text model
stt_model = whisper.load_model("tiny")


#load the csv for the agent
loader = CSVLoader(file_path="courses-report.2025-10-16.csv")
data = loader.load()


#define the tool to the agent
@tool
def query_course_data(query: str) -> str:
    """Iterates through data object and returns docs that match the query parameter"""
    results = []
    for doc in data:
        if query.lower() in doc.page_content.lower():
            results.append(doc.page_content)
    return "\n".join(results)
tools = [query_course_data]


#instantiate the agent and bind the tool
alfred = ChatOllama(
    model="llama3.2:1b",
    temperature=0,
).bind_tools(tools)


# Wake word detection which starts recording audio
def listen_for_wake_word():
    """Continuously listens through the microphone until the wake word is detected."""
    #recognizer = sr.Recognizer()--------------------------
    #mic = sr.Microphone() --------------------------
    print("Listening for wake word... say 'Alfred' to start recording.")
   
    greetings = [
        "Hello, I'm Alfred. How can I help you?",
        "Hi there, Alfred here. What can I do for you today?",
        "Greetings! This is Alfred. How may I assist you?",
        "Hey! I'm Alfred. How can I help you today?"
    ]
   
    while True:
        # Capture audio from microphone
        #with mic as source:-----------------------------
           # recognizer.adjust_for_ambient_noise(source)       # Reduce background noise
           # audio = recognizer.listen(source, phrase_time_limit=3)  # Listen for up to 3 seconds
       #-------------------------------------------------------
        try:
            # Convert spoken audio to text using Google Speech Recognition
            #text = recognizer.recognize_google(audio).lower()    #this is onnline speech to text


            #Use whisper model to
           # audio_file = "wake.wav"


            recording = sd.rec(int(DURATION * FREQ), samplerate=FREQ, channels=2)
            sd.wait()
            write("wake.wav", FREQ, recording)


            text = speech_to_text("wake.wav").lower()




            print(f"Heard: {text}")
           
            # Check if the wake word was said
            if WAKE_WORD in text:
                print("Wake word detected!")




                # NEW FEATURE: Randomized Voice Greeting
                greeting = random.choice(greetings)
                engine.say(greeting)
                engine.runAndWait()




                # Optional short pause before recording starts
                time.sleep(1)
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
    mel = whisper.log_mel_spectrogram(audio, n_mels=stt_model.dims.n_mels).to(stt_model.device)


    # detect the spoken language
    _, probs = stt_model.detect_language(mel)
    #print(f"Detected language: {max(probs, key=probs.get)}")


    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(stt_model, mel, options)


    # return the recognized text
    return result.text


# Agent logic
def agent(user_input, agent, tools):
    ALFRED = agent
    #instantiate messages with instructions for the agent and the user input
    messages = [
        SystemMessage(
            content="You are a helpful assistant whose name is Alfred. You help students at John Carroll University by answering questions on Math, Computer Science, and Data Science course information." \
            "ALWAYS use the tool provided to answer the user's question. ALWAYS use the user's input as the parameter for the tool." \
            "ALWAYS use the data returned from the tool to form your response."
            "If the tool does not return anything, always answer with 'I do not understand the question, please ask again' and NEVER PROVIDE ANY OTHER INFORMATION." \
            "UNDER NO CIRCUMSTANCES should you ever answer questions that do not pertain to the course information." \
            "UNDER NO CIRCUMSTANCES should you ever use profanity."
            "When you give an answer, respond in clear sentences, not in raw CSV text."
        ),
        HumanMessage(content=user_input),
    ]
    #generate inital response
    response = ALFRED.invoke(messages)


    #if statement to make sure the agent uses the tool to access the data
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        tool = tools[0]
        if tool.name == tool_name:
            # Execute the tool with the arguments
            tool_result = tool.invoke(tool_args)


            # Add the tool result to the messages
            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                    name=tool_name,
                )
            )


            # Get final response after tool execution
            final_response = ALFRED.invoke(messages)
            final_response_content = final_response.content
            tools = response.tool_calls[0]["name"]
            return final_response_content


# Text-to-speech
def text_to_speech(text):
    engine.say("{text}")
    engine.runAndWait()


# Main function that connects all our components together
def main():
    while True:
        listen_for_wake_word()  # 1. Listen for wake word
        speech_input = record_audio()  # 2. Record user's spoken input and return it as a .wav file called 'speech_input'
        text_input = speech_to_text(speech_input)  # 3. Convert 'speech_input' to a text and save it as 'text_input'


        #quick print to test
        print(text_input)


        agent_response = agent(text_input, alfred, tools)  # 4. Feed the text_input into the Aflred and return Alfred's response saved as 'agent_response'


        #quick print to test
        print(agent_response)


        text_to_speech(agent_response)  # 5. Speak Alfred's response back to the user






if __name__ == "__main__":
    main()
