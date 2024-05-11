import cv2
import numpy as np
import streamlit as st
import threading
from typing import Union
import av
from streamlit_webrtc import VideoTransformerBase, webrtc_streamer, ClientSettings
import easyocr
from textblob import TextBlob
from googletrans import Translator, LANGUAGES

# Initialize EasyOCR reader and Google Translator
reader = easyocr.Reader(['en'])  # Set the languages for OCR
translator = Translator()

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def transform(self, frame):
        # Convert the frame to BGR format for EasyOCR
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Use EasyOCR to extract text from the frame
        result = self.reader.readtext(frame_bgr)

        # Process the detected text
        processed_frame = frame.copy()

        for detection in result:
            text = detection[1]
            bbox = detection[0]

            try:
                # Detect the language of the extracted text using TextBlob
                detected_lang = TextBlob(text).detect_language()
            except:
                detected_lang = 'en'  # Default to 'en' if language detection fails

            # Translate the text to the target language if it's different from the source language
            target_lang = st.session_state.target_lang
            if detected_lang != target_lang:
                translated_text = translate_text(text, target_lang)
            else:
                translated_text = text

            # Display the translated text on the processed frame
            text_position = (int(bbox[0][0]), int(bbox[0][1]))  # Position of the detected text
            cv2.putText(
                processed_frame,
                translated_text,
                text_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),  # Green color for translated text
                2
            )

        # Convert the processed frame back to RGB format
        processed_frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        return processed_frame_rgb

def translate_text(text, target_lang):
    translation = translator.translate(text, dest=target_lang)
    return translation.text

def main():
    st.title("Live OCR Translation with WebRTC")

    # Initialize WebRTC parameters
    rtc_configuration = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}

    media_stream_constraints = {
        "video": True,
        "audio": False,
    }

    # Start WebRTC streaming
    webrtc_ctx = webrtc_streamer(
        key="example",
        rtc_configuration=rtc_configuration,
        media_stream_constraints=media_stream_constraints,
        video_transformer_factory=VideoTransformer,
    )

    if webrtc_ctx is not None:
        if webrtc_ctx.state.playing:
            st.write("WebRTC connection established. Select target language and start the camera to perform live OCR translation.")

            # Create a dropdown to select the target language
            supported_languages = list(LANGUAGES.values())
            st.session_state.target_lang = st.selectbox("Select Target Language", supported_languages, index=13)

            # Display the processed frame with translated text
            if st.button("Take Snapshot"):
                with webrtc_ctx.video_transformer.frame_lock:
                    # Get the latest frame from the video transformer
                    snapshot_frame = webrtc_ctx.video_transformer.out_image

                    if snapshot_frame is not None:
                        # Perform OCR on the snapshot frame
                        snapshot_bgr = cv2.cvtColor(snapshot_frame, cv2.COLOR_RGB2BGR)
                        result = reader.readtext(snapshot_bgr)

                        # Process the detected text and translate
                        processed_snapshot = snapshot_frame.copy()

                        for detection in result:
                            text = detection[1]
                            bbox = detection[0]

                            try:
                                # Detect the language of the extracted text using TextBlob
                                detected_lang = TextBlob(text).detect_language()
                            except:
                                detected_lang = 'en'  # Default to 'en' if language detection fails

                            # Translate the text to the target language if it's different from the source language
                            if detected_lang != st.session_state.target_lang:
                                translated_text = translate_text(text, st.session_state.target_lang)
                            else:
                                translated_text = text

                            # Display the translated text on the snapshot
                            text_position = (int(bbox[0][0]), int(bbox[0][1]))  # Position of the detected text
                            cv2.putText(
                                processed_snapshot,
                                translated_text,
                                text_position,
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.8,
                                (0, 255, 0),  # Green color for translated text
                                2
                            )

                        # Display the processed snapshot with translated text
                        st.image(processed_snapshot, channels="RGB")
        else:
            st.warning("WebRTC connection is not established.")
    else:
        st.warning("Failed to initialize WebRTC stream. Please check your connection and try again.")

if __name__ == "__main__":
    main()
