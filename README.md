# kabar.io

`kabar.io` adalah pipeline Python untuk mengambil berita Indonesia dari **NewsData.io**, membersihkan data, memberi label sentimen dengan **Gemini free tier**, lalu menyimpannya ke **Neon Postgres** dengan fallback ke CSV.

## Fitur

- Ambil berita dari beberapa kategori NewsData.io
- Pagination lewat `nextPage`
- Clean data dengan `pandas`
- Analisis sentimen dengan Gemini `gemini-3.5-flash`
- Simpan hasil ke Neon Postgres, fallback ke CSV jika DB tidak tersedia
- Deduplication berdasarkan `article_id`
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
│   ├── neon_handler.py
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
DATABASE_URL=postgresql://user:password@ep-xxxx-pooler.us-east-2.aws.neon.tech/dbname?sslmode=require&channel_binding=require
```

Setting non-secret ada di `config/settings.yml`.

Catatan:

- `NEWSDATA_API_KEY` wajib untuk fetch berita
- `GEMINI_API_KEYS` dipakai untuk sentiment analysis
- `DATABASE_URL` dipakai untuk Neon Postgres, sebaiknya pakai pooled connection string dari Neon Console
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

## Referensi Kategori NewsData

Berikut daftar kategori yang bisa kamu pakai sebagai referensi saat mengatur `config/settings.yml`:

| Category | Parameter API | Contoh konten Indonesia |
| --- | --- | --- |
| Business | `business` | Saham IHSG, BUMN, investasi, startup |
| Crime | `crime` | Korupsi KPK, kriminalitas, fraud |
| Domestic | `domestic` | Isu dalam negeri, kebijakan lokal |
| Education | `education` | Kurikulum Merdeka, SNBT, beasiswa |
| Entertainment | `entertainment` | Selebriti, film, musik Indonesia |
| Environment | `environment` | Bencana alam, deforestasi, kebakaran hutan |
| Food | `food` | Kuliner, pangan, harga bahan pokok |
| Health | `health` | BPJS, wabah, kebijakan Kemenkes |
| Lifestyle | `lifestyle` | Gaya hidup, tren sosial |
| Politics | `politics` | Pilkada, DPR, kebijakan pemerintah |
| Science | `science` | Riset, inovasi, teknologi nuklir |
| Sports | `sports` | Timnas, Liga 1, SEA Games |
| Technology | `technology` | Fintech, AI, regulasi data |
| Top | `top` | Breaking news terpopuler |
| Tourism | `tourism` | Pariwisata, destinasi, MICE |
| World | `world` | Berita global yang menyentuh Indonesia |
| Other | `other` | Tidak terkategori |

## Cara Jalan

### Full pipeline

```bash
python pipeline.py
```

Alur:

1. `NewsDataClient.fetch_all_categories()`
2. `clean_articles()`
3. `analyze_sentiment()`
4. `save_with_fallback(df, OUTPUT_CSV)`

### Mode cepat

Kalau ingin skip sentiment untuk testing:

```bash
python pipeline.py --skip-sentiment
```

## Database

Primary storage project ini adalah Neon Postgres.

Format `DATABASE_URL` yang disarankan:

```env
DATABASE_URL=postgresql://[user]:[password]@[neon_hostname]/[dbname]?sslmode=require&channel_binding=require
```

Kalau kamu mengaktifkan connection pooling di Neon Console, hostname biasanya memakai suffix `-pooler`, misalnya:

```env
DATABASE_URL=postgresql://[user]:[password]@ep-cool-darkness-123456-pooler.us-east-2.aws.neon.tech/[dbname]?sslmode=require&channel_binding=require
```

CSV tetap tersedia sebagai fallback jika `DATABASE_URL` belum diisi atau koneksi database gagal.

## Output

Kalau fallback CSV dipakai, hasil pipeline disimpan ke:

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
- Neon dan CSV sama-sama dedupe berdasarkan `article_id`
- Gemini API free tier dipakai lewat `gemini-3.5-flash`
- Kalau ada beberapa key di `GEMINI_API_KEYS`, sistem akan mencoba key berikutnya saat key sebelumnya kena limit atau error jaringan
- `config/settings.yml` jadi source of truth untuk category, country, language, page size, model, dan fallback CSV

## Lisensi

Belum ditentukan.
