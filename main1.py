import streamlit as st
import cv2
#import easyocr
import numpy as np
from PIL import Image
import pytesseract

# Cache the OCR model (important: avoids reloading every time)
# @st.cache_resource
# def load_reader():
#     return easyocr.Reader(['en'], gpu=True)

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
import base64

from pydantic import BaseModel, EmailStr
from typing import Optional

import pandas as pd
import os

FILE_PATH = "cards_data.csv"
COLUMNS = ["name","designation",
                "organisation",
                "phone1",
                "phone2",
                "phone3",
                "email1",
                "email2",
                "email3",
                "address",
                "Website"]
def save_to_file(data):
    new_df = pd.DataFrame([data])

    # Ensure column order
    new_df = new_df.reindex(columns=COLUMNS)

    if os.path.exists(FILE_PATH):
        existing_df = pd.read_csv(FILE_PATH)

        # Align columns if structure changed
        existing_df = existing_df.reindex(columns=COLUMNS)

        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        updated_df = new_df

    updated_df.to_csv(FILE_PATH, index=False)

def create_vcard(final_data):
        vcard = f"""BEGIN:VCARD
        VERSION:3.0
        FN:{final_data.get('name','')}
        ORG:{final_data.get('organisation','')}
        TEL:{final_data.get('phone1','')}
        EMAIL:{final_data.get('email1','')}
        ADR:{final_data.get('address','')}
        END:VCARD
        """
        return vcard
    
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

st.title("📇 Business Card OCR")

uploaded_file = st.file_uploader("Upload a business card image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    st.subheader("Original Image")
    st.image(img, channels="BGR")

    # OCR
    # results = reader.readtext(img)


    # threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.3)

    # annotated = img.copy()

    # extracted_text = []

    # for (bbox, text, score) in results:
    #     if score > threshold:
    #         extracted_text.append(text)

    #         # Convert bbox to int
    #         pts = np.array(bbox).astype(int)

    #         # Draw bounding box
    #         cv2.polylines(annotated, [pts], isClosed=True, color=(0,255,0), thickness=2)

    #         # Put text
    #         cv2.putText(
    #             annotated,
    #             text,
    #             (pts[0][0], pts[0][1] - 5),
    #             cv2.FONT_HERSHEY_SIMPLEX,
    #             0.6,
    #             (255, 0, 0),
    #             2
    #         )

    # st.subheader("Annotated Image")
    # st.image(annotated, channels="BGR")

    # st.subheader("Extracted Text")
    # joined_text = "\n".join(extracted_text)
    # st.write(joined_text)


    text1 = pytesseract.image_to_string(img)

    st.subheader("Extracted Text tesseract")
    st.write(text1)
    def extract_fields(text):
        prompt=f"""You are a helpful business card reader.
        Your job is to classify the content from business card into fields like Employee_Name, organisation_name, phone_number, Adress, website.
        If a value is not available, set it to none. DO NOT ASSUME values, ONLY USE information from given input.
        INPUT: {text}"""
        structured_llm = llm.with_structured_output(Employee)
        response = structured_llm.invoke(prompt)
        return response
    res=extract_fields(text1)
    st.subheader("✏️ Edit Extracted Fields")

    # Convert Pydantic object → dict
    data = res.dict() if res else {}

    vcard_data=data

    # Initialize session state (so edits persist)
    if "form_data" not in st.session_state:
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

        submitted = st.form_submit_button("💾 Save")

        if submitted:
            # Update session state
            final_data = {"name": name,"designation": designation,
                "organisation": organisation,"phone1": phone1,
                "phone2": phone2, "phone3": phone3,
                "email1": email1,"email2": email2,
                "email3": email3,"address": address,
                "Website": Website }
            st.session_state["form_data"] = final_data
    vcard_data = create_vcard(st.session_state["form_data"])
    b64 = base64.b64encode(vcard_data.encode()).decode()
    st.markdown(
    f'<a href="data:text/vcard_data;base64,{b64}">Add Contact</a>',
    unsafe_allow_html=True
)
    st.download_button(
                    label="Save to Contacts",
                    data=vcard_data,
                    file_name="contact.vcf",
                    mime="text/vcard"
                )
            
            # try:
            #     save_to_file(final_data)
            #     st.success("Data Saved successfully!")
            # except Exception as e:
            #     st.success("Failed to save data")

           
                        



