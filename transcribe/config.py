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

    def ensure_dirs(self):
        for d in [self.DOWNLOAD_DIR, self.TEXT_OUTPUT_DIR]:
            if not os.path.exists(d):
                os.makedirs(d)
