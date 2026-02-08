"""
Image Upload Router - Cloudflare R2 Integration
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Header, Depends
from typing import Optional
import uuid
from datetime import datetime
import io
from sqlalchemy.ext.asyncio import AsyncSession

from app.models_sql.base import get_async_session
from app.models_sql import User
from app.services.auth_dependency_sql import get_current_user_sql

router = APIRouter(
    prefix="/v1/upload",
    tags=["Upload 📤"]
)


def init_r2_client():
    """Initialize R2 client using boto3"""
    try:
        import boto3
        from botocore.config import Config
        from app.config import settings
        
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        return s3_client
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="boto3 is not installed. Please run: pip install boto3"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize R2 client: {str(e)}"
        )


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_sql),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Upload image to Cloudflare R2 storage
    
    - **file**: Image file (JPEG, PNG, WEBP)
    
    Returns:
    - **url**: Public URL of uploaded image
    - **filename**: Generated filename in R2
    """
    
    # 1. User is already validated by get_current_user_sql dependency
    
    # 2. Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Allowed types: JPEG, PNG, WEBP"
        )
    
    # 3. Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    await file.seek(0, 2)  # Seek to end
    file_size = await file.tell()
    await file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large: {file_size / (1024*1024):.2f}MB. Maximum size: 10MB"
        )
    
    # 4. Generate unique filename
    file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"pets/{uuid.uuid4()}.{file_ext}"
    
    # 5. Upload to R2
    try:
        from app.config import settings
        
        # Check if R2 credentials are configured
        if not settings.R2_ACCESS_KEY_ID or not settings.R2_SECRET_ACCESS_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="R2 credentials not configured. Please add R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY to .env file"
            )
        
        if not settings.R2_PUBLIC_URL:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="R2_PUBLIC_URL not configured. Please add it to .env file"
            )
        
        # Initialize R2 client
        s3_client = init_r2_client()
        
        # Read file content
        file_content = await file.read()
        
        # Upload to R2
        s3_client.put_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=unique_filename,
            Body=file_content,
            ContentType=file.content_type,
            CacheControl='public, max-age=31536000'  # Cache for 1 year
        )
        
        # Generate public URL
        public_url = f"{settings.R2_PUBLIC_URL}/{unique_filename}"
        
        return {
            "success": True,
            "url": public_url,
            "filename": unique_filename,
            "size": file_size,
            "content_type": file.content_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.delete("/image")
async def delete_image(
    filename: str,
    current_user: dict = Depends(get_current_user_sql),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Delete image from R2 storage
    
    - **filename**: Filename in R2 (e.g., pets/uuid.jpg)
    """
    
    # User is already validated by get_current_user_sql dependency
    try:
        from app.config import settings
        
        s3_client = init_r2_client()
        
        # Delete from R2
        s3_client.delete_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=filename
        )
        
        return {
            "success": True,
            "message": f"Image {filename} deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )
