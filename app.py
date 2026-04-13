import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

st.set_page_config(page_title="Mapper Pro UI", layout="wide")

st.title("🚀 Mapper Pro UI")
st.write("Accurate Language Mapping • No Translation • Accent Safe")

file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    st.subheader("🔍 Preview")
    st.dataframe(df.head())

    columns = df.columns.tolist()

    # Select columns
    source_col = st.selectbox("Source Column", columns)
    target_col = st.selectbox(
        "Target Column (Language to map into)",
        [col for col in columns if col != source_col]
    )

    if st.button("🚀 Run Mapping"):

        # Clean ONLY for matching
        df["_source_clean"] = df[source_col].astype(str).str.lower().str.strip()
        df["_target_clean"] = df[target_col].astype(str).str.lower().str.strip()

        target_list = df["_target_clean"].dropna().unique().tolist()

        # Better matching logic
        def match(text):
            if not text or text == "nan":
                return ""

            result = process.extractOne(
                text,
                target_list,
                scorer=fuzz.token_sort_ratio  # better for text variations
            )

            # stricter threshold to avoid wrong mapping
            if result and result[1] >= 85:
                return result[0]
            return ""

        # Apply matching
        mapped_values = []

        for text in df["_source_clean"]:
            matched = match(text)

            if matched:
                # Get original value with accents
                original = df[df["_target_clean"] == matched][target_col].values
                mapped_values.append(original[0] if len(original) > 0 else "")
            else:
                mapped_values.append("")

        df["Mapped_Result"] = mapped_values

        # Drop temp columns
        df.drop(columns=["_source_clean", "_target_clean"], inplace=True)

        st.success("✅ Mapping Completed (No Translation Used)")
        st.dataframe(df)

        # Download with accents preserved
        csv = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

        st.download_button(
            "📥 Download Result",
            csv,
            "mapped_output.csv",
            "text/csv"
        )
