import os
from dotenv import load_dotenv

class Config:
    """
    設定やパスの管理を行うクラス
    """
    def __init__(self):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common', '.env'))
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common', '.aws.env'))
        self.BUCKET_NAME = os.getenv('BUCKET_NAME', 'hamoday')
        self.S3_OBJECT_PREFIX = os.getenv('S3_OBJECT_PREFIX', 'audio/')
        self.DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
        self.TEXT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'texts')
        # 録音ファイルの出力ディレクトリ
        self.WAVE_OUTPUT_DIR = os.getenv('WAVE_OUTPUT_DIR', os.path.join(os.path.dirname(__file__), 'recordings'))
        # 録音関連のパラメータ
        self.FORMAT = os.getenv('FORMAT', 'paInt16')
        self.CHANNELS = int(os.getenv('CHANNELS', 1))
        self.RATE = int(os.getenv('RATE', 44100))
        self.CHUNK = int(os.getenv('CHUNK', 1024))
        self.RECORD_SECONDS = int(os.getenv('RECORD_SECONDS', 60))

    def ensure_dirs(self):
        for d in [self.DOWNLOAD_DIR, self.TEXT_OUTPUT_DIR, self.WAVE_OUTPUT_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)
