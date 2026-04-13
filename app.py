import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Mapper Pro UI", layout="wide")

st.title("🚀 Mapper Pro UI")
st.markdown("### Smart Mapping: US → DE (via DE_translated)")
st.markdown("⚡ No dropdown | High accuracy | No translation used")

file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    st.subheader("🔍 Data Preview")
    st.dataframe(df.head())

    # ✅ Strict column check
    required_cols = ["US", "DE", "DE_translated"]
    if not all(col in df.columns for col in required_cols):
        st.error("❌ File must contain EXACT columns: US, DE, DE_translated")
    else:
        threshold = st.slider("🎯 Matching Accuracy Threshold", 70, 100, 90)

        if st.button("🚀 Run Mapping"):

            # 🔹 Clean text (important)
            df["US_clean"] = df["US"].astype(str).str.lower().str.strip()
            df["DE_translated_clean"] = df["DE_translated"].astype(str).str.lower().str.strip()

            # 🔹 Lists for matching
            de_translated_list = df["DE_translated_clean"].tolist()
            de_original_list = df["DE"].tolist()

            # 🔹 Matching function
            def match(text):
                if not text:
                    return "", 0

                result = process.extractOne(
                    text,
                    de_translated_list,
                    scorer=fuzz.token_sort_ratio
                )

                if result:
                    _, score, index = result
                    if score >= threshold:
                        return de_original_list[index], score

                return "", 0

            # 🔹 Apply mapping
            results = df["US_clean"].apply(match)

            df["Mapped_DE"] = results.apply(lambda x: x[0])
            df["Match_Score"] = results.apply(lambda x: x[1])

            st.success("✅ Mapping Completed!")

            # 🔍 Show only important columns (clean UI)
            st.dataframe(df[["US", "DE", "DE_translated", "Mapped_DE", "Match_Score"]])

            # ⬇️ Download
            csv = df.to_csv(index=False, encoding="utf-8-sig")

            st.download_button(
                "⬇️ Download Mapped File",
                csv,
                "mapped_us_de.csv",
                "text/csv"
            )
