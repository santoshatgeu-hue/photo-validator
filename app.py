import streamlit as st
import cv2
import numpy as np
from PIL import Image

# -------------------------------
# BASIC CONFIG
# -------------------------------
st.set_page_config(page_title="Passport Photo Validator", page_icon="🪪")
st.title("🪪 Passport Photo Validator")
st.write("Upload a passport-size photograph. The system will check if a full face is visible.")

# --- STEP 1: Student ID Input ---
student_id = st.text_input("Enter Student ID (required):")

# --- STEP 2: File Upload ---
uploaded_file = st.file_uploader("Upload Passport Photo", type=["jpg", "jpeg", "png"])

# --- STEP 3: Google Form Upload Link ---
# Replace this with your actual Google Form pre-fill URL and entry ID for Student ID
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeVMywItDcpk1fJHT4Uj0NARIYVX90yTj9/viewform?usp=pp_url&entry.257403491="

if uploaded_file is not None:
    if not student_id:
        st.warning("⚠️ Please enter your Student ID before uploading.")
    else:
        # Load image
        image = Image.open(uploaded_file).convert("RGB")
        img_array = np.array(image)

        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # Load OpenCV face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        # Draw rectangle around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(img_array, (x, y), (x + w, y + h), (0, 255, 0), 2)

        st.image(img_array, caption="Uploaded Image with Detection", use_column_width=True)

        # --- STEP 4: Face Validation ---
        if len(faces) == 1:
            (x, y, w, h) = faces[0]
            height, width = gray.shape
            face_area_ratio = (w * h) / (width * height)

            if 0.1 < face_area_ratio < 0.6:
                st.success("✅ Acceptable: Full face is visible.")
                
                # Construct Google Form link with student ID pre-filled
                upload_link = f"{GOOGLE_FORM_URL}{student_id}"
                st.markdown(f"### 📤 [Click here to upload your accepted photo to Google Drive via Form]({upload_link})")
                st.info("The above link will open your institution’s official upload form where you can attach your photo.")
            else:
                st.warning("⚠️ Not Acceptable: Face size seems incorrect (too small or too zoomed).")
        elif len(faces) == 0:
            st.error("❌ Not Acceptable: No face detected.")
        else:
            st.error("❌ Not Acceptable: Multiple faces detected.")
