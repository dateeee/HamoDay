import os
import time
from config import ensure_dirs, TEXT_OUTPUT_DIR
from s3_utils import list_s3_files, download_file
from transcriber import transcribe_wav

# 2分おきにS3から音声をダウンロードし、文字起こししてtextsに保存するバッチ

def run_batch():
    ensure_dirs()
    while True:
        print("=== 文字起こしバッチ開始 ===")
        files = list_s3_files()
        for s3_key in files:
            local_wav = download_file(s3_key)
            if local_wav is None or not os.path.exists(local_wav):
                print(f"ファイルが存在しません: {local_wav}")
                continue
            text_filename = os.path.splitext(os.path.basename(local_wav))[0] + ".txt"
            text_path = os.path.join(TEXT_OUTPUT_DIR, text_filename)
            if os.path.exists(text_path):
                print(f"既に文字起こし済み: {text_path} をスキップ")
                continue
            text, elapsed = transcribe_wav(local_wav)
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"文字起こし完了: {text_path} (処理時間: {elapsed:.2f}秒)")
        print("=== 2分待機します ===")
        time.sleep(120)
