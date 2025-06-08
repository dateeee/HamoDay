import os
import whisper
import time
from config import Config

class Transcriber:
    """
    Whisperによる音声ファイルの文字起こしを担当するクラス
    """
    def __init__(self, config: Config):
        self.config = config

    def transcribe_wav(self, wav_path, model_name="large"):
        if not os.path.exists(wav_path):
            print(f"transcribe対象ファイルが存在しません: {wav_path}")
            return "", 0.0
        # Whisperモデルのロード
        try:
            model = whisper.load_model(model_name)
        except Exception as e:
            print(f"Whisperモデルのロードに失敗しました: {model_name}. エラー: {e}")
            return "", 0.0
        start = time.time()
        result = model.transcribe(wav_path, language='ja')
        elapsed = time.time() - start
        # 文字起こし結果の整形
        segments = result.get("segments")
        if segments:
            text = "\n".join([seg["text"].strip() for seg in segments])
        else:
            text = result["text"]
        return text, elapsed
