import whisper

model = whisper.load_model("tiny")

# normal .wav file
audio_path = r"C:\Users\tadsa\GitHub\capstone_project\speech_to_text_model\voice-sample.wav"

def speech_to_text(audio_file):
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
    return(result)