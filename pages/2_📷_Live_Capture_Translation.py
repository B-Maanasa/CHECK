import cv2
import easyocr
import numpy as np
import streamlit as st
from textblob import TextBlob
from googletrans import Translator, LANGUAGES

# Initialize EasyOCR reader and Google Translator
reader = easyocr.Reader(['en'])  # Set the languages for OCR
translator = Translator()

def translate_text(text, target_lang):
    translation = translator.translate(text, dest=target_lang)
    return translation.text

def capture_and_process(target_lang='en', camera_on=True):
    st.title("Live OCR Translation")

    cap = cv2.VideoCapture(0) if camera_on else None

    while True:
        if cap is not None:
            ret, frame = cap.read()  # Capture frame from the camera
            if not ret:
                break
        
            # Use EasyOCR to extract text from the frame
            result = reader.readtext(frame)
            
            # Process the detected text
            processed_frame = frame.copy()  # Initialize processed frame

            for detection in result:
                text = detection[1]
                bbox = detection[0]  # Bounding box of the detected text
                
                try:
                    # Detect the language of the extracted text using TextBlob
                    detected_lang = TextBlob(text).detect_language()
                except:
                    detected_lang = 'en'  # Default to 'en' if language detection fails
                
                # Translate the text to the target language if it's different from the source language
                if detected_lang != target_lang:
                    translated_text = translate_text(text, target_lang)
                else:
                    translated_text = text
                
                # Display the translated text on the input image
                text_position = (int(bbox[0][0]), int(bbox[0][1]))  # Position of the detected text
                cv2.putText(
                    processed_frame,
                    translated_text,
                    text_position,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),  # White color
                    2
                )

            # Display the processed frame using Streamlit
            st.image(processed_frame, channels="BGR")

        # Check for key press (press 'q' to quit)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    if cap is not None:
        cap.release()

def start_translation(target_lang='en'):
    st.title("Camera Control")
    camera_on = st.button("Camera On")
    camera_off = st.button("Camera Off")
    
    if camera_off:
        capture_and_process(target_lang, camera_on=False)
    elif camera_on:
        capture_and_process(target_lang)

if __name__ == "__main__":
    # Get the supported languages for translation
    supported_languages = list(LANGUAGES.values())
    
    # Create a Streamlit dropdown to select the target language
    selected_language = st.selectbox("Select Target Language", supported_languages, index=0)
    
    # Start the translation process
    start_translation(selected_language)
