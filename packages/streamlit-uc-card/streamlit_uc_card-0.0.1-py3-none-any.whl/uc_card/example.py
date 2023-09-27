import streamlit as st
from uc_card import uc_card


col1, col2 = st.columns(2)
with col1.container():
    uc = dict(title="AI for Patient Data Management",
            industry="Insurance",
            business_value="Cost Reduction",
            domain_and_process="Customer Service",
            complexity="High",
            technique=['Deep Learning', 'Natural Language Processing'],
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla vitae elit libero, a pharetra augue.",
            image_url="http://34.90.113.6:5000/generated/1695662156-0.png"
    )
    uc_card(**uc)

with col2.container():
    uc2 = dict(title="Anomaly Detection in Manufacturing",
            industry="Manufacturing",
            business_value="Quality Improvement",
            domain_and_process="Marketing",
            complexity="Low",
            technique=['ML', 'NLP', 'Fine-Tuning'],
            description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla vitae elit libero, a pharetra augue.",
            image_url="http://34.90.113.6:5000/generated/1695663559-0.png"
    )
    uc_card(**uc2)
