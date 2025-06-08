import os
import wave
import time
import threading
import queue
import pyaudio
import boto3
from dotenv import load_dotenv
from config import Config

# 録音処理・S3アップロード・全体管理を行う

class Recorder:
    """
    録音処理とファイル保存のみを担当
    """
    def __init__(self, config: Config):
        self.config = config
        self.p = pyaudio.PyAudio()
        # 録音ファイル保存ディレクトリがなければ作成
        if not os.path.exists(self.config.WAVE_OUTPUT_DIR):
            os.makedirs(self.config.WAVE_OUTPUT_DIR)

    def record(self):
        # オーディオストリームを開く
        stream = self.p.open(format=getattr(pyaudio, os.getenv('FORMAT', 'paInt16')),
                             channels=int(os.getenv('CHANNELS', 1)),
                             rate=int(os.getenv('RATE', 44100)),
                             input=True,
                             frames_per_buffer=int(os.getenv('CHUNK', 1024)))
        frames = []
        # 指定秒数分録音
        for _ in range(0, int(self.config.RATE / self.config.CHUNK * self.config.RECORD_SECONDS)):
            data = stream.read(self.config.CHUNK)
            frames.append(data)
        # ファイル名にタイムスタンプを付与
        filename = f'recording_{int(time.time())}.wav'
        filepath = os.path.join(self.config.WAVE_OUTPUT_DIR, filename)
        # WAVファイルとして保存
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.config.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(getattr(pyaudio, os.getenv('FORMAT', 'paInt16'))))
        wf.setframerate(self.config.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        # ストリームを閉じる
        stream.stop_stream()
        stream.close()
        return filepath, filename

    def terminate(self):
        # PyAudioのリソース解放
        self.p.terminate()

class S3Uploader:
    """
    S3クライアントの生成とアップロード処理のみを担当
    """
    def __init__(self, config: Config):
        self.config = config
        self.s3 = boto3.client('s3')

    def upload(self, filepath, filename):
        # S3のキーを生成
        s3_key = self.config.S3_OBJECT_PREFIX + filename
        try:
            # S3へファイルをアップロード
            self.s3.upload_file(filepath, self.config.BUCKET_NAME, s3_key)
            print(f'S3アップロード完了: {s3_key}')
            # アップロード後ローカルファイル削除
            os.remove(filepath)
            print(f'ローカルファイル削除: {filepath}')
        except Exception as e:
            print(f'S3アップロード失敗: {e}')

class RecordingManager:
    """
    各クラスを組み合わせて全体の流れを制御
    録音→S3アップロードを非同期で繰り返す
    """
    def __init__(self):
        self.config = Config()
        self.recorder = Recorder(self.config)
        self.uploader = S3Uploader(self.config)
        self.q = queue.Queue()  # 録音ファイルの受け渡し用キュー
        # アップロード専用スレッドを起動
        self.uploader_thread = threading.Thread(target=self.upload_worker, daemon=True)
        self.uploader_thread.start()

    def upload_worker(self):
        # キューからファイルを受け取りS3へアップロード
        while True:
            item = self.q.get()
            if item is None:
                break
            filepath, filename = item
            self.uploader.upload(filepath, filename)
            self.q.task_done()

    def run(self):
        # 録音→アップロードのメインループ
        count = 0
        try:
            while True:
                print(f'録音開始: {count+1}ファイル目')
                filepath, filename = self.recorder.record()
                print(f'録音保存: {filepath}')
                self.q.put((filepath, filename))  # キューに追加
                count += 1
        finally:
            # 終了処理
            self.recorder.terminate()
            self.q.put(None)
            self.uploader_thread.join()

