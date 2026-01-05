"""
Photo Service for automatic compression and processing
Ported from JPUNS-Claude.6.5.0
"""
from PIL import Image
import io
import base64
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class PhotoService:
    """Service for photo compression and processing"""

    @staticmethod
    def compress_photo(
        photo_data_url: str,
        max_width: int = 800,
        max_height: int = 1000,
        quality: int = 85
    ) -> str:
        """
        Compress photo to reduce size while maintaining quality

        Args:
            photo_data_url: Data URL with base64 encoded image (e.g., "data:image/jpeg;base64,...")
            max_width: Maximum width in pixels (default: 800)
            max_height: Maximum height in pixels (default: 1000)
            quality: JPEG quality 1-100 (default: 85, higher = better quality)

        Returns:
            Compressed photo as data URL string
        """
        try:
            # Validate input
            if not photo_data_url or not photo_data_url.startswith('data:image'):
                logger.warning("Invalid photo data URL format")
                return photo_data_url

            # Parse data URL: "data:image/jpeg;base64,<base64_data>"
            parts = photo_data_url.split(',', 1)
            if len(parts) != 2:
                logger.warning("Could not split data URL into prefix and data")
                return photo_data_url

            prefix, b64_data = parts

            # Decode base64 to bytes
            try:
                decoded = base64.b64decode(b64_data)
            except Exception as e:
                logger.error(f"Failed to decode base64 image data: {e}")
                return photo_data_url

            # Open image with PIL
            image = Image.open(io.BytesIO(decoded))

            # Convert to RGB if necessary (handle transparency)
            if image.mode in ('RGBA', 'P', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if 'A' in image.mode:
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # Get original dimensions and size
            original_width, original_height = image.size
            original_size = len(decoded)

            # Calculate new size maintaining aspect ratio
            if original_width > max_width or original_height > max_height:
                ratio = min(max_width / original_width, max_height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)

                # Resize with high-quality Lanczos algorithm
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(
                    f"Resized image from {original_width}x{original_height} "
                    f"to {new_width}x{new_height}"
                )

            # Compress to JPEG with quality optimization
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            compressed_data = output.getvalue()
            compressed_size = len(compressed_data)

            # Calculate compression statistics
            compression_ratio = (1 - compressed_size / original_size) * 100
            logger.info(
                f"Compressed photo: {original_size:,} bytes -> {compressed_size:,} bytes "
                f"({compression_ratio:.1f}% reduction)"
            )

            # Re-encode to base64
            compressed_b64 = base64.b64encode(compressed_data).decode('ascii')

            return f"data:image/jpeg;base64,{compressed_b64}"

        except Exception as e:
            logger.error(f"Error compressing photo: {e}", exc_info=True)
            return photo_data_url

    @staticmethod
    def compress_bytes(
        image_bytes: bytes,
        max_width: int = 800,
        max_height: int = 1000,
        quality: int = 85
    ) -> bytes:
        """
        Compress photo bytes directly.

        Args:
            image_bytes: Raw image bytes
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            quality: JPEG quality 1-100

        Returns:
            Compressed image bytes
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB
            if image.mode in ('RGBA', 'P', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if 'A' in image.mode:
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize if needed
            original_width, original_height = image.size
            if original_width > max_width or original_height > max_height:
                ratio = min(max_width / original_width, max_height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Compress
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            return output.getvalue()

        except Exception as e:
            logger.error(f"Error compressing photo bytes: {e}")
            return image_bytes

    @staticmethod
    def validate_photo_size(photo_data_url: str, max_size_mb: int = 5) -> bool:
        """
        Validate photo size is within acceptable limits.
        """
        if not photo_data_url or not photo_data_url.startswith('data:image'):
            return True

        parts = photo_data_url.split(',', 1)
        if len(parts) != 2:
            return True

        try:
            decoded = base64.b64decode(parts[1])
            size_mb = len(decoded) / (1024 * 1024)
            return size_mb <= max_size_mb
        except Exception:
            return False

    @staticmethod
    def get_photo_dimensions(photo_data_url: str) -> Optional[Tuple[int, int]]:
        """Get photo dimensions (width, height)."""
        if not photo_data_url or not photo_data_url.startswith('data:image'):
            return None

        parts = photo_data_url.split(',', 1)
        if len(parts) != 2:
            return None

        try:
            decoded = base64.b64decode(parts[1])
            image = Image.open(io.BytesIO(decoded))
            return image.size
        except Exception:
            return None

    @staticmethod
    def get_photo_info(photo_data_url: str) -> Optional[dict]:
        """Get comprehensive photo information."""
        if not photo_data_url or not photo_data_url.startswith('data:image'):
            return None

        parts = photo_data_url.split(',', 1)
        if len(parts) != 2:
            return None

        try:
            prefix, b64_data = parts
            decoded = base64.b64decode(b64_data)
            image = Image.open(io.BytesIO(decoded))

            format_match = prefix.split(':')[1].split(';')[0]
            image_format = format_match.split('/')[1].upper()

            return {
                'format': image_format,
                'mode': image.mode,
                'dimensions': image.size,
                'width': image.size[0],
                'height': image.size[1],
                'size_bytes': len(decoded),
                'size_mb': len(decoded) / (1024 * 1024),
                'size_kb': len(decoded) / 1024,
            }
        except Exception as e:
            logger.error(f"Error getting photo info: {e}")
            return None

    @staticmethod
    def bytes_to_data_url(image_bytes: bytes, mime_type: str = 'image/jpeg') -> str:
        """Convert image bytes to data URL."""
        b64 = base64.b64encode(image_bytes).decode('ascii')
        return f"data:{mime_type};base64,{b64}"

    @staticmethod
    def data_url_to_bytes(data_url: str) -> Optional[bytes]:
        """Convert data URL to bytes."""
        if not data_url or not data_url.startswith('data:'):
            return None

        parts = data_url.split(',', 1)
        if len(parts) != 2:
            return None

        try:
            return base64.b64decode(parts[1])
        except Exception:
            return None


# Global singleton instance
photo_service = PhotoService()
