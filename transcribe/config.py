import os
from dotenv import load_dotenv

# 設定やパスの管理
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common', '.env'))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'common', '.aws.env'))

BUCKET_NAME = os.getenv('BUCKET_NAME', 'hamoday')
S3_OBJECT_PREFIX = os.getenv('S3_OBJECT_PREFIX', 'audio/')
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')
TEXT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'texts')

# ディレクトリ作成ユーティリティ
def ensure_dirs():
    for d in [DOWNLOAD_DIR, TEXT_OUTPUT_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
