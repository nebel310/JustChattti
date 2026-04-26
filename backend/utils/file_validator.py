import os
import uuid
import time
import random
import string

from typing import List, Tuple
from fastapi import UploadFile, HTTPException




class FileValidator:
    """Валидатор файлов для загрузки"""
    
    ALLOWED_IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', 
        '.webp', '.bmp', '.tiff', '.svg'
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    def __init__(
        self,
        allowed_extensions: List[str] = None,
        max_size_bytes: int = None
    ):
        self.allowed_extensions = set(
            allowed_extensions or self.ALLOWED_IMAGE_EXTENSIONS
        )
        self.max_size_bytes = max_size_bytes or self.MAX_FILE_SIZE
    
    async def validate_file(
        self, 
        file: UploadFile,
        check_extension: bool = True,
        check_size: bool = True
    ) -> Tuple[str, str]:
        """
        Валидация файла
        
        Возвращает:
            Tuple[original_filename, extension]
        """
        
        if not file.filename:
            raise HTTPException(
                status_code=400, 
                detail="No filename provided"
            )
        
        original_filename = file.filename
        extension = os.path.splitext(original_filename)[1].lower()
        
        if check_extension and extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid file extension. "
                    f"Allowed: {', '.join(sorted(self.allowed_extensions))}"
                )
            )
        
        if check_size:
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > self.max_size_bytes:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"File too large. "
                        f"Max size: {self.max_size_bytes // (1024*1024)}MB"
                    )
                )
        
        return original_filename, extension
    
    def generate_unique_filename(
        self, 
        original_filename: str, 
        use_uuid: bool = True
    ) -> str:
        """Генерация уникального имени файла"""
        
        _, extension = os.path.splitext(original_filename)
        
        if use_uuid:
            return f"{uuid.uuid4()}{extension}"
        else:            
            timestamp = int(time.time())
            random_str = ''.join(
                random.choices(string.ascii_lowercase + string.digits, k=8)
            )
            return f"{timestamp}_{random_str}{extension}"


image_validator = FileValidator(
    allowed_extensions=[
        '.jpg', '.jpeg', '.png', '.gif', '.webp'
    ],
    max_size_bytes=5 * 1024 * 1024
)