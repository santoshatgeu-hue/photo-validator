import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

st.set_page_config(page_title="Passport Photo Validator", page_icon="🪪")
st.title("🪪 Passport Photo Validator & Uploader")

st.write("### Upload a passport-size photo.")
st.write("The app will verify if a **full face is visible** and upload it to Google Drive if acceptable.")

# --- Step 1: Input Student ID ---
student_id = st.text_input("Enter Student ID (required):")

# --- Step 2: File Upload ---
uploaded_file = st.file_uploader("Upload Passport Photo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    if not student_id:
        st.warning("⚠️ Please enter your Student ID before uploading the file.")
    else:
        # Read image
        image = Image.open(uploaded_file).convert("RGB")
        img_array = np.array(image)

        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Load OpenCV's face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        # Draw rectangle around face(s)
        for (x, y, w, h) in faces:
            cv2.rectangle(img_array, (x, y), (x + w, y + h), (0, 255, 0), 2)

        st.image(img_array, caption="Uploaded Image with Detection", use_column_width=True)

        # --- Step 3: Decision logic ---
        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            height, width = gray.shape
            face_area_ratio = (w * h) / (width * height)

            if 0.1 < face_area_ratio < 0.6:
                st.success("✅ Acceptable: Full face is visible.")

                # Save locally with student_id as filename
                filename = f"{student_id}.jpg"
                image.save(filename)

                # --- Step 4: Upload to Google Drive ---
                try:
                    gauth = GoogleAuth()
                    gauth.LocalWebserverAuth()
                    drive = GoogleDrive(gauth)

                    # Upload file
                    file_drive = drive.CreateFile({'title': filename})
                    file_drive.SetContentFile(filename)
                    file_drive.Upload()
                    st.success(f"✅ File '{filename}' uploaded successfully to Google Drive.")
                    st.info(f"Google Drive File ID: {file_drive['id']}")
                except Exception as e:
                    st.error(f"⚠️ Google Drive upload failed: {e}")

            else:
                st.warning("⚠️ Not Acceptable: Face size seems incorrect (too small or too zoomed).")
        elif len(faces) == 0:
            st.error("❌ Not Acceptable: No face detected.")
        else:
            st.error("❌ Not Acceptable: Multiple faces detected.")
