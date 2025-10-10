"""
File service for handling file uploads, storage, and management.
"""
import os
import uuid
import mimetypes
from typing import Dict, Optional
# import librosa  # Temporarily commented out
import wave
from app.config import settings


class FileService:
    """Service for handling file operations."""
    
    def __init__(self):
        """Initialize file service and ensure upload directories exist."""
        self.upload_folder = settings.upload_folder
        self._ensure_upload_directories()
    
    def _ensure_upload_directories(self):
        """Create upload directories if they don't exist."""
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(os.path.join(self.upload_folder, "resumes"), exist_ok=True)
        os.makedirs(os.path.join(self.upload_folder, "voice"), exist_ok=True)
    
    def save_file(
        self, 
        file_content: bytes, 
        original_filename: str, 
        user_id: int, 
        file_type: str = "resume"
    ) -> Dict[str, str]:
        """
        Save uploaded file to filesystem.
        
        Args:
            file_content: Raw file bytes
            original_filename: Original filename from upload
            user_id: ID of user uploading file
            file_type: Type of file ('resume' or 'voice')
            
        Returns:
            Dictionary with file information
            
        Raises:
            Exception: If file save fails
        """
        try:
            # Generate unique filename
            file_extension = self._get_file_extension(original_filename)
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Create user-specific directory
            user_dir = os.path.join(self.upload_folder, file_type, str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            
            # Full file path
            file_path = os.path.join(user_dir, unique_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return {
                "stored_filename": unique_filename,
                "file_path": file_path,
                "user_dir": user_dir,
                "file_extension": file_extension
            }
            
        except Exception as e:
            raise Exception(f"Failed to save file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from filesystem.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            File information dictionary or None
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            stat_info = os.stat(file_path)
            return {
                "file_path": file_path,
                "file_size": stat_info.st_size,
                "mime_type": self._get_mime_type(file_path),
                "exists": True
            }
        except Exception:
            return None
    
    def get_audio_duration(self, file_path: str) -> Optional[float]:
        """
        Get duration of audio file in seconds.

        Args:
            file_path: Path to audio file

        Returns:
            Duration in seconds or None if failed
        """
        try:
            # Try with wave module for WAV files
            try:
                with wave.open(file_path, 'r') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration = frames / float(rate)
                    return round(duration, 2)
            except:
                # For other audio formats, try to get basic file info
                # Return a default duration if we can't determine it
                try:
                    import subprocess
                    result = subprocess.run(
                        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                         '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        duration = float(result.stdout.strip())
                        return round(duration, 2)
                except:
                    pass
                # If all else fails, return None (duration check will be skipped)
                return None
        except Exception:
            return None
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename."""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type of file."""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    def cleanup_user_files(self, user_id: int) -> bool:
        """
        Clean up all files for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            import shutil
            
            # Clean up resume files
            resume_dir = os.path.join(self.upload_folder, "resumes", str(user_id))
            if os.path.exists(resume_dir):
                shutil.rmtree(resume_dir)
            
            # Clean up voice files
            voice_dir = os.path.join(self.upload_folder, "voice", str(user_id))
            if os.path.exists(voice_dir):
                shutil.rmtree(voice_dir)
            
            return True
        except Exception:
            return False
    
    def get_user_storage_usage(self, user_id: int) -> Dict:
        """
        Calculate storage usage for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Storage usage information
        """
        try:
            total_size = 0
            file_count = 0
            
            # Check resume files
            resume_dir = os.path.join(self.upload_folder, "resumes", str(user_id))
            if os.path.exists(resume_dir):
                for root, dirs, files in os.walk(resume_dir):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except:
                            continue
            
            # Check voice files
            voice_dir = os.path.join(self.upload_folder, "voice", str(user_id))
            if os.path.exists(voice_dir):
                for root, dirs, files in os.walk(voice_dir):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except:
                            continue
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count
            }
            
        except Exception:
            return {
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "file_count": 0
            }