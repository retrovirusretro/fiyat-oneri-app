import streamlit as st
import pandas as pd

st.set_page_config(page_title="Fiyat Öneri Uygulaması", layout="wide")
st.title("📊 Fiyat Artış / İndirim Öneri Aracı")

uploaded_file = st.file_uploader("Excel dosyanızı yükleyin", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Kolon isimlerindeki boşlukları temizle
    df.columns = df.columns.str.strip()

    # Gerekli kolonlar
    gerekli_kolonlar = ["LotKodu", "TR İlk Fiyat", "SonFiyat", "Avg. Price", "TW Qty.", "TW Cover", "TW Stock Qty.", "Stok Yaşı", "GM %"]
    if all(k in df.columns for k in gerekli_kolonlar):

        # Cost Hesapla
        df["Cost"] = df["Avg. Price"] * (1 - df["GM %"] / 100)

        # Fiyat öneri fonksiyonu
        def fiyat_oneri(row):
            if row["Stok Yaşı"] <= 30 or row["TW Qty."] in [0, None]:
                return "Fiyat Değişimi Önerilmez"
            indirim_orani = 1 - row["SonFiyat"] / row["TR İlk Fiyat"]
            if row["TW Cover"] < 3.5 and indirim_orani < 0.2 and row["TW Stock Qty."] > 15:
                return "Fiyat Artışı Önerisi"
            if row["TW Cover"] > 20 and row["TW Stock Qty."] > 15:
                return "İndirim / Kampanya Önerisi"
            return "Fiyat Değişimi Önerilmez"

        df["Açıklama"] = df.apply(fiyat_oneri, axis=1)

        # KPI Göstergeleri
        st.markdown("### 🎯 KPI Göstergeleri")
        col1, col2, col3 = st.columns(3)
        col1.metric("Ort. GMROI", f"{df['TW GMROI'].mean():.2f}" if "TW GMROI" in df.columns else "TW GMROI verisi eksik")
        col2.metric("Ort. STR %", f"{df['STR %'].mean():.1f}%" if "STR %" in df.columns else "STR % verisi eksik")
        col3.metric("Ort. Cover", f"{df['TW Cover'].mean():.1f}")

        # Filtre kutusu
        st.markdown("### 🔍 Filtrele")
        oneri_turu = st.multiselect("Öneri Türü", df["Açıklama"].unique(), default=df["Açıklama"].unique())

        filtered_df = df[df["Açıklama"].isin(oneri_turu)]

        # Öneri tablosu
        st.markdown("### 📋 Öneri Tablosu")
        if filtered_df.empty:
            st.warning("Seçtiğiniz kriterlere uygun veri bulunamadı.")
        else:
            st.dataframe(filtered_df)

            # CSV İndir
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Sonuçları İndir (CSV)", data=csv, file_name="fiyat_oneri_sonuclar.csv", mime="text/csv")
    else:
        st.warning("Bazı gerekli kolonlar eksik.")
else:
    st.info("Devam etmek için bir dosya yükleyin.")
