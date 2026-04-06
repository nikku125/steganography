"""
Steganography Engine for the Steganography Tool.
Implements LSB (Least Significant Bit) steganography for hiding
and extracting encrypted data within images.
"""

import numpy as np
from PIL import Image
from utils import (
    bytes_to_bits, bits_to_bytes,
    int_to_bits, bits_to_int,
    calculate_capacity, HEADER_BITS
)

# Chunk size for processing (number of pixels per chunk)
CHUNK_SIZE = 10_000


def embed_data(cover_image: Image.Image, payload: bytes) -> Image.Image:
    """
    Embed encrypted payload into a cover image using LSB steganography.

    The data format embedded in the image:
        [32-bit payload length] [payload bytes as bits in LSBs]

    Each bit of the payload replaces the least significant bit of one
    color channel (R, G, or B) of one pixel, processed sequentially.

    Args:
        cover_image: The original PIL Image (will be converted to RGB).
        payload: The encrypted data bytes to embed.

    Returns:
        A new PIL Image with the payload hidden in its pixels.

    Raises:
        ValueError: If the payload is too large for the image.
    """
    # Ensure RGB mode
    img = cover_image.convert('RGB')
    capacity = calculate_capacity(img)

    if len(payload) > capacity:
        raise ValueError(
            f"Payload too large! Payload: {len(payload)} bytes, "
            f"Image capacity: {capacity} bytes. "
            f"Use a larger image or reduce payload size."
        )

    # Convert image to numpy array for efficient manipulation
    pixels = np.array(img)
    height, width, channels = pixels.shape

    # Flatten pixel array for sequential access: [R, G, B, R, G, B, ...]
    flat_pixels = pixels.flatten()

    # Build the full bit stream: length header + payload bits
    length_bits = int_to_bits(len(payload), HEADER_BITS)
    payload_bits = bytes_to_bits(payload)
    all_bits = length_bits + payload_bits

    total_bits = len(all_bits)

    # Embed bits into LSBs using chunk-based processing
    for chunk_start in range(0, total_bits, CHUNK_SIZE):
        chunk_end = min(chunk_start + CHUNK_SIZE, total_bits)
        chunk_bits = all_bits[chunk_start:chunk_end]

        for i, bit in enumerate(chunk_bits):
            pixel_index = chunk_start + i
            # Clear LSB and set to our bit
            flat_pixels[pixel_index] = (flat_pixels[pixel_index] & 0xFE) | bit

    # Reshape back to image dimensions
    stego_pixels = flat_pixels.reshape((height, width, channels))
    stego_image = Image.fromarray(stego_pixels.astype(np.uint8), 'RGB')

    return stego_image


def extract_data(stego_image: Image.Image) -> bytes:
    """
    Extract hidden payload from a stego image using LSB steganography.

    Reads the 32-bit length header first, then extracts exactly that
    many bytes of payload data from subsequent pixel LSBs.

    Args:
        stego_image: The PIL Image containing hidden data.

    Returns:
        The extracted payload bytes (still encrypted).

    Raises:
        ValueError: If the image doesn't contain valid hidden data
                    or the embedded length is corrupted.
    """
    # Ensure RGB mode
    img = stego_image.convert('RGB')
    pixels = np.array(img)
    flat_pixels = pixels.flatten()

    total_available_bits = len(flat_pixels)

    # --- Step 1: Extract the 32-bit length header ---
    if total_available_bits < HEADER_BITS:
        raise ValueError("Image too small to contain hidden data.")

    length_bits = []
    for i in range(HEADER_BITS):
        length_bits.append(flat_pixels[i] & 1)

    payload_length = bits_to_int(length_bits)

    # Sanity check on extracted length
    max_capacity = (total_available_bits - HEADER_BITS) // 8
    if payload_length <= 0 or payload_length > max_capacity:
        raise ValueError(
            "No valid hidden data found, or the data is corrupted. "
            "Make sure this image was created by this tool."
        )

    # --- Step 2: Extract payload bits using chunk-based processing ---
    total_payload_bits = payload_length * 8
    payload_bits = []

    for chunk_start in range(0, total_payload_bits, CHUNK_SIZE):
        chunk_end = min(chunk_start + CHUNK_SIZE, total_payload_bits)

        for i in range(chunk_start, chunk_end):
            pixel_index = HEADER_BITS + i
            payload_bits.append(flat_pixels[pixel_index] & 1)

    # Convert bits back to bytes
    payload = bits_to_bytes(payload_bits)

    return payload


def get_image_info(image: Image.Image) -> dict:
    """
    Get detailed information about an image for the UI.

    Args:
        image: The PIL Image to analyze.

    Returns:
        Dictionary with image metadata and capacity info.
    """
    img = image.convert('RGB')
    width, height = img.size
    capacity = calculate_capacity(img)

    return {
        'width': width,
        'height': height,
        'total_pixels': width * height,
        'channels': 3,
        'mode': img.mode,
        'capacity_bytes': capacity,
        'capacity_bits': capacity * 8,
    }
