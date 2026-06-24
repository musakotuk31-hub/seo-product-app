# SEO Ürün Excel Oluşturucu

Bu uygulama ürün görsellerinden SEO uyumlu ürün adı, açıklama, özellik ve anahtar kelime üretir. Sonuçları Excel olarak indirmenizi sağlar.

## Online Yayına Alma - Streamlit Cloud

1. Bu klasörü GitHub'a yükleyin.
2. https://share.streamlit.io üzerinden yeni app oluşturun.
3. `app.py` dosyasını ana dosya olarak seçin.
4. Yayına aldıktan sonra uygulamada OpenAI API Key girin.
5. Ürün görsellerini yükleyip Excel oluşturun.

## Yerelde Çalıştırma

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Excel Kolonları

- Görsel Dosya Adı
- Ürün Kategorisi
- SEO Ürün Adı
- Ürün Açıklaması
- Ürün Özellikleri
- SEO Anahtar Kelimeler

## Not

Ürün kapasitesi, ölçüsü veya materyali görselden kesin anlaşılmıyorsa sistem uydurmaz. Başlık maksimum 100 karakter olacak şekilde hazırlanır.
