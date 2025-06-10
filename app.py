import streamlit as st
import pandas as pd
from utils import process_excel_file

st.title("Υπολογισμός Ανθρωπομηνών με Εξαίρεση Επικαλύψεων")

uploaded_file = st.file_uploader("Ανέβασε ένα αρχείο Excel", type=["xlsx"])

if uploaded_file:
    df, total_months, output = process_excel_file(uploaded_file)
    
    if df.empty:
        st.warning("Το αρχείο δεν περιέχει έγκυρες περιόδους.")
    else:
        st.write("### Τροποποιημένο αρχείο:")
        st.dataframe(df)
        
        st.write(f"### Συνολικοί Ανθρωπομήνες (χωρίς επικαλύψεις): **{total_months:.1f}**")
        
        st.download_button(
            label="📥 Κατεβάστε το νέο αρχείο Excel",
            data=output,
            file_name="updated_anthropomines.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
