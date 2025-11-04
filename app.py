import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pydrive2.auth import ServiceAccountCredentials
from pydrive2.drive import GoogleDrive
import tempfile
import os

# --- Google Drive Authentication ---
SCOPE = ['https://www.googleapis.com/auth/drive.file']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', SCOPE)
drive = GoogleDrive(creds)

# --- Streamlit UI ---
st.title("📸 Passport Photo Validator & Uploader")
st.write("Upload a passport-size photo. The system will accept it only if a full face is visible.")

student_id = st.text_input("Enter Student ID:")
uploaded_file = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])

if uploaded_file and student_id:
    image = Image.open(uploaded_file)
    img_array = np.array(image.convert('RGB'))

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 1:
        st.success("✅ Acceptable — Full face detected.")

        # Save image temporarily
        temp_path = os.path.join(tempfile.gettempdir(), f"{student_id}.jpg")
        image.save(temp_path)

        # Upload to Google Drive folder
        FOLDER_ID = "1aD2BIdry9WNreOOoiGXau3FNvNJh-9FO"
        file_drive = drive.CreateFile({'title': f"{student_id}.jpg", 'parents': [{'id': FOLDER_ID}]})
        file_drive.SetContentFile(temp_path)
        file_drive.Upload()

        st.success(f"📁 File uploaded successfully to Google Drive as {student_id}.jpg")

        os.remove(temp_path)

    elif len(faces) == 0:
        st.error("❌ No face detected. Please upload a clear passport photo.")
    else:
        st.error("❌ Multiple faces detected. Only one face should be visible.")
