import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Passport Photo Validator", page_icon="🪪")

st.title("🪪 Passport Photo Validator")
st.write("Upload a passport-size photo. The app will check if a full face is visible.")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read image
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Load OpenCV's pretrained Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img_array, (x, y), (x + w, y + h), (0, 255, 0), 2)

    st.image(img_array, caption="Uploaded Image with Detection", use_column_width=True)

    # Check face detection result
    if len(faces) == 1:
        (x, y, w, h) = faces[0]
        height, width = gray.shape

        # Check if face occupies reasonable area (not too zoomed or cut)
        face_area_ratio = (w * h) / (width * height)
        if 0.1 < face_area_ratio < 0.6:
            st.success("✅ Acceptable: Full face is visible.")
        else:
            st.warning("⚠️ Not Acceptable: Face size seems incorrect (too small or too zoomed).")
    elif len(faces) == 0:
        st.error("❌ Not Acceptable: No face detected.")
    else:
        st.error("❌ Not Acceptable: Multiple faces detected.")
