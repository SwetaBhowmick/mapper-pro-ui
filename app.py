import streamlit as st
import pandas as pd
from rapidfuzz import process
import requests

# ------------------ UI HEADER ------------------ #
st.set_page_config(page_title="Mapper Pro UI", layout="wide")

st.markdown("""
    <h1 style='text-align: center;'>🚀 Mapper Pro UI</h1>
    <p style='text-align: center; font-size:18px;'>
    Smart Language Mapping • Accent Safe • Auto Detection
    </p>
""", unsafe_allow_html=True)

# ------------------ API KEY ------------------ #
deepl_api_key = st.text_input("🔑 Enter DeepL API Key (Optional)", type="password")

# ------------------ FILE UPLOAD ------------------ #
file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    st.subheader("🔍 Preview")
    st.dataframe(df.head())

    columns = df.columns.tolist()

    # ------------------ COLUMN SELECTION ------------------ #
    source_col = st.selectbox("Source Column", columns)

    target_options = [col for col in columns if col != source_col]
    target_col = st.selectbox("Target Column (Language to map into)", target_options)

    # ------------------ BUTTON ------------------ #
    if st.button("🚀 Run Mapping"):

        # Clean text ONLY for matching (not original data)
        df["__source_clean"] = df[source_col].astype(str).str.lower().str.strip()
        df["__target_clean"] = df[target_col].astype(str).str.lower().str.strip()

        target_list = df["__target_clean"].dropna().tolist()

        # ------------------ MATCH FUNCTION ------------------ #
        def match(text):
            result = process.extractOne(text, target_list)
            if result and result[1] > 90:
                return result[0]
            return ""

        # ------------------ CHECK IF TRANSLATION NEEDED ------------------ #
        use_translation = False

        if target_col not in df.columns or df[target_col].isna().all():
            use_translation = True

        # ------------------ TRANSLATION FUNCTION ------------------ #
        def translate(text):
            url = "https://api-free.deepl.com/v2/translate"
            params = {
                "auth_key": deepl_api_key,
                "text": text,
                "target_lang": "DE"
            }
            response = requests.post(url, data=params)
            return response.json()["translations"][0]["text"]

        # ------------------ PROCESS ------------------ #
        results = []

        for idx, row in df.iterrows():
            text = row["__source_clean"]

            # 👉 Only translate if needed
            if use_translation and deepl_api_key:
                try:
                    text = translate(text).lower().strip()
                except:
                    text = row["__source_clean"]

            matched = match(text)

            # Get ORIGINAL value with accents
            if matched:
                original_match = df[df["__target_clean"] == matched][target_col].values
                if len(original_match) > 0:
                    results.append(original_match[0])
                else:
                    results.append("")
            else:
                results.append("")

        df["Mapped_Result"] = results

        # Drop temp columns
        df.drop(columns=["__source_clean", "__target_clean"], inplace=True)

        st.success("✅ Mapping Completed!")
        st.dataframe(df)

        # ------------------ DOWNLOAD ------------------ #
        csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

        st.download_button(
            "📥 Download Result",
            csv,
            "mapped_output.csv",
            "text/csv"
        )
