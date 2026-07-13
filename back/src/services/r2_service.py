import logging
import boto3
from core.config import settings

logger = logging.getLogger(__name__)


class R2Service:
    def __init__(self):
        self._client = None
        self.bucket = settings.CLOUDFLARE_R2_BUCKET_NAME

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.R2_ENDPOINT_URL,
                aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
                region_name="auto",
            )
        return self._client

    def upload_file(self, file_bytes: bytes, filename: str) -> str:
        key = f"rag/{filename}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=file_bytes)
        return key

    def upload_exam_file(self, file_bytes: bytes, files_uuid: str, filename: str) -> str:
        key = f"files_for_exam/{files_uuid}/{filename}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=file_bytes)
        return key

    def generate_presigned_upload_url(
        self, files_uuid: str, filename: str, expires_in: int = 900
    ) -> dict:
        """
        Returns a presigned PUT URL so the browser can upload directly to R2,
        bypassing API Gateway/Lambda payload limits.
        """
        key = f"files_for_exam/{files_uuid}/{filename}"
        url = self.client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return {"filename": filename, "key": key, "url": url}

    def list_files_in_folder(self, prefix: str) -> list:
        response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return [
            {"key": obj["Key"], "filename": obj["Key"].split("/")[-1]}
            for obj in response.get("Contents", [])
        ]

    def download_file(self, s3_key: str) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=s3_key)
        return response["Body"].read()

    def delete_file(self, s3_key: str):
        self.client.delete_object(Bucket=self.bucket, Key=s3_key)


r2_service = R2Service()
