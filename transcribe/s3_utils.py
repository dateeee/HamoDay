import os
import boto3
from config import Config

class S3Utils:
    """
    S3操作をまとめたユーティリティクラス
    """
    def __init__(self, config: Config):
        self.config = config
        self.s3 = boto3.client('s3')

    def list_s3_files(self):
        response = self.s3.list_objects_v2(Bucket=self.config.BUCKET_NAME, Prefix=self.config.S3_OBJECT_PREFIX)
        files = []
        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.endswith('.wav'):
                files.append(key)
        return files

    def download_file(self, s3_key):
        filename = os.path.basename(s3_key)
        local_path = os.path.join(self.config.DOWNLOAD_DIR, filename)
        if os.path.exists(local_path):
            print(f"既に存在: {local_path} をスキップ")
            return local_path
        try:
            self.s3.download_file(self.config.BUCKET_NAME, s3_key, local_path)
            print(f"ダウンロード成功: {local_path}")
        except Exception as e:
            print(f"ダウンロード失敗: {s3_key} → {e}")
            return None
        return local_path
