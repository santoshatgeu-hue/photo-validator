import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json
import tempfile
import os

st.set_page_config(page_title="Passport Photo Validator", page_icon="🪪")
st.title("🪪 Passport Photo Validator & Uploader")

st.write("Upload a passport-size photo. The system checks if a full face is visible and automatically uploads it to Google Drive if acceptable.")

# --- Step 1: Student ID ---
student_id = st.text_input("Enter Student ID (required):")

# --- Step 2: Upload photo ---
uploaded_file = st.file_uploader("Upload Passport Photo", type=["jpg", "jpeg", "png"])

# --- Step 3: Access Drive credentials from Streamlit Secrets ---
if "google_service_key" not in st.secrets:
    st.error("Google Drive credentials not configured. Please add service account key to Streamlit Secrets.")
else:
    SERVICE_JSON = st.secrets["google_service_key"]
    DRIVE_FOLDER_ID = st.secrets["drive_folder_id"]

    def create_drive_instance():
        """Authenticate using the service account from Streamlit Secrets"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_json:
            json.dump(SERVICE_JSON, temp_json)
            temp_json.flush()
            gauth = GoogleAuth()
            gauth.LoadServiceConfigFile(temp_json.name)
            drive = GoogleDrive(gauth)
        return drive

    if uploaded_file is not None:
        if not student_id:
            st.warning("⚠️ Please enter your Student ID before uploading.")
        else:
            image = Image.open(uploaded_file).convert("RGB")
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

            for (x, y, w, h) in faces:
                cv2.rectangle(img_array, (x, y), (x + w, y + h), (0, 255, 0), 2)

            st.image(img_array, caption="Uploaded Image with Detection", use_column_width=True)

            # --- Step 4: Face validation ---
            if len(faces) == 1:
                (x, y, w, h) = faces[0]
                height, width = gray.shape
                face_area_ratio = (w * h) / (width * height)

                if 0.1 < face_area_ratio < 0.6:
                    st.success("✅ Acceptable: Full face is visible.")
                    filename = f"{student_id}.jpg"
                    image.save(filename)

                    try:
                        drive = create_drive_instance()
                        file_drive = drive.CreateFile({
                            'title': filename,
                            'parents': [{'id': DRIVE_FOLDER_ID}]
                        })
                        file_drive.SetContentFile(filename)
                        file_drive.Upload()
                        st.success(f"✅ '{filename}' uploaded successfully to Google Drive.")
                        st.info(f"Google Drive File ID: {file_drive['id']}")
                        os.remove(filename)
                    except Exception as e:
                        st.error(f"⚠️ Upload failed: {e}")
                else:
                    st.warning("⚠️ Not Acceptable: Face size seems incorrect (too small or too zoomed).")
            elif len(faces) == 0:
                st.error("❌ Not Acceptable: No face detected.")
            else:
                st.error("❌ Not Acceptable: Multiple faces detected.")
