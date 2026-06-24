import base64
import io
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="SEO Ürün Excel Oluşturucu", page_icon="📦", layout="wide")
st.title("📦 SEO Ürün Adı & Açıklama Excel Oluşturucu")
st.write("Ürün görsellerini yükleyin; sistem her ürün için SEO güçlü başlık, Trendyol/Google uyumlu açıklama ve anahtar kelimeler üretip Excel dosyası verir.")

api_key = st.text_input("OpenAI API Key", type="password", help="API anahtarınız sadece bu oturumda kullanılır.")
model = st.selectbox("Model", ["gpt-4.1", "gpt-4o", "gpt-4o-mini"], index=0)
files = st.file_uploader("Ürün görsellerini yükle", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

SYSTEM_PROMPT = """
Sen Trendyol ve Google SEO konusunda uzman bir e-ticaret ürün içerik editörüsün.
Görseldeki ürünü analiz et ve Türkçe çıktı üret.
Kurallar:
- SEO ürün adı maksimum 100 karakter olsun.
- Ürün adı spam görünmesin, kelime tekrarı yapmasın.
- En güçlü başlık tek bir başlık olmalı.
- Marka uydurma.
- Ürün ölçüsü/kapasitesi görselden kesin anlaşılmıyorsa yazma.
- Açıklama kullanıcıyı bilgilendirsin, satış odaklı ama abartısız olsun.
- Trendyol ve Google için doğal anahtar kelime kullan.
- Sadece geçerli JSON döndür.
JSON formatı:
{
  "urun_kategorisi": "",
  "seo_urun_adi": "",
  "urun_aciklamasi": "",
  "urun_ozellikleri": [""],
  "seo_anahtar_kelimeler": [""]
}
"""

def img_to_data_url(uploaded_file):
    data = uploaded_file.getvalue()
    mime = uploaded_file.type or "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(data).decode("utf-8")

def analyze_image(client, file, model_name):
    data_url = img_to_data_url(file)
    response = client.chat.completions.create(
        model=model_name,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": "Bu ürün görselini analiz et ve Excel'e uygun SEO ürün içeriği hazırla."},
                {"type": "image_url", "image_url": {"url": data_url}}
            ]}
        ],
        temperature=0.4,
    )
    return json.loads(response.choices[0].message.content)

def to_excel(rows):
    df = pd.DataFrame(rows)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Urunler", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Urunler"]
        header_format = workbook.add_format({"bold": True, "bg_color": "#D9EAF7", "border": 1})
        wrap_format = workbook.add_format({"text_wrap": True, "valign": "top"})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        widths = [18, 24, 38, 60, 55, 45]
        for i, width in enumerate(widths):
            worksheet.set_column(i, i, width, wrap_format)
        worksheet.freeze_panes(1, 0)
    output.seek(0)
    return output

if st.button("Excel Oluştur", type="primary"):
    if not api_key:
        st.error("Lütfen OpenAI API Key girin.")
    elif not files:
        st.error("Lütfen en az bir görsel yükleyin.")
    else:
        client = OpenAI(api_key=api_key)
        rows = []
        progress = st.progress(0)
        for idx, file in enumerate(files, start=1):
            with st.spinner(f"Analiz ediliyor: {file.name}"):
                try:
                    result = analyze_image(client, file, model)
                    rows.append({
                        "Görsel Dosya Adı": file.name,
                        "Ürün Kategorisi": result.get("urun_kategorisi", ""),
                        "SEO Ürün Adı": result.get("seo_urun_adi", "")[:100],
                        "Ürün Açıklaması": result.get("urun_aciklamasi", ""),
                        "Ürün Özellikleri": "\n".join(result.get("urun_ozellikleri", [])),
                        "SEO Anahtar Kelimeler": ", ".join(result.get("seo_anahtar_kelimeler", [])),
                    })
                except Exception as e:
                    rows.append({
                        "Görsel Dosya Adı": file.name,
                        "Ürün Kategorisi": "Hata",
                        "SEO Ürün Adı": "",
                        "Ürün Açıklaması": f"Analiz hatası: {e}",
                        "Ürün Özellikleri": "",
                        "SEO Anahtar Kelimeler": "",
                    })
            progress.progress(idx / len(files))
        st.success("Excel hazırlandı.")
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        excel_file = to_excel(rows)
        filename = f"seo_urun_listesi_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        st.download_button("Excel İndir", data=excel_file, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
