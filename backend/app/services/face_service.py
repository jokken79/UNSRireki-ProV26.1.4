"""
Face Detection and Cropping Service
Uses OpenCV for face detection in ID cards
Ported from JpkkenRirekisho12.24v1.0
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    """Convert image bytes to OpenCV format."""
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def detect_and_crop_face(image_bytes: bytes, padding: float = 0.3) -> Optional[bytes]:
    """
    Detect and crop face from an image (typically an ID card).

    Args:
        image_bytes: Raw image bytes
        padding: Padding ratio around the detected face (0.3 = 30%)

    Returns:
        Cropped face image as bytes, or None if no face found
    """
    try:
        image = load_image_from_bytes(image_bytes)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Load OpenCV's pre-trained Haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        if len(faces) == 0:
            # Try with different parameters
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,
                minNeighbors=3,
                minSize=(20, 20)
            )

        if len(faces) == 0:
            logger.warning("No face detected in image")
            return None

        # Use the largest face found (most likely the main photo)
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face

        # Add padding
        pad_w = int(w * padding)
        pad_h = int(h * padding)

        # Calculate new coordinates with padding
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(image.shape[1], x + w + pad_w)
        y2 = min(image.shape[0], y + h + pad_h)

        # Crop the face region
        face_crop = image[y1:y2, x1:x2]

        # Convert back to bytes
        face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
        face_pil = Image.fromarray(face_rgb)

        buffer = io.BytesIO()
        face_pil.save(buffer, format='PNG')

        logger.info(f"Face detected and cropped: {w}x{h} -> {x2-x1}x{y2-y1}")
        return buffer.getvalue()

    except Exception as e:
        logger.error(f"Error detecting/cropping face: {e}")
        return None


def crop_face_to_base64(image_bytes: bytes) -> Optional[str]:
    """
    Detect, crop face, and return as base64 encoded string.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Base64 encoded PNG string, or None if no face found
    """
    face_bytes = detect_and_crop_face(image_bytes)
    if face_bytes is None:
        return None

    return base64.b64encode(face_bytes).decode('utf-8')


def crop_face_to_data_url(image_bytes: bytes) -> Optional[str]:
    """
    Detect, crop face, and return as data URL.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Data URL string, or None if no face found
    """
    face_bytes = detect_and_crop_face(image_bytes)
    if face_bytes is None:
        return None

    b64 = base64.b64encode(face_bytes).decode('utf-8')
    return f"data:image/png;base64,{b64}"


def get_face_region(image_bytes: bytes) -> Optional[Tuple[int, int, int, int]]:
    """
    Get the bounding box of the detected face.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Tuple of (x, y, width, height) or None if no face found
    """
    try:
        image = load_image_from_bytes(image_bytes)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        if len(faces) == 0:
            return None

        # Return the largest face
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        return tuple(largest_face)

    except Exception as e:
        logger.error(f"Error getting face region: {e}")
        return None


def has_face(image_bytes: bytes) -> bool:
    """
    Check if an image contains a face.

    Args:
        image_bytes: Raw image bytes

    Returns:
        True if face detected, False otherwise
    """
    return get_face_region(image_bytes) is not None
