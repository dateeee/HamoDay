import os
import wave
import time
import threading
import queue
import pyaudio
import boto3
from dotenv import load_dotenv

class ConfigLoader:
    """
    設定ファイルの読み込みと環境変数の取得を一元管理
    """
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        load_dotenv(os.path.join(base_dir, 'common', '.env'))
        load_dotenv(os.path.join(base_dir, 'common', '.aws.env'))
        self.bucket_name = os.getenv('BUCKET_NAME', 'hamoday')
        self.s3_object_prefix = os.getenv('S3_OBJECT_PREFIX', 'audio/')
        self.format = getattr(pyaudio, os.getenv('FORMAT', 'paInt16'))
        self.channels = int(os.getenv('CHANNELS', 1))
        self.rate = int(os.getenv('RATE', 44100))
        self.chunk = int(os.getenv('CHUNK', 1024))
        self.record_seconds = int(os.getenv('RECORD_SECONDS', 60))
        self.wave_output_dir = os.getenv('WAVE_OUTPUT_DIR', 'recordings')

class Recorder:
    """
    録音処理とファイル保存のみを担当
    """
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.p = pyaudio.PyAudio()
        if not os.path.exists(self.config.wave_output_dir):
            os.makedirs(self.config.wave_output_dir)

    def record(self):
        stream = self.p.open(format=self.config.format,
                             channels=self.config.channels,
                             rate=self.config.rate,
                             input=True,
                             frames_per_buffer=self.config.chunk)
        frames = []
        for _ in range(0, int(self.config.rate / self.config.chunk * self.config.record_seconds)):
            data = stream.read(self.config.chunk)
            frames.append(data)
        filename = f'recording_{int(time.time())}.wav'
        filepath = os.path.join(self.config.wave_output_dir, filename)
        wf = wave.open(filepath, 'wb')
        wf.setnchannels(self.config.channels)
        wf.setsampwidth(self.p.get_sample_size(self.config.format))
        wf.setframerate(self.config.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        stream.stop_stream()
        stream.close()
        return filepath, filename

    def terminate(self):
        self.p.terminate()

class S3Uploader:
    """
    S3クライアントの生成とアップロード処理のみを担当
    """
    def __init__(self, config: ConfigLoader):
        self.config = config
        self.s3 = boto3.client('s3')

    def upload(self, filepath, filename):
        s3_key = self.config.s3_object_prefix + filename
        try:
            self.s3.upload_file(filepath, self.config.bucket_name, s3_key)
            print(f'S3アップロード完了: {s3_key}')
            os.remove(filepath)
            print(f'ローカルファイル削除: {filepath}')
        except Exception as e:
            print(f'S3アップロード失敗: {e}')

class RecordingManager:
    """
    各クラスを組み合わせて全体の流れを制御
    """
    def __init__(self):
        self.config = ConfigLoader()
        self.recorder = Recorder(self.config)
        self.uploader = S3Uploader(self.config)
        self.q = queue.Queue()
        self.uploader_thread = threading.Thread(target=self.upload_worker, daemon=True)
        self.uploader_thread.start()

    def upload_worker(self):
        while True:
            item = self.q.get()
            if item is None:
                break
            filepath, filename = item
            self.uploader.upload(filepath, filename)
            self.q.task_done()

    def run(self):
        count = 0
        try:
            while True:
                print(f'録音開始: {count+1}ファイル目')
                filepath, filename = self.recorder.record()
                print(f'録音保存: {filepath}')
                self.q.put((filepath, filename))
                count += 1
        finally:
            self.recorder.terminate()
            self.q.put(None)
            self.uploader_thread.join()

if __name__ == '__main__':
    manager = RecordingManager()
    manager.run()
