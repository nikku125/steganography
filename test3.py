from PIL import Image
import io
from stego_engine import embed_data, extract_data
from crypto_module import encrypt, decrypt

img = Image.new('RGB', (100, 100), color = 'red')
secret_data = b"Streamlit upload simulation"
password = "testpassword"
payload = encrypt(b'\x00\x00' + secret_data, password)

stego_img = embed_data(img, payload)
buf = io.BytesIO()
stego_img.save(buf, format='PNG')
img_bytes = buf.getvalue()

class DummyUploadedFile(io.BytesIO):
    def getvalue(self):
        return super().getvalue()

stego_file = DummyUploadedFile(img_bytes)

# Streamlit code imitation
stego_image = Image.open(stego_file)
stego_image.load() # st.image might trigger load
stego_bytes = stego_file.getvalue()

ext_payload = extract_data(stego_image)
print("Payload exactly matches:", ext_payload == payload)
try:
    dec, val = decrypt(ext_payload, password)
    print("Decryption successful!", val)
except ValueError as e:
    print("Decryption Error:", str(e))
    stego_image_safe = Image.open(io.BytesIO(stego_bytes))
    ext_payload_safe = extract_data(stego_image_safe)
    print("Safe Payload exactly matches:", ext_payload_safe == payload)
    try:
        dec2, val2 = decrypt(ext_payload_safe, password)
        print("Safe Decryption successful!", val2)
    except:
        print("Safe Decryption also failed!")

