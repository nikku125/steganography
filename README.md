# Steganography Tool – Secure Web-Based Data Hiding & Extraction System

A cybersecurity tool that enables users to **hide secret data inside images** using advanced steganographic techniques, protected by **military-grade encryption**.

## 🔐 Features

- **LSB Steganography** – Embeds data in the least significant bits of image pixels, making changes invisible to the human eye
- **AES-128 Encryption** – Protects hidden data with industry-standard symmetric encryption (CBC mode)
- **SHA-256 Integrity Verification** – Detects tampering or corruption of hidden data
- **PBKDF2 Key Derivation** – Derives strong encryption keys from user passwords with 100,000 iterations
- **Secure Random Salt** – Uses `os.urandom()` for cryptographic randomness
- **Chunk-Based Processing** – Efficiently handles large payloads by processing in manageable chunks
- **Interactive Web Interface** – Clean, modern Streamlit UI for easy operation

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.8+ | Core language |
| Streamlit | Web application framework |
| PyCryptodome | AES encryption & PBKDF2 |
| Pillow (PIL) | Image processing |
| NumPy | Efficient pixel manipulation |

## 📦 Installation

```bash
# Clone or navigate to the project directory
cd steganography_project

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

```bash
# Launch the web application
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Hiding Data
1. Go to the **🔒 Hide Data** tab
2. Upload a cover image (PNG, BMP, or TIFF)
3. Choose to hide a text message or a file
4. Enter an encryption password
5. Click **Embed Data** and download the stego image

### Extracting Data
1. Go to the **🔓 Extract Data** tab
2. Upload the stego image
3. Enter the same password used during hiding
4. Click **Extract Data** to recover the hidden content

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Streamlit Web Interface        │
│         (app.py - User Interface)        │
├─────────────────┬───────────────────────┤
│  Steganography  │   Cryptography        │
│  Engine         │   Module              │
│  (stego_engine) │   (crypto_module)     │
│                 │                       │
│  • LSB Embed    │   • AES-128-CBC       │
│  • LSB Extract  │   • PBKDF2 Key Gen    │
│  • Capacity     │   • SHA-256 Hash      │
│    Analysis     │   • Salt Generation   │
├─────────────────┴───────────────────────┤
│           Utilities (utils.py)          │
│  • Bit/Byte Conversion                 │
│  • Validation & Format Checking        │
│  • Capacity Calculations               │
└─────────────────────────────────────────┘
```

## 🔒 Security Details

- **Encryption**: AES-128 in CBC mode with PKCS7 padding
- **Key Derivation**: PBKDF2 with HMAC-SHA256, 100,000 iterations
- **Integrity**: SHA-256 hash embedded with ciphertext
- **Randomness**: `os.urandom()` for salt and IV generation
- **Supported Formats**: PNG, BMP, TIFF (lossless only – JPEG compression destroys hidden data)

## ⚠️ Important Notes

- **Only use lossless image formats** (PNG, BMP, TIFF). Lossy formats like JPEG will destroy the hidden data.
- **Remember your password** – there is no way to recover data without it.
- The stego image will always be saved as **PNG** to preserve data integrity.
- Larger images can hold more hidden data. Check the capacity indicator before embedding.

## ✅ Project Milestones Completed

- Requirement analysis and system architecture design completed.
- LSB based image steganography implemented for embedding data.
- AES based password encryption added for securing hidden information.
- SHA-256 hashing implemented for tamper detection and integrity verification.
- Web interface developed using Python and Streamlit.
- Embedding and extraction modules implemented and tested.
- Chunk-based processing implemented to support large files.
- User interface optimized for improved usability.
- Blockchain concept integrated for additional validation as suggested by the mentor.
- Animation added to demonstrate the steganography process visually.
- Final testing, debugging and performance optimization completed.

## 📄 License

This project is for educational and authorized security testing purposes only.
