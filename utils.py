"""
Utility functions for the Steganography Tool.
Provides helpers for validation, conversion, and capacity calculations.
"""

import os
from PIL import Image

# Supported image formats for steganography (lossless formats only)
SUPPORTED_FORMATS = {'.png', '.bmp', '.tiff', '.tif'}

# Maximum file size for upload (50 MB)
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Header size: 32 bits for payload length
HEADER_BITS = 32


def validate_image_format(filename: str) -> bool:
    """Check if the file has a supported lossless image extension."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_FORMATS


def validate_file_size(data: bytes) -> bool:
    """Check if the file size is within the allowed limit."""
    return len(data) <= MAX_FILE_SIZE_BYTES


def calculate_capacity(image: Image.Image) -> int:
    """
    Calculate the maximum number of bytes that can be hidden in an image.
    Uses 1 bit per color channel (R, G, B) per pixel.
    Subtracts the header size (32 bits for length prefix).
    """
    width, height = image.size
    # Ensure image is in RGB mode for consistent channel count
    channels = 3  # R, G, B
    total_bits = width * height * channels
    available_bits = total_bits - HEADER_BITS
    return max(0, available_bits // 8)


def bytes_to_bits(data: bytes) -> list:
    """Convert a bytes object to a list of individual bits (0s and 1s)."""
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_bytes(bits: list) -> bytes:
    """Convert a list of bits (0s and 1s) back to a bytes object."""
    byte_list = []
    for i in range(0, len(bits), 8):
        byte_val = 0
        for bit in bits[i:i + 8]:
            byte_val = (byte_val << 1) | int(bit)
        byte_list.append(byte_val)
    return bytes(byte_list)


def int_to_bits(value: int, bit_count: int = 32) -> list:
    """Convert an integer to a fixed-length list of bits."""
    bits = []
    for i in range(bit_count - 1, -1, -1):
        bits.append((value >> i) & 1)
    return bits


def bits_to_int(bits: list) -> int:
    """Convert a list of bits back to an integer."""
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return value


def format_file_size(size_bytes: int) -> str:
    """Format a byte count into a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
