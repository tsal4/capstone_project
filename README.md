# Alfred: the MCDS AI Voice Assistant

#### This Repository is for the Fall 2025 AI Chatbot Capstone Project.

#### By: Thaddeus Salwan, Steve Loya, Justin Lupton, Frank Freeman

Alfred is a fully functional Retrieval-Augmented Generation system with voice capabilites. Alfred utilizes user input to query data in order to generate a correct answer. Alfred is designed to be ran locally on a Raspberry Pi with a speakerphone and touchscreen display.

Features include:
- Wake Word Detection: Google Speech Recognition
- Speech-to-Text: OpenAI's Whisper Tiny ran locally
- RAG system:
  - LLM: Meta's LLaMa3.2 (1B parameters) ran locally with Ollama
  - Orchestated locally with LangChain
- Text-to-Speech: pyttsx3 library
