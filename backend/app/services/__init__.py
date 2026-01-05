"""
Services module for UNS Rirekisho Pro v26.1.4

Provides:
- PhotoService: Image compression and processing
- FaceService: Face detection using OpenCV
- OCRService: Text extraction using EasyOCR
"""

from .photo_service import PhotoService, photo_service
from .face_service import detect_and_crop_face, crop_face_to_base64
from .ocr_service import process_image, process_zairyu_card

__all__ = [
    'PhotoService',
    'photo_service',
    'detect_and_crop_face',
    'crop_face_to_base64',
    'process_image',
    'process_zairyu_card',
]
