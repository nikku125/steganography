import io
import time
from PIL import Image
from stego_engine import embed_data, extract_data
from crypto_module import encrypt, decrypt, compute_sha256
from blockchain_module import ledger

# Create a small dummy image
img = Image.new('RGB', (100, 100), color = 'red')
cover_image = img

secret_data = b"Hello Blockchain"
password = "testpassword"

# Prepare payload
payload_raw = b'\x00\x00' + secret_data
encrypted_payload = encrypt(payload_raw, password)

# Embed
stego_image = embed_data(cover_image, encrypted_payload)
img_buffer = io.BytesIO()
stego_image.save(img_buffer, format='PNG')
img_bytes = img_buffer.getvalue()

# Blockchain Record
tx_hash = compute_sha256(img_bytes)
block_data = {
    "action": "embed",
    "transaction_hash": tx_hash,
    "payload_size": len(encrypted_payload),
    "timestamp": time.time()
}
ledger.add_block(block_data)
print("Block added. Chain valid:", ledger.is_chain_valid())

# Extract
stego_file_bytes = img_bytes
tx_hash_2 = compute_sha256(stego_file_bytes)
is_verified = ledger.verify_transaction(tx_hash_2)
print("Transaction verified in blockchain:", is_verified)

extracted_enc = extract_data(stego_image)
decrypted, integrity = decrypt(extracted_enc, password)
print("Extraction success:", decrypted[2:] == secret_data, "Integrity:", integrity)
