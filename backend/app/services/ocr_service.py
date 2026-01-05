"""
OCR Service using EasyOCR for Japanese and English text recognition
Ported from JpkkenRirekisho12.24v1.0
"""

import numpy as np
from PIL import Image
import io
import re
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# EasyOCR reader - lazy loaded
_reader = None


def get_reader():
    """Get or initialize the EasyOCR reader."""
    global _reader
    if _reader is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR reader (ja, en)...")
            _reader = easyocr.Reader(['ja', 'en'], gpu=False)
            logger.info("EasyOCR reader initialized.")
        except ImportError:
            logger.error("EasyOCR not installed. Run: pip install easyocr")
            return None
    return _reader


def process_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Process an image and extract text using EasyOCR.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Dictionary containing extracted text and structured data
    """
    reader = get_reader()
    if reader is None:
        return {"error": "EasyOCR not available", "raw_text": "", "lines": [], "extracted_data": {}}

    try:
        # Convert bytes to numpy array
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image)

        # Run OCR
        results = reader.readtext(image_np)

        # Extract all text
        all_text = ' '.join([text for (_, text, _) in results])

        # Try to extract structured data
        extracted_data = extract_structured_data(results)

        return {
            "raw_text": all_text,
            "lines": [{"text": text, "confidence": float(conf)} for (_, text, conf) in results],
            "extracted_data": extracted_data
        }

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return {"error": str(e), "raw_text": "", "lines": [], "extracted_data": {}}


def extract_structured_data(ocr_results: List) -> Dict[str, Any]:
    """
    Extract structured data from OCR results.
    Attempts to find common fields in Zairyu cards and Rirekisho.
    """
    all_text = ' '.join([text for (_, text, _) in ocr_results])
    data = {}

    # Name patterns (Japanese)
    # Look for katakana names (common in Zairyu cards)
    katakana_pattern = r'[ァ-ヶー]{2,}\s*[ァ-ヶー]{2,}'
    katakana_match = re.search(katakana_pattern, all_text)
    if katakana_match:
        data['nameFurigana'] = katakana_match.group().strip()

    # Birth date patterns
    date_patterns = [
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',
    ]

    for pattern in date_patterns:
        match = re.search(pattern, all_text)
        if match:
            year, month, day = match.groups()
            data['birthDate'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            try:
                birth = datetime(int(year), int(month), int(day))
                today = datetime.now()
                age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
                data['age'] = age
            except ValueError:
                pass
            break

    # Nationality patterns
    nationality_keywords = {
        'ベトナム': 'Vietnam',
        'VIET NAM': 'Vietnam',
        'VIETNAM': 'Vietnam',
        '中国': 'China',
        'CHINA': 'China',
        'フィリピン': 'Philippines',
        'PHILIPPINES': 'Philippines',
        'インドネシア': 'Indonesia',
        'INDONESIA': 'Indonesia',
        'ミャンマー': 'Myanmar',
        'MYANMAR': 'Myanmar',
        'ネパール': 'Nepal',
        'NEPAL': 'Nepal',
        'タイ': 'Thailand',
        'THAILAND': 'Thailand',
        'ブラジル': 'Brazil',
        'BRAZIL': 'Brazil',
        'ペルー': 'Peru',
        'PERU': 'Peru',
    }

    for keyword, nationality in nationality_keywords.items():
        if keyword in all_text.upper():
            data['nationality'] = nationality
            break

    # Gender patterns
    if '男' in all_text or 'MALE' in all_text.upper():
        data['gender'] = '男性'
    elif '女' in all_text or 'FEMALE' in all_text.upper():
        data['gender'] = '女性'

    # Residence card number pattern (在留カード番号)
    # Format: AA12345678BB
    card_pattern = r'[A-Z]{2}\d{8}[A-Z]{2}'
    card_match = re.search(card_pattern, all_text.upper())
    if card_match:
        data['residenceCardNo'] = card_match.group()

    # Visa type patterns
    visa_types = [
        '技能実習', '特定技能', '技術・人文知識・国際業務',
        '留学', '家族滞在', '永住者', '定住者', '日本人の配偶者等',
        '技術', '人文知識', '国際業務', '特定活動'
    ]
    for visa in visa_types:
        if visa in all_text:
            data['visaType'] = visa
            break

    # Expiry date (在留期間満了日)
    expiry_keywords = ['満了', '期限', 'EXPIRY', 'UNTIL', '有効期限']
    for i, (_, text, _) in enumerate(ocr_results):
        for keyword in expiry_keywords:
            if keyword in text.upper():
                # Look at next few items for a date
                for j in range(i+1, min(i+4, len(ocr_results))):
                    potential_date = ocr_results[j][1]
                    for pattern in date_patterns:
                        match = re.search(pattern, potential_date)
                        if match:
                            year, month, day = match.groups()
                            data['visaExpiry'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            break
                    if 'visaExpiry' in data:
                        break
                break

    # Address patterns (Japanese postal code + address)
    postal_pattern = r'〒?\s*(\d{3})[ー\-]?(\d{4})'
    postal_match = re.search(postal_pattern, all_text)
    if postal_match:
        data['postalCode'] = f"{postal_match.group(1)}-{postal_match.group(2)}"

    return data


def process_zairyu_card(image_bytes: bytes) -> Dict[str, Any]:
    """
    Specifically process a Zairyu (residence) card.
    """
    result = process_image(image_bytes)
    result['document_type'] = 'zairyu_card'
    return result


def process_rirekisho(image_bytes: bytes) -> Dict[str, Any]:
    """
    Process a Rirekisho (resume) document.
    """
    result = process_image(image_bytes)
    result['document_type'] = 'rirekisho'
    return result


def extract_text_only(image_bytes: bytes) -> str:
    """
    Extract only the text from an image.

    Args:
        image_bytes: Raw image bytes

    Returns:
        Extracted text as string
    """
    result = process_image(image_bytes)
    return result.get('raw_text', '')
