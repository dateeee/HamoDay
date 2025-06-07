import os
import boto3
from config import BUCKET_NAME, S3_OBJECT_PREFIX, DOWNLOAD_DIR

# S3クライアントの初期化
s3 = boto3.client('s3')

# S3から録音ファイル一覧（.wavのみ）を取得
def list_s3_files():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_OBJECT_PREFIX)
    files = []
    for obj in response.get('Contents', []):
        key = obj['Key']
        if key.endswith('.wav'):
            files.append(key)
    return files

# S3からファイルをダウンロード。既に存在する場合はスキップ
def download_file(s3_key):
    filename = os.path.basename(s3_key)
    local_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(local_path):
        print(f"既に存在: {local_path} をスキップ")
        return local_path
    try:
        s3.download_file(BUCKET_NAME, s3_key, local_path)
        print(f"ダウンロード成功: {local_path}")
    except Exception as e:
        print(f"ダウンロード失敗: {s3_key} → {e}")
        return None
    return local_path
