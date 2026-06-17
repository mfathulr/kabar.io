# kabar.io

`kabar.io` adalah pipeline Python untuk mengambil berita Indonesia dari **NewsData.io**, membersihkan data, memberi label sentimen dengan **Gemini free tier**, lalu menyimpannya ke CSV.

## Fitur

- Ambil berita dari beberapa kategori NewsData.io
- Pagination lewat `nextPage`
- Clean data dengan `pandas`
- Analisis sentimen dengan Gemini `gemini-3.5-flash`
- Simpan hasil ke CSV dengan deduplication berdasarkan `article_id`
- Mode cepat tanpa sentiment untuk testing

## Struktur Proyek

```text
kabar.io/
├── .env
├── config.py
├── config/
│   └── settings.yml
├── collectors/
│   └── newsdata_client.py
├── processors/
│   ├── cleaner.py
│   └── sentiment.py
├── storage/
│   └── csv_handler.py
├── pipeline.py
└── requirements.txt
```

## Kebutuhan

- Python 3.10+
- API key NewsData.io
- Satu atau beberapa API key Gemini jika ingin menjalankan sentiment analysis

## Instalasi

1. Buat virtual environment

```bash
python -m venv .venv
```

2. Aktifkan environment

```bash
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

## Konfigurasi Env

Pakai `.env` di root project untuk secret:

```env
NEWSDATA_API_KEY=your_key_here
GEMINI_API_KEYS=key1,key2,key3
```

Setting non-secret ada di `config/settings.yml`.

Catatan:

- `NEWSDATA_API_KEY` wajib untuk fetch berita
- `GEMINI_API_KEYS` dipakai untuk sentiment analysis
- Tidak ada hardcoded key di source code

## Config YAML

Edit file ini untuk ubah category dan constant lain:

```text
config/settings.yml
```

Contoh isi:

```yaml
# Categories enabled by default in this project:
# - politics
# - business
# - technology
# - health
newsdata:
  base_url: https://newsdata.io/api/1
  country: id
  language: id,en
  page_size: 10
  categories:
    - politics
    - business
    - technology
    - health

gemini:
  model: gemini-3.5-flash

output:
  csv: data/news.csv
```

Kalau mau pakai kategori tertentu saja, cukup hapus item yang tidak dibutuhkan dari `categories`.
Kalau kamu mau cek daftar kategori resmi NewsData.io yang lebih lengkap, rujuk dokumentasi resminya karena project ini hanya mengaktifkan 4 kategori di config default.

## Cara Jalan

### Full pipeline

```bash
python pipeline.py
```

Alur:

1. `NewsDataClient.fetch_all_categories()`
2. `clean_articles()`
3. `analyze_sentiment()`
4. `save_to_csv(df, "data/news_raw.csv")`

### Mode cepat

Kalau ingin skip sentiment untuk testing:

```bash
python pipeline.py --skip-sentiment
```

## Output

Hasil pipeline disimpan ke:

```text
data/news.csv
```

Kolom utama yang dipakai:

- `article_id`
- `title`
- `description`
- `source_id`
- `source_url`
- `country`
- `category`
- `language`
- `pubDate`
- `fetched_at`
- `pub_date_wib`
- `domain`
- `sentiment`
- `sentiment_confidence`
- `sentiment_reason`

## Catatan Perilaku

- `fetch_latest()` akan retry sekali kalau kena `ConnectionError`
- Kalau API mengembalikan `429`, artikel pada kategori itu akan dilewati
- Sentiment diproses per batch 10 baris dengan jeda 1 detik antar batch
- CSV akan dideduplicate berdasarkan `article_id`
- Gemini API free tier dipakai lewat `gemini-3.5-flash`
- Kalau ada beberapa key di `GEMINI_API_KEYS`, sistem akan mencoba key berikutnya saat key sebelumnya kena limit atau error jaringan
- `config/settings.yml` jadi source of truth untuk category, country, language, page size, model, dan output CSV

## Lisensi

Belum ditentukan.
