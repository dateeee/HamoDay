import os
import time
import config
import s3_utils
import transcriber

class BatchTranscriber:
    """
    S3から音声ファイルをダウンロードし、文字起こししてtextsに保存するバッチ処理クラス
    """
    def __init__(self, s3_utils, transcriber, config):
        self.s3_utils = s3_utils
        self.transcriber = transcriber
        self.config = config

    def run(self):
        self.config.ensure_dirs()
        while True:
            print("=== 文字起こしバッチ開始 ===")
            files = self.s3_utils.list_s3_files()
            for s3_key in files:
                local_wav = self.s3_utils.download_file(s3_key)
                if local_wav is None or not os.path.exists(local_wav):
                    print(f"ファイルが存在しません: {local_wav}")
                    continue
                text_filename = os.path.splitext(os.path.basename(local_wav))[0] + ".txt"
                text_path = os.path.join(self.config.TEXT_OUTPUT_DIR, text_filename)
                if os.path.exists(text_path):
                    print(f"既に文字起こし済み: {text_path} をスキップ")
                    continue
                text, elapsed = self.transcriber.transcribe_wav(local_wav)
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"文字起こし完了: {text_path} (処理時間: {elapsed:.2f}秒)")
            print("=== 2分待機します ===")
            time.sleep(120)
