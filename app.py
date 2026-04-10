import streamlit as st
import pandas as pd
from rapidfuzz import process
import deepl

# -------- PAGE CONFIG --------
st.set_page_config(page_title="Mapper Pro UI", layout="wide")

# -------- HEADER --------
st.markdown("""
<div style='background-color:#232F3E;padding:15px;border-radius:8px'>
<h2 style='color:white;margin:0;'>🚀 Mapper Pro UI</h2>
<p style='color:#D5DBDB;margin:0;'>DeepL Powered • Smart Mapping • Accent Safe</p>
</div>
""", unsafe_allow_html=True)

st.write("")

# -------- API KEY --------
auth_key = st.text_input("🔑 Enter DeepL API Key", type="password")

# -------- FILE UPLOAD --------
file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if file and auth_key:

    df = pd.read_excel(file)

    st.subheader("🔍 Preview")
    st.dataframe(df.head(), use_container_width=True)

    columns = df.columns.tolist()

    col1, col2 = st.columns(2)

    with col1:
        source_col = st.selectbox("Source Column", columns)

    with col2:
        target_col = st.selectbox("Target Column (Language to map into)", columns)

    # -------- RUN BUTTON --------
    if st.button("🚀 Run Mapping"):

        translator = deepl.Translator(auth_key)

        st.info("🔄 Translating using DeepL...")

        translated_list = []

        for text in df[source_col]:
            if pd.isna(text):
                translated_list.append("")
            else:
                try:
                    result = translator.translate_text(
                        str(text),
                        target_lang=target_col.upper()  # DE / FR / NL etc
                    )
                    translated_list.append(result.text)
                except:
                    translated_list.append("")

        df["AUTO_TRANSLATED"] = translated_list

        st.info("🔍 Matching values...")

        # -------- CLEAN FOR MATCHING ONLY --------
        source_clean = df["AUTO_TRANSLATED"].astype(str).str.strip().str.casefold()
        target_clean = df[target_col].astype(str).str.strip().str.casefold()

        # -------- MAP BACK TO ORIGINAL (KEEPS ACCENTS) --------
        clean_to_original = dict(zip(target_clean, df[target_col]))
        target_list = list(clean_to_original.keys())

        def match(text):
            if pd.isna(text):
                return ""

            text_clean = str(text).strip().casefold()
            result = process.extractOne(text_clean, target_list)

            if result and result[1] >= 90:
                return clean_to_original.get(result[0], "")
            return ""

        df["Matched_Result"] = df["AUTO_TRANSLATED"].apply(match)

        df["Status"] = df["Matched_Result"].apply(
            lambda x: "Matched" if x else "Not Matched"
        )

        st.success("✅ Mapping Completed!")

        st.dataframe(df, use_container_width=True)

        # -------- SUMMARY --------
        total = len(df)
        matched = (df["Status"] == "Matched").sum()

        st.markdown(f"""
        ### 📊 Summary
        - Total Rows: **{total}**
        - Matched: **{matched}**
        - Unmatched: **{total - matched}**
        """)

        # -------- DOWNLOAD (ACCENT SAFE) --------
        csv = df.to_csv(index=False, encoding="utf-8-sig")

        st.download_button(
            "⬇️ Download Result",
            csv,
            "mapped_output.csv",
            "text/csv"
        )
