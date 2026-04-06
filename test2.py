import io
import time
from PIL import Image
from stego_engine import embed_data, extract_data
from crypto_module import encrypt, decrypt
import numpy as np

img = Image.new('RGB', (100, 100), color = 'red')
secret_data = b"Hello Blockchain Streamlit test"
password = "test"
payload = encrypt(b'\x00\x00' + secret_data, password)

stego_img = embed_data(img, payload)
buf = io.BytesIO()
stego_img.save(buf, format='PNG')
img_bytes = buf.getvalue()

stego_img2 = Image.open(io.BytesIO(img_bytes))
ext_payload = extract_data(stego_img2)
print("Payload matched?", payload == ext_payload)
print("Payload lengths:", len(payload), len(ext_payload))
dec, valid = decrypt(ext_payload, password)
print("Decrypted!", valid)
