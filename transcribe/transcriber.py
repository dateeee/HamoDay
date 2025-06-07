import os
import whisper
import time
from config import TEXT_OUTPUT_DIR

# wavファイルをWhisperで文字起こしし、文ごとに改行して返す
# また、処理にかかった時間（秒）も返す
def transcribe_wav(wav_path, model_name="large"):
    if not os.path.exists(wav_path):
        print(f"transcribe対象ファイルが存在しません: {wav_path}")
        return "", 0.0
    model = whisper.load_model(model_name)
    start = time.time()
    result = model.transcribe(wav_path, language='ja')
    elapsed = time.time() - start
    segments = result.get("segments")
    if segments:
        text = "\n".join([seg["text"].strip() for seg in segments])
    else:
        text = result["text"]
    return text, elapsed
