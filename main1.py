import streamlit as st
import cv2
#import easyocr
import numpy as np
import pytesseract
import drive_methods
from langchain_groq import ChatGroq
import os
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import hashlib
import os

   
class Employee(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    organisation: Optional[str] = None
    
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    phone3: Optional[str] = None
    
    email1: Optional[str] = None
    email2: Optional[str] = None
    email3: Optional[str] = None

    address: Optional[str] = None

    Website: Optional[str] = None


os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)
# reader = load_reader()

st.title("📇 Business Card Reader")

uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    def resize_with_max(img, max_w=350, max_h=300):
        h, w = img.shape[:2]
        scale = min(max_w / w, max_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(img, (new_w, new_h))

    resized_img = resize_with_max(img)
    st.subheader("Original Image")
    st.image(resized_img, channels="BGR")
   
    text1 = pytesseract.image_to_string(img)

    st.subheader("Extracted Raw Text")
    st.write(text1)
    def extract_fields(text):
        prompt=f"""You are a helpful business card reader.
        Your job is to classify the content from business card into fields like Employee_Name, organisation_name, phone_number, Adress, website.
        If a value is not available, set it to none. DO NOT ASSUME values, ONLY USE information from given input.
        INPUT: {text}"""
        structured_llm = llm.with_structured_output(Employee)
        response = structured_llm.invoke(prompt)
        return response
    res = extract_fields(text1)
    st.subheader("✏️ Edit Extracted Fields")

    # Convert Pydantic object → dict
    data = res.dict() if res else {}
    image_hash = hashlib.sha256(file_bytes).hexdigest()

    # Initialize or refresh session state when a new image is uploaded
    if st.session_state.get("last_image_hash") != image_hash:
        st.session_state.form_data = data
        st.session_state.last_image_hash = image_hash
    elif "form_data" not in st.session_state:
        st.session_state.form_data = data

    with st.form("edit_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Name", st.session_state.form_data.get("name", ""))
            designation = st.text_input("Designation", st.session_state.form_data.get("designation", ""))
            organisation = st.text_input("Organisation", st.session_state.form_data.get("organisation", ""))

            phone1 = st.text_input("Phone 1", st.session_state.form_data.get("phone1", ""))
            phone2 = st.text_input("Phone 2", st.session_state.form_data.get("phone2", ""))
            phone3 = st.text_input("Phone 3", st.session_state.form_data.get("phone3", ""))

        with col2:
            email1 = st.text_input("Email 1", st.session_state.form_data.get("email1", ""))
            email2 = st.text_input("Email 2", st.session_state.form_data.get("email2", ""))
            email3 = st.text_input("Email 3", st.session_state.form_data.get("email3", ""))

            address = st.text_area("Address", st.session_state.form_data.get("address", ""))
            Website = st.text_area("Website", st.session_state.form_data.get("Website", ""))
            remarks = st.text_area("Remarks", "")

        submitted = st.form_submit_button("💾 Save to drive")

        if submitted:
            # Update session state
            
            final_data = {"Date":str(datetime.today().strftime("%d-%m-%Y")),"name": name,"designation": designation,
                "organisation": organisation,"phone1": phone1,
                "phone2": phone2, "phone3": phone3,
                "email1": email1,"email2": email2,
                "email3": email3,
                "Website": Website, "Remarks": remarks,"address": address, "Raw_text":text1 }
            st.session_state["form_data"] = final_data
            try:
                li=list(final_data.values())
                #print(li)
                drive_methods.write_data(li)

                #save_to_file(final_data)
                st.success("Data Saved successfully!")
            except Exception as e:
                st.success("Failed to save data")
                print(e)
   
                        



