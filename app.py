import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Mapper Pro UI", layout="wide")

st.title("🚀 Mapper Pro UI")
st.write("US → DE Mapping using DE_translated (English Matching)")

file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    st.subheader("🔍 Preview")
    st.dataframe(df.head())

    columns = df.columns.tolist()

    # Column selection
    us_col = st.selectbox("Select US Column", columns)
    de_col = st.selectbox("Select DE Column (Target)", columns)
    de_translated_col = st.selectbox("Select DE_translated Column (English)", columns)

    if st.button("🚀 Run Mapping"):

        # Clean ONLY for matching
        df["_us_clean"] = df[us_col].astype(str).str.lower().str.strip()
        df["_de_trans_clean"] = df[de_translated_col].astype(str).str.lower().str.strip()

        target_list = df["_de_trans_clean"].dropna().unique().tolist()

        # Matching function
        def match(text):
            if not text or text == "nan":
                return ""

            result = process.extractOne(
                text,
                target_list,
                scorer=fuzz.token_sort_ratio
            )

            if result and result[1] >= 90:  # strict threshold
                return result[0]
            return ""

        # Mapping
        mapped_values = []

        for text in df["_us_clean"]:
            matched = match(text)

            if matched:
                original = df[df["_de_trans_clean"] == matched][de_col].values
                mapped_values.append(original[0] if len(original) > 0 else "")
            else:
                mapped_values.append("")

        df["Mapped_DE"] = mapped_values

        # Drop temp columns
        df.drop(columns=["_us_clean", "_de_trans_clean"], inplace=True)

        st.success("✅ Mapping Completed (English Matching Used)")
        st.dataframe(df)

        # Download with accents preserved
        csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

        st.download_button(
            "📥 Download Result",
            csv,
            "mapped_output.csv",
            "text/csv"
        )
