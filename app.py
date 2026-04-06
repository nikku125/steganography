"""
Steganography Tool – Secure Web-Based Data Hiding & Extraction System
Main Streamlit application providing the interactive web interface.
"""

import streamlit as st
from PIL import Image
import io
import os
import sys
import time

# Add project directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stego_engine import embed_data, extract_data, get_image_info
from crypto_module import encrypt, decrypt, compute_sha256
from blockchain_module import ledger
from utils import (
    validate_image_format, validate_file_size,
    calculate_capacity, format_file_size
)

# ─────────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StegoCrypt – Steganography Tool",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# Custom CSS – Dark Cyber Theme
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Root Variables ── */
    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a1f35;
        --bg-card-hover: #1f2847;
        --accent-cyan: #06d6a0;
        --accent-blue: #118ab2;
        --accent-purple: #7b2ff7;
        --accent-pink: #ff006e;
        --text-primary: #e8eaf6;
        --text-secondary: #9ca3af;
        --border-color: #2a3050;
        --glow-cyan: 0 0 20px rgba(6, 214, 160, 0.3);
        --glow-purple: 0 0 20px rgba(123, 47, 247, 0.3);
    }

    /* ── Global Styles ── */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0d1320 50%, #111827 100%) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Header ── */
    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        margin-bottom: 1rem;
    }
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #06d6a0, #118ab2, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .main-header .subtitle {
        color: var(--text-secondary);
        font-size: 1.05rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }

    /* ── Cards ── */
    .cyber-card {
        background: linear-gradient(145deg, rgba(26, 31, 53, 0.9), rgba(17, 24, 39, 0.95));
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .cyber-card:hover {
        border-color: var(--accent-cyan);
        box-shadow: var(--glow-cyan);
    }
    .cyber-card h3 {
        color: var(--accent-cyan);
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.15rem;
    }

    /* ── Status badges ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-success {
        background: rgba(6, 214, 160, 0.15);
        color: #06d6a0;
        border: 1px solid rgba(6, 214, 160, 0.3);
    }
    .badge-danger {
        background: rgba(255, 0, 110, 0.15);
        color: #ff006e;
        border: 1px solid rgba(255, 0, 110, 0.3);
    }
    .badge-info {
        background: rgba(17, 138, 178, 0.15);
        color: #118ab2;
        border: 1px solid rgba(17, 138, 178, 0.3);
    }

    /* ── Capacity Bar ── */
    .capacity-bar-container {
        background: rgba(42, 48, 80, 0.5);
        border-radius: 10px;
        padding: 3px;
        margin: 8px 0;
    }
    .capacity-bar {
        height: 8px;
        border-radius: 8px;
        transition: width 0.5s ease;
    }

    /* ── Metric Box ── */
    .metric-box {
        background: linear-gradient(145deg, rgba(26, 31, 53, 0.7), rgba(17, 24, 39, 0.8));
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-box .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--accent-cyan);
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-box .label {
        color: var(--text-secondary);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    /* ── Sidebar Styling ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1320 0%, #111827 100%) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* ── Info Panel in Sidebar ── */
    .sidebar-info {
        background: linear-gradient(145deg, rgba(26, 31, 53, 0.6), rgba(17, 24, 39, 0.7));
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .sidebar-info h4 {
        color: var(--accent-cyan);
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .sidebar-info p, .sidebar-info li {
        color: var(--text-secondary);
        font-size: 0.82rem;
        line-height: 1.6;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(26, 31, 53, 0.6) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(6, 214, 160, 0.15), rgba(17, 138, 178, 0.15)) !important;
        border-color: var(--accent-cyan) !important;
        color: var(--accent-cyan) !important;
        box-shadow: var(--glow-cyan) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #06d6a0, #118ab2) !important;
        color: #0a0e17 !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 25px rgba(6, 214, 160, 0.4) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #7b2ff7, #118ab2) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        box-shadow: var(--glow-purple) !important;
        transform: translateY(-1px) !important;
    }

    /* ── File uploader ── */
    .stFileUploader > div {
        border: 2px dashed var(--border-color) !important;
        border-radius: 12px !important;
        background: rgba(26, 31, 53, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stFileUploader > div:hover {
        border-color: var(--accent-cyan) !important;
        background: rgba(6, 214, 160, 0.05) !important;
    }

    /* ── Text inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(26, 31, 53, 0.6) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 10px rgba(6, 214, 160, 0.2) !important;
    }

    /* ── Radio buttons ── */
    .stRadio > div {
        gap: 0.5rem;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(26, 31, 53, 0.4) !important;
        border-radius: 10px !important;
        border: 1px solid var(--border-color) !important;
    }

    /* ── Footer ── */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: var(--text-secondary);
        font-size: 0.8rem;
        border-top: 1px solid var(--border-color);
        margin-top: 2rem;
    }

    /* ── Hide default streamlit elements ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-blue);
    }

    /* ── Scanning Animation ── */
    .scan-container {
        position: relative;
        display: inline-block;
        overflow: hidden;
        border-radius: 8px;
        border: 2px solid var(--accent-cyan);
        box-shadow: 0 0 15px rgba(6, 214, 160, 0.3);
    }
    .scan-container img {
        display: block;
        width: 100%;
        height: auto;
    }
    .scan-line {
        position: absolute;
        top: -5%;
        left: 0;
        width: 100%;
        height: 5px;
        background: rgba(6, 214, 160, 0.8);
        box-shadow: 0 0 15px 5px rgba(6, 214, 160, 0.5);
        animation: scan 2s linear infinite;
    }
    @keyframes scan {
        0% { top: -5%; }
        50% { top: 105%; }
        100% { top: -5%; }
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🔐</div>
        <h2 style="background: linear-gradient(135deg, #06d6a0, #118ab2);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-weight: 700; font-size: 1.5rem; margin: 0;">
            StegoCrypt
        </h2>
        <p style="color: #9ca3af; font-size: 0.8rem; margin-top: 4px;">v1.0 • Secure Steganography</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="sidebar-info">
        <h4>🛡️ Security Stack</h4>
        <p>
            • <strong>AES-128-CBC</strong> encryption<br>
            • <strong>PBKDF2</strong> key derivation (100K iter.)<br>
            • <strong>SHA-256</strong> integrity hashing<br>
            • <strong>LSB</strong> steganography<br>
            • Secure random salt & IV
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-info">
        <h4>📁 Supported Formats</h4>
        <p>
            • PNG (recommended)<br>
            • BMP (uncompressed)<br>
            • TIFF (lossless)
        </p>
        <p style="color: #ff006e; font-size: 0.78rem; margin-top: 6px;">
            ⚠️ JPEG is NOT supported – lossy compression destroys hidden data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-info">
        <h4>📖 How It Works</h4>
        <p>
            1. Your data is encrypted with AES-128<br>
            2. A SHA-256 hash is computed for integrity<br>
            3. Encrypted data + hash is embedded in image pixel LSBs<br>
            4. The modified image looks identical to the original
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer">
        Built with 🐍 Python & Streamlit<br>
        For educational & authorized use only
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Main Header
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔐 StegoCrypt</h1>
    <p class="subtitle">Secure Data Hiding & Extraction using LSB Steganography + AES-128 Encryption</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Main Tabs
# ─────────────────────────────────────────────────────────────
tab_hide, tab_extract, tab_ledger = st.tabs(["🔒  Hide Data", "🔓  Extract Data", "⛓️ Blockchain Ledger"])


# =============================================================
# TAB 1 – HIDE DATA
# =============================================================
with tab_hide:
    st.markdown("""
    <div class="cyber-card">
        <h3>📥 Embed Secret Data into an Image</h3>
        <p style="color: #9ca3af; font-size: 0.9rem;">
            Upload a cover image, provide your secret data and a strong password.
            The tool will encrypt your data and invisibly embed it within the image pixels.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_upload, col_settings = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown("#### 🖼️ Cover Image")
        cover_file = st.file_uploader(
            "Upload a cover image (PNG, BMP, TIFF)",
            type=["png", "bmp", "tiff", "tif"],
            key="cover_upload",
            help="This image will carry the hidden data. Larger images can hold more data."
        )

        if cover_file:
            cover_image = Image.open(cover_file)
            img_info = get_image_info(cover_image)

            # Display image
            st.image(cover_image, caption="Cover Image Preview", use_container_width=True)

            # Image info metrics
            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{img_info['width']}×{img_info['height']}</div>
                    <div class="label">Dimensions</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{img_info['total_pixels']:,}</div>
                    <div class="label">Total Pixels</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{format_file_size(img_info['capacity_bytes'])}</div>
                    <div class="label">Max Capacity</div>
                </div>
                """, unsafe_allow_html=True)

    with col_settings:
        st.markdown("#### 🔑 Secret Data & Password")

        data_type = st.radio(
            "What do you want to hide?",
            ["📝 Text Message", "📄 File"],
            horizontal=True,
            key="hide_data_type"
        )

        secret_data = None
        original_filename = None

        if data_type == "📝 Text Message":
            secret_text = st.text_area(
                "Enter your secret message",
                height=150,
                placeholder="Type your secret message here...",
                key="secret_text"
            )
            if secret_text:
                secret_data = secret_text.encode('utf-8')
        else:
            secret_file = st.file_uploader(
                "Upload a secret file to hide",
                type=None,
                key="secret_file_upload",
                help="Any file type is supported. The file will be encrypted and hidden."
            )
            if secret_file:
                secret_data = secret_file.read()
                original_filename = secret_file.name

        st.markdown("")  # Spacing
        password = st.text_input(
            "🔐 Encryption Password",
            type="password",
            placeholder="Enter a strong password",
            key="hide_password",
            help="This password will encrypt your data. You'll need it to extract later."
        )

        confirm_password = st.text_input(
            "🔐 Confirm Password",
            type="password",
            placeholder="Re-enter your password",
            key="hide_confirm_password"
        )

        # Show data size info
        if secret_data and cover_file:
            cap = img_info['capacity_bytes']
            data_size = len(secret_data)
            # Account for encryption overhead (salt + IV + hash + padding)
            estimated_encrypted_size = data_size + 16 + 16 + 64 + 16  # rough estimate
            usage_pct = min(100, (estimated_encrypted_size / cap) * 100) if cap > 0 else 100

            color = "#06d6a0" if usage_pct < 70 else ("#ffd166" if usage_pct < 90 else "#ff006e")

            st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; color: #9ca3af; font-size: 0.82rem;">
                    <span>Data: {format_file_size(data_size)}</span>
                    <span>Capacity: {format_file_size(cap)}</span>
                </div>
                <div class="capacity-bar-container">
                    <div class="capacity-bar" style="width: {usage_pct:.1f}%; background: linear-gradient(90deg, {color}, {color}88);"></div>
                </div>
                <div style="text-align: center; color: {color}; font-size: 0.8rem; font-family: 'JetBrains Mono';">
                    {usage_pct:.1f}% capacity used (estimated)
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Embed Button ──
    st.markdown("")
    embed_col1, embed_col2, embed_col3 = st.columns([1, 2, 1])
    with embed_col2:
        embed_clicked = st.button(
            "🔒  Embed Data into Image",
            use_container_width=True,
            key="embed_btn"
        )

    if embed_clicked:
        # Validation
        if not cover_file:
            st.error("⚠️ Please upload a cover image.")
        elif not secret_data:
            st.error("⚠️ Please provide secret data (text or file).")
        elif not password:
            st.error("⚠️ Please enter an encryption password.")
        elif password != confirm_password:
            st.error("⚠️ Passwords do not match!")
        elif len(password) < 4:
            st.error("⚠️ Password must be at least 4 characters.")
        else:
            with st.spinner("🔄 Encrypting and embedding data..."):
                try:
                    # Visual Animation of Steganography Process
                    import base64
                    import time
                    
                    img_buffer_anim = io.BytesIO()
                    cover_image.save(img_buffer_anim, format='PNG')
                    img_b64 = base64.b64encode(img_buffer_anim.getvalue()).decode()
                    
                    animation_html = f"""
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <h4 style="color: #06d6a0; font-family: 'JetBrains Mono', monospace; margin-bottom: 1rem;">
                            <span class="status-badge badge-success">⚙️ Injecting Data into Pixel LSBs...</span>
                        </h4>
                        <div class="scan-container" style="max-width: 500px; margin: 0 auto;">
                            <img src="data:image/png;base64,{img_b64}" />
                            <div class="scan-line"></div>
                        </div>
                    </div>
                    """
                    scan_placeholder = st.empty()
                    scan_placeholder.markdown(animation_html, unsafe_allow_html=True)
                    
                    # Simulate processing time for animation
                    time.sleep(2.5)

                    # Step 1: Prepare payload
                    # If it's a file, prepend filename for later extraction
                    if original_filename:
                        filename_bytes = original_filename.encode('utf-8')
                        # Format: [filename_len (2 bytes)] [filename] [file_data]
                        payload_raw = (
                            len(filename_bytes).to_bytes(2, 'big') +
                            filename_bytes +
                            secret_data
                        )
                        is_file = True
                    else:
                        # Text message: prefix with 0x00 0x00 to indicate text
                        payload_raw = b'\x00\x00' + secret_data
                        is_file = False

                    # Step 2: Encrypt
                    encrypted_payload = encrypt(payload_raw, password)

                    # Step 3: Embed
                    stego_image = embed_data(cover_image, encrypted_payload)

                    # Step 4: Convert to bytes for download
                    img_buffer = io.BytesIO()
                    stego_image.save(img_buffer, format='PNG')
                    img_bytes = img_buffer.getvalue()

                    # Step 5: Record in Blockchain
                    tx_hash = compute_sha256(img_bytes)
                    block_data = {
                        "action": "embed",
                        "transaction_hash": tx_hash,
                        "payload_size": len(encrypted_payload),
                        "timestamp": time.time()
                    }
                    ledger.add_block(block_data)

                    # Clear animation
                    scan_placeholder.empty()

                    # Success!
                    st.markdown("""
                    <div class="cyber-card" style="border-color: #06d6a0; box-shadow: 0 0 20px rgba(6, 214, 160, 0.2);">
                        <h3 style="color: #06d6a0;">✅ Data Successfully Embedded!</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    # Show comparison
                    comp1, comp2 = st.columns(2)
                    with comp1:
                        st.markdown("**Original Image**")
                        st.image(cover_image, use_container_width=True)
                    with comp2:
                        st.markdown("**Stego Image (with hidden data)**")
                        st.image(stego_image, use_container_width=True)

                    # Stats
                    original_hash = compute_sha256(secret_data)
                    s1, s2, s3 = st.columns(3)
                    with s1:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="value">{format_file_size(len(encrypted_payload))}</div>
                            <div class="label">Encrypted Size</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with s2:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="value">{format_file_size(len(img_bytes))}</div>
                            <div class="label">Stego Image Size</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with s3:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="value" style="font-size: 0.7rem;">{original_hash[:16]}...</div>
                            <div class="label">SHA-256 Hash</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Download button
                    st.markdown("")
                    dl1, dl2, dl3 = st.columns([1, 2, 1])
                    with dl2:
                        # Use original filename with _stego suffix
                        original_name = os.path.splitext(cover_file.name)[0]
                        download_filename = f"{original_name}_stego.png"
                        st.download_button(
                            label="⬇️  Download Stego Image (.png)",
                            data=img_bytes,
                            file_name=download_filename,
                            mime="application/octet-stream",
                            use_container_width=True,
                            key="download_stego"
                        )

                except ValueError as e:
                    st.error(f"❌ Embedding failed: {str(e)}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")


# =============================================================
# TAB 2 – EXTRACT DATA
# =============================================================
with tab_extract:
    st.markdown("""
    <div class="cyber-card">
        <h3>📤 Extract Hidden Data from an Image</h3>
        <p style="color: #9ca3af; font-size: 0.9rem;">
            Upload a stego image created by this tool and enter the correct password
            to decrypt and retrieve the hidden data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    ext_col1, ext_col2 = st.columns([1, 1], gap="large")

    with ext_col1:
        st.markdown("#### 🖼️ Stego Image")
        stego_file = st.file_uploader(
            "Upload the stego image containing hidden data",
            type=["png", "bmp", "tiff", "tif"],
            key="stego_upload",
            help="Upload the image that was created by this tool with hidden data."
        )

        if stego_file:
            stego_bytes_cache = stego_file.getvalue()
            stego_image = Image.open(io.BytesIO(stego_bytes_cache))
            st.image(stego_image, caption="Stego Image Preview", use_container_width=True)

            s_info = get_image_info(stego_image)
            em1, em2 = st.columns(2)
            with em1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{s_info['width']}×{s_info['height']}</div>
                    <div class="label">Dimensions</div>
                </div>
                """, unsafe_allow_html=True)
            with em2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="value">{s_info['total_pixels']:,}</div>
                    <div class="label">Total Pixels</div>
                </div>
                """, unsafe_allow_html=True)

    with ext_col2:
        st.markdown("#### 🔑 Decryption Password")
        extract_password = st.text_input(
            "🔐 Enter the password used during embedding",
            type="password",
            placeholder="Enter your password",
            key="extract_password",
            help="You must use the exact same password that was used to hide the data."
        )

        st.markdown("")
        extract_clicked = st.button(
            "🔓  Extract Hidden Data",
            use_container_width=True,
            key="extract_btn"
        )

    if extract_clicked:
        if not stego_file:
            st.error("⚠️ Please upload a stego image.")
        elif not extract_password:
            st.error("⚠️ Please enter the decryption password.")
        else:
            with st.spinner("🔄 Extracting and decrypting hidden data..."):
                try:
                    # Visual Animation of Steganography Extraction Process
                    import base64
                    import time
                    
                    img_buffer_anim = io.BytesIO()
                    stego_image.save(img_buffer_anim, format='PNG')
                    img_b64 = base64.b64encode(img_buffer_anim.getvalue()).decode()
                    
                    animation_html = f"""
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <h4 style="color: #118ab2; font-family: 'JetBrains Mono', monospace; margin-bottom: 1rem;">
                            <span class="status-badge badge-info">🔍 Scanning Pixels for Hidden Data...</span>
                        </h4>
                        <div class="scan-container" style="max-width: 500px; margin: 0 auto; border-color: #118ab2; box-shadow: 0 0 15px rgba(17, 138, 178, 0.3);">
                            <img src="data:image/png;base64,{img_b64}" />
                            <div class="scan-line" style="background: rgba(17, 138, 178, 0.8); box-shadow: 0 0 15px 5px rgba(17, 138, 178, 0.5);"></div>
                        </div>
                    </div>
                    """
                    scan_placeholder = st.empty()
                    scan_placeholder.markdown(animation_html, unsafe_allow_html=True)
                    
                    # Simulate processing time for animation
                    time.sleep(2.5)

                    # Step 1: Verify stego image in Blockchain
                    tx_hash = compute_sha256(stego_bytes_cache)
                    is_verified_in_blockchain = ledger.verify_transaction(tx_hash)

                    # Step 2: Extract encrypted payload
                    encrypted_payload = extract_data(stego_image)

                    # Step 3: Decrypt
                    decrypted_data, integrity_valid = decrypt(
                        encrypted_payload, extract_password
                    )

                    # Step 4: Parse payload type
                    filename_len = int.from_bytes(decrypted_data[:2], 'big')

                    if filename_len == 0:
                        # It's a text message
                        extracted_text = decrypted_data[2:].decode('utf-8')
                        is_file_extract = False
                    else:
                        # It's a file
                        filename = decrypted_data[2:2 + filename_len].decode('utf-8')
                        file_data = decrypted_data[2 + filename_len:]
                        is_file_extract = True

                    # Clear animation
                    scan_placeholder.empty()

                    # Integrity status
                    if integrity_valid:
                        bc_badge = ""
                        if is_verified_in_blockchain:
                            bc_badge = '<span class="status-badge badge-success" style="margin-top: 10px;">⛓️ Blockchain Verified</span>'
                        else:
                            bc_badge = '<span class="status-badge badge-danger" style="margin-top: 10px;">⛓️ Not in Blockchain</span>'

                        st.markdown(f"""
                        <div class="cyber-card" style="border-color: #06d6a0; box-shadow: 0 0 20px rgba(6, 214, 160, 0.2);">
                            <h3 style="color: #06d6a0;">✅ Data Successfully Extracted!</h3>
                            <span class="status-badge badge-success">🛡️ SHA-256 Integrity Verified</span>
                            {bc_badge}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="cyber-card" style="border-color: #ffd166; box-shadow: 0 0 20px rgba(255, 209, 102, 0.2);">
                            <h3 style="color: #ffd166;">⚠️ Data Extracted – Integrity Warning</h3>
                            <span class="status-badge badge-danger">⚠️ SHA-256 Hash Mismatch – Data may be tampered</span>
                        </div>
                        """, unsafe_allow_html=True)

                    if is_file_extract:
                        # Show file info and download
                        st.markdown(f"""
                        <div class="cyber-card">
                            <h3>📄 Extracted File</h3>
                            <p style="color: #e8eaf6;">
                                <strong>Filename:</strong> {filename}<br>
                                <strong>Size:</strong> {format_file_size(len(file_data))}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                        dl1, dl2, dl3 = st.columns([1, 2, 1])
                        with dl2:
                            st.download_button(
                                label=f"⬇️  Download {filename}",
                                data=file_data,
                                file_name=filename,
                                use_container_width=True,
                                key="download_extracted_file"
                            )
                    else:
                        # Show text message
                        st.markdown(f"""
                        <div class="cyber-card">
                            <h3>📝 Extracted Message</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.text_area(
                            "Hidden Message",
                            value=extracted_text,
                            height=200,
                            key="extracted_message_display",
                            disabled=True
                        )

                    # Show hash info
                    if is_file_extract:
                        data_hash = compute_sha256(file_data)
                        data_size = len(file_data)
                    else:
                        data_hash = compute_sha256(extracted_text.encode('utf-8'))
                        data_size = len(extracted_text.encode('utf-8'))

                    h1, h2 = st.columns(2)
                    with h1:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="value">{format_file_size(data_size)}</div>
                            <div class="label">Extracted Data Size</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with h2:
                        st.markdown(f"""
                        <div class="metric-box">
                            <div class="value" style="font-size: 0.7rem;">{data_hash[:24]}...</div>
                            <div class="label">Data Hash (SHA-256)</div>
                        </div>
                        """, unsafe_allow_html=True)

                except ValueError as e:
                    st.error(f"❌ Extraction failed: {str(e)}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")


# =============================================================
# TAB 3 – BLOCKCHAIN LEDGER
# =============================================================
with tab_ledger:
    st.markdown("""
    <div class="cyber-card">
        <h3>⛓️ Blockchain Ledger</h3>
        <p style="color: #9ca3af; font-size: 0.9rem;">
            This simulated blockchain records all embedding operations to provide an immutable log 
            for verifying the integrity and origin of stego images.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown("#### Immutable Transaction Chain")
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            ledger.load_ledger()
            
    # Check chain validity
    chain_valid = ledger.is_chain_valid()
    if chain_valid:
        st.markdown("""
        <div style="background: rgba(6, 214, 160, 0.15); border: 1px solid #06d6a0; padding: 10px; border-radius: 8px; margin-bottom: 20px; color: #06d6a0; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;">✅</span> <strong>Blockchain Integrity Status: VALID</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(255, 0, 110, 0.15); border: 1px solid #ff006e; padding: 10px; border-radius: 8px; margin-bottom: 20px; color: #ff006e; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 1.2rem;">⚠️</span> <strong>Blockchain Integrity Status: CORRUPTED</strong>
        </div>
        """, unsafe_allow_html=True)
        
    chain_data = ledger.get_chain()
    
    if len(chain_data) == 0:
        st.info("No blocks found in the ledger.")
    else:
        for i, block in enumerate(reversed(chain_data)):
            # Expand the first few blocks by default
            is_expanded = (i < 3)
            with st.expander(f"📦 Block #{block['index']} - {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block['timestamp']))}", expanded=is_expanded):
                if block['index'] == 0:
                    st.markdown("**Genesis Block**")
                else:
                    st.markdown(f"**Action:** `{block['data'].get('action', 'Unknown')}`")
                    st.markdown(f"**Tx Hash:** `{block['data'].get('transaction_hash', 'N/A')}`")
                    st.markdown(f"**Payload Size:** `{block['data'].get('payload_size', 0)} bytes`")
                
                st.markdown("---")
                st.code(f"Block Hash: {block['hash']}\\nPrev Hash:  {block['previous_hash']}", language="text")

# ─────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <p>🔐 <strong>StegoCrypt</strong> – Secure Web-Based Data Hiding & Extraction System</p>
    <p>Built with Python • Streamlit • AES-128 • LSB Steganography • SHA-256</p>
</div>
""", unsafe_allow_html=True)
