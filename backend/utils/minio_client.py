import aioboto3
import uuid
import os
from fastapi import UploadFile, HTTPException
from .minio_config import settings




class MinioClient:
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint = f"http://{settings.minio_endpoint}"
        self.bucket = settings.minio_bucket
    
    
    async def upload(self, file: UploadFile) -> str:
        """Загружает файл и возвращает его уникальное имя"""
        
        ext = self._validate_file(file)
        
        filename = f"{uuid.uuid4()}{ext}"
        
        content = await file.read()
        
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name='us-east-1'
        ) as client:
            await client.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=content,
                ContentType=file.content_type or "image/jpeg"
            )
        
        return filename
    
    
    async def get_url(self, filename: str) -> str:
        """Возвращает временную ссылку на файл (1 час)"""
        
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name='us-east-1'
        ) as client:
            url = await client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': filename},
                ExpiresIn=3600
            )
        
        return url
    
    
    async def delete(self, filename: str) -> None:
        """Удаляет файл"""
        
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name='us-east-1'
        ) as client:
            await client.delete_object(Bucket=self.bucket, Key=filename)
    
    
    async def exists(self, filename: str) -> bool:
        """Проверяет существование файла"""
        
        try:
            async with self.session.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                region_name='us-east-1'
            ) as client:
                await client.head_object(Bucket=self.bucket, Key=filename)
            return True
        except:
            return False
    
    
    def _validate_file(self, file: UploadFile) -> str:
        """Валидация файла"""
        
        if not file.filename:
            raise HTTPException(400, "No filename")
        
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.allowed_extensions:
            raise HTTPException(400, f"Invalid file extension. Allowed: {settings.allowed_extensions}")
        
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)
        
        if size > settings.max_file_size_bytes:
            raise HTTPException(400, f"File too large. Max: {settings.max_file_size_mb}MB")
        
        return ext



minio = MinioClient()