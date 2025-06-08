from batch_runner import BatchTranscriber
import config
import s3_utils
import transcriber

if __name__ == '__main__':
    conf = config.Config()
    s3u = s3_utils.S3Utils(conf)
    tr = transcriber.Transcriber(conf)
    batch = BatchTranscriber(s3u, tr, conf)
    batch.run()