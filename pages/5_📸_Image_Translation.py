import streamlit as st
import easyocr
import numpy as np
from PIL import Image
import io
from googletrans import Translator

# Initialize EasyOCR reader for English language
reader = easyocr.Reader(['en'])
translator = Translator()

# Function to perform OCR on the uploaded image and translate text to the target language
def perform_ocr_on_image(image_bytes, target_lang):
    # Open image from bytes
    img = Image.open(io.BytesIO(image_bytes))

    # Convert image to numpy array
    img_np = np.array(img)

    # Perform OCR using EasyOCR
    result = reader.readtext(img_np)

    ocr_result = ""
    for detection in result:
        text = detection[1]

        # Translate text to the target language
        translation = translator.translate(text, dest=target_lang)
        translated_text = translation.text

        ocr_result += translated_text + "\n"

    return ocr_result

# Streamlit app main page
st.title("Image OCR Translation")

uploaded_image = st.file_uploader("Upload an image (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_image:
    supported_languages = ['en', 'fr', 'es', 'de']  # Example supported languages
    selected_ocr_language_image = st.selectbox("Select OCR Target Language", supported_languages)

    ocr_image_button = st.button("Perform OCR")

    if ocr_image_button:
        image_bytes = uploaded_image.read()
        ocr_result_image = perform_ocr_on_image(image_bytes, selected_ocr_language_image)

        st.header("OCR Result:")
        st.text_area("Translated Text", value=ocr_result_image, height=300)
