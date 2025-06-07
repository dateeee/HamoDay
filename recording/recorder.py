import os
import wave
import time
import threading
import queue
import pyaudio
import boto3
from dotenv import load_dotenv

# 設定・パス管理
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common', '.env'))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common', '.aws.env'))

BUCKET_NAME = os.getenv('BUCKET_NAME', 'hamoday')
S3_OBJECT_PREFIX = os.getenv('S3_OBJECT_PREFIX', 'audio/')
FORMAT = getattr(pyaudio, os.getenv('FORMAT', 'paInt16'))
CHANNELS = int(os.getenv('CHANNELS', 1))
RATE = int(os.getenv('RATE', 44100))
CHUNK = int(os.getenv('CHUNK', 1024))
RECORD_SECONDS = int(os.getenv('RECORD_SECONDS', 60))
WAVE_OUTPUT_DIR = os.getenv('WAVE_OUTPUT_DIR', 'recordings')

# S3クライアント
s3 = boto3.client('s3')

def ensure_dirs():
    if not os.path.exists(WAVE_OUTPUT_DIR):
        os.makedirs(WAVE_OUTPUT_DIR)

def upload_worker(q):
    """
    S3へのアップロードを担当するワーカースレッド関数。
    キューからファイルパスとファイル名を受け取り、
    S3へアップロード後、ローカルファイルを削除する。
    アップロード失敗時はファイルを残す。
    """
    while True:
        filepath, filename = q.get()
        if filepath is None:
            break
        s3_key = S3_OBJECT_PREFIX + filename
        try:
            s3.upload_file(filepath, BUCKET_NAME, s3_key)
            print(f'S3アップロード完了: {s3_key}')
            os.remove(filepath)
            print(f'ローカルファイル削除: {filepath}')
        except Exception as e:
            print(f'S3アップロード失敗: {e}')
        finally:
            q.task_done()

def record_and_upload():
    """
    音声を録音し、録音ファイルをS3アップロード用キューに追加する関数。
    録音は指定秒数ごとに繰り返し行われる。
    """
    ensure_dirs()
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    count = 0
    q = queue.Queue()
    uploader = threading.Thread(target=upload_worker, args=(q,), daemon=True)
    uploader.start()
    try:
        while True:
            print(f'録音開始: {count+1}ファイル目')
            frames = []
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            filename = f'recording_{int(time.time())}.wav'
            filepath = os.path.join(WAVE_OUTPUT_DIR, filename)
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            print(f'録音保存: {filepath}')
            q.put((filepath, filename))
            count += 1
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        q.put((None, None))
        uploader.join()
