import time
import subprocess
import wave
import numpy as np
from pathlib import Path
from faster_whisper import WhisperModel

# ===== Config =====
FRAME_MS = 30
SILENCE_THRESHOLD = 120
END_SILENCE_MS = 800
MIN_SPEECH_MS = 300
MAX_RECORDING_MS = 15000
TEMP_WAV = Path("/tmp/recording.wav")
PREF_SAMPLE_RATE = 16000
PREF_CHANNELS = 1
MIC_TARGET = None

# ===== Recording helpers =====
def _spawn_pw_cat_record(rate, channels, target):
    cmd = [
        "pw-cat", "--record", "-",
        "--format", "s16",
        "--rate", str(rate),
        "--channels", str(channels)
    ]
    if target:
        cmd += ["--target", str(target)]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def _select_record_pipeline(target):
    attempts = [
        (PREF_SAMPLE_RATE, PREF_CHANNELS),
        (PREF_SAMPLE_RATE, 2),
        (48000, PREF_CHANNELS),
        (48000, 2),
    ]
    for rate, ch in attempts:
        proc = _spawn_pw_cat_record(rate, ch, target)
        bytes_per_sample = 2
        frame_bytes = int(rate * FRAME_MS / 1000) * bytes_per_sample * ch
        chunk = proc.stdout.read(frame_bytes)
        if chunk:
            return proc, rate, ch, chunk, ""
        proc.terminate()
    return None, None, None, None, "No working pw-cat configuration found"

def record_with_vad(timeout_seconds=30):
    """Record audio until silence is detected (VAD)."""
    print("🎤 Listening... (speak now)")
    proc, rate, ch, first_chunk, err = _select_record_pipeline(MIC_TARGET)
    if not proc:
        print(f"❌ {err}")
        return None, None, None

    bytes_per_sample = 2
    frame_bytes = int(rate * FRAME_MS / 1000) * bytes_per_sample * ch
    audio_buffer = bytearray()

    # Noise calibration
    noise_samples = []
    if first_chunk:
        s = np.frombuffer(first_chunk, dtype=np.int16).astype(np.float32)
        noise_samples.append(float(np.sqrt(np.mean(s * s))))
    noise_floor = float(np.median(noise_samples)) if noise_samples else 50.0
    threshold = max(SILENCE_THRESHOLD, noise_floor * 1.8)

    is_speaking, silence_ms, speech_ms, total_ms = False, 0, 0, 0
    start = time.time()

    if first_chunk is not None:
        samples = np.frombuffer(first_chunk, dtype=np.int16).astype(np.float32)
        rms = float(np.sqrt(np.mean(samples * samples)))
        if rms > threshold:
            is_speaking = True
            speech_ms = FRAME_MS
            audio_buffer.extend(first_chunk)

    while True:
        if (time.time() - start) > timeout_seconds:
            break
        chunk = proc.stdout.read(frame_bytes)
        if not chunk:
            break
        samples = np.frombuffer(chunk, dtype=np.int16).astype(np.float32)
        rms = float(np.sqrt(np.mean(samples * samples)))
        if is_speaking:
            audio_buffer.extend(chunk)
            if rms < threshold:
                silence_ms += FRAME_MS
            else:
                silence_ms = 0
                speech_ms += FRAME_MS
            if silence_ms >= END_SILENCE_MS and speech_ms >= MIN_SPEECH_MS:
                break
            elif total_ms >= MAX_RECORDING_MS:
                break
        else:
            if rms > threshold:
                is_speaking = True
                speech_ms = FRAME_MS
                silence_ms = 0
                audio_buffer.extend(chunk)
        total_ms += FRAME_MS

    proc.terminate()
    if audio_buffer and len(audio_buffer) > 1000:
        return bytes(audio_buffer), rate, ch
    return None, None, None

def save_wav(audio_data, filepath, sample_rate, channels):
    with wave.open(str(filepath), 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

# ===== Transcription =====
def transcribe_audio(whisper_model, audio_path):
    print("🧠 Transcribing...")
    try:
        segments, _ = whisper_model.transcribe(
            str(audio_path),
            language="en",
            beam_size=1,
            best_of=1,
            temperature=0.0,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=200
            )
        )
        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip() if text else None
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None

# ===== Example usage =====
if __name__ == "__main__":
    whisper = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    audio_data, rate, ch = record_with_vad()
    if audio_data:
        save_wav(audio_data, TEMP_WAV, sample_rate=rate, channels=ch)
        text = transcribe_audio(whisper, TEMP_WAV)
        print(f"📝 You said: \"{text}\"" if text else "❓ No speech detected")
