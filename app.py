import streamlit as st
import fitz  # PyMuPDF
import os

# MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="PDF Header/Footer Manager",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "processed_file" not in st.session_state:
    st.session_state.processed_file = None


# Theme toggle function
def theme_toggle():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


# Theme-aware CSS styling
def get_css(theme):
    if theme == "dark":
        return """
            <style>
                /* Full-page gradient background */
                body, .stApp {
                    background: linear-gradient(135deg, #2B0059, #6A1B9A) !important;
                    background-attachment: fixed !important;
                    min-height: 100vh !important;
                    color: white !important;
                }
                /* Checkbox and Radio Button Labels */
                .stCheckbox label p,
                .stRadio label p {
                    color: white !important;
                    font-weight: 500 !important;
                }
                /* Button styling */
                .stButton>button {
                    background: #6A1B9A !important;
                    color: white !important;
                    border: 2px solid #9C27B0 !important;
                    border-radius: 10px !important;
                    padding: 14px 28px !important;
                    font-size: 16px !important;
                    font-weight: 600 !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
                }
                /* Button hover effect */
                .stButton>button:hover {
                    background: #9C27B0 !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2) !important;
                }
                /* File uploader styling */
                .stFileUploader>div>div>input[type="file"] {
                    color: white !important;
                }
                /* Form container styling */
                .stForm {
                    background: rgba(255, 255, 255, 0.05) !important;
                    border: 1px solid #4A148C !important;
                    border-radius: 15px !important;
                    padding: 25px !important;
                }
                /* Title styling */
                h1 {
                    color: white !important;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
                }
                /* Main content container */
                [data-testid="stVerticalBlock"] {
                    background: rgba(0, 0, 0, 0.3) !important;
                    border-radius: 20px !important;
                    padding: 30px !important;
                }
            </style>
        """
    else:
        return """
            <style>
                /* Light theme background */
                body, .stApp {
                    background: linear-gradient(135deg, #F3E5F5, #E8EAF6) !important;
                    background-attachment: fixed !important;
                    min-height: 100vh !important;
                    color: #333 !important;
                }
                /* Checkbox and Radio Button Labels */
                .stCheckbox label p,
                .stRadio label p {
                    color: #333 !important;
                    font-weight: 500 !important;
                }
                /* Button styling */
                .stButton>button {
                    background: #6A1B9A !important;
                    color: white !important;
                    border: 2px solid #9C27B0 !important;
                    border-radius: 10px !important;
                    padding: 14px 28px !important;
                    font-size: 16px !important;
                    font-weight: 600 !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
                }
                /* Button hover effect */
                .stButton>button:hover {
                    background: #9C27B0 !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2) !important;
                }
                /* Form container styling */
                .stForm {
                    background: rgba(255, 255, 255, 0.8) !important;
                    border: 1px solid #E0E0E0 !important;
                    border-radius: 15px !important;
                    padding: 25px !important;
                }
                /* Title styling */
                h1 {
                    color: #6A1B9A !important;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
                }
                /* Main content container */
                [data-testid="stVerticalBlock"] {
                    background: rgba(255, 255, 255, 0.9) !important;
                    border-radius: 20px !important;
                    padding: 30px !important;
                }
            </style>
        """


# Apply CSS and create toggle
st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)
with st.sidebar:
    st.button(
        "🌙" if st.session_state.theme == "dark" else "☀️",
        on_click=theme_toggle,
        key="theme_toggle"
    )

st.title("PDF Header/Footer Manager")

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)


def remove_headers_footers(input_path, remove_header=False, remove_footer=False):
    """Remove headers/footers while maintaining original dimensions"""
    doc = fitz.open(input_path)
    margin_percent = 15  # Adjust based on your document's header/footer size

    for page in doc:
        # Get original page dimensions
        media_rect = page.mediabox
        page_width = media_rect.width
        page_height = media_rect.height

        # Erase header
        if remove_header:
            header_height = page_height * margin_percent / 100
            page.draw_rect(
                fitz.Rect(0, 0, page_width, header_height),
                color=(1, 1, 1),  # White color
                fill=(1, 1, 1),  # Opaque fill
                overlay=True  # Cover existing content
            )

        # Erase footer
        if remove_footer:
            footer_height = page_height * margin_percent / 100
            page.draw_rect(
                fitz.Rect(0, page_height - footer_height, page_width, page_height),
                color=(1, 1, 1),
                fill=(1, 1, 1),
                overlay=True
            )

        # Clean page contents to optimize
        page.clean_contents()

    # Save with original dimensions and optimize
    output_path = os.path.join(TEMP_DIR, f"processed_{os.path.basename(input_path)}")
    doc.save(output_path,
             garbage=3,  # Aggressive cleanup
             deflate=True,  # Compress output
             clean=True)  # Remove unused resources
    return output_path


def add_headers_footers(input_path, header_path, footer_path):
    doc = fitz.open(input_path)

    if header_path:
        header_pix = fitz.Pixmap(header_path)
    if footer_path:
        footer_pix = fitz.Pixmap(footer_path)

    for page in doc:
        # Use original page dimensions
        media_rect = page.mediabox
        page_width = media_rect.width
        page_height = media_rect.height

        if header_path:
            scale = page_width / header_pix.width
            header_rect = fitz.Rect(0, 0, page_width, header_pix.height * scale)
            page.insert_image(header_rect, pixmap=header_pix, overlay=True)

        if footer_path:
            scale = page_width / footer_pix.width
            footer_rect = fitz.Rect(0, page_height - footer_pix.height * scale,
                                    page_width, page_height)
            page.insert_image(footer_rect, pixmap=footer_pix, overlay=True)

    output_path = os.path.join(TEMP_DIR, f"final_{os.path.basename(input_path)}")
    doc.save(output_path,
             garbage=3,
             deflate=True,
             clean=True)
    return output_path


# Main app
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

with st.form("combined_processing"):
    st.header("Processing Options")
    remove_header = st.checkbox("Remove Header")
    remove_footer = st.checkbox("Remove Footer")

    st.header("Add New Headers/Footers")
    header_file = st.file_uploader("Header Image", type=["png", "jpg", "jpeg"])
    footer_file = st.file_uploader("Footer Image", type=["png", "jpg", "jpeg"])

    process_clicked = st.form_submit_button("Process PDF")

if process_clicked and uploaded_file:
    # Save original file
    input_path = os.path.join(TEMP_DIR, uploaded_file.name)
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    current_path = input_path

    # Process removal if needed
    if remove_header or remove_footer:
        current_path = remove_headers_footers(
            current_path,
            remove_header=remove_header,
            remove_footer=remove_footer
        )

    # Process addition if images provided
    if header_file or footer_file:
        # Save header/footer images
        header_path = None
        footer_path = None

        if header_file:
            header_ext = header_file.name.split(".")[-1]
            header_path = os.path.join(TEMP_DIR, f"header.{header_ext}")
            with open(header_path, "wb") as f:
                f.write(header_file.getbuffer())

        if footer_file:
            footer_ext = footer_file.name.split(".")[-1]
            footer_path = os.path.join(TEMP_DIR, f"footer.{footer_ext}")
            with open(footer_path, "wb") as f:
                f.write(footer_file.getbuffer())

        current_path = add_headers_footers(current_path, header_path, footer_path)

        # Cleanup temporary images
        if header_path and os.path.exists(header_path):
            os.remove(header_path)
        if footer_path and os.path.exists(footer_path):
            os.remove(footer_path)

    # Save final processed file to session state
    st.session_state.processed_file = current_path

    # Cleanup original file
    os.remove(input_path)

# Download button
if st.session_state.processed_file:
    with open(st.session_state.processed_file, "rb") as f:
        st.download_button(
            "Download Processed PDF",
            f,
            file_name=f"processed_{os.path.basename(uploaded_file.name)}" if uploaded_file else "processed.pdf",
            key="download_processed"
        )
