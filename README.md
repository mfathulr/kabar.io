# kabar.io

`kabar.io` adalah pipeline Python untuk mengambil berita Indonesia dari **NewsData.io**, membersihkan data, memberi label sentimen dengan **Gemini free tier**, lalu menyimpannya ke **Neon Postgres** dengan fallback ke CSV.

## Fitur

- Ambil berita dari beberapa kategori NewsData.io
- Pagination lewat `nextPage`
- Clean data dengan `pandas`
- Analisis sentimen dengan Gemini `gemini-2.5-flash`
- Simpan hasil ke Neon Postgres, fallback ke CSV jika DB tidak tersedia
- Deduplication berdasarkan `article_id`

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
├── migrations/
│   └── 001_news_articles.sql
├── scripts/
│   ├── run_fetch_news.sh
│   └── run_sentiment_worker.sh
├── sentiment_worker.py
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
# Available category sets:
# - balanced
# - broader
# - local
# - economy
newsdata:
  base_url: https://newsdata.io/api/1
  country: id
  language: id,en
  page_size: 15
  active_category_set: balanced
  category_sets:
    balanced:
      - politics
      - business
      - technology
      - health
      - world
    broader:
      - politics
      - business
      - technology
      - health
      - world
      - entertainment
      - sports
    local:
      - domestic
      - politics
      - education
      - crime
      - health
    economy:
      - business
      - technology
      - domestic
      - world
      - politics
  categories:
    - politics
    - business
    - technology
    - health
    - world
  credit_budget_per_day: 200
  credit_buffer: 30
  max_pages_per_category: 4

gemini:
  model: gemini-2.5-flash

output:
  csv: data/news.csv
```

Kalau mau pakai kategori tertentu saja, cukup ganti `active_category_set` atau edit `categories` secara manual.
Kalau kamu mau cek daftar kategori resmi NewsData.io yang lebih lengkap, rujuk dokumentasi resminya karena project ini sekarang memakai preset yang bisa diubah dari config.

### Strategi Kombinasi Kategori

Default yang saya sarankan untuk free tier adalah `balanced`:

- `politics`
- `business`
- `technology`
- `health`
- `world`

Kenapa ini aman:

- cukup beragam untuk feed harian
- masih relevan untuk berita Indonesia
- mudah dikembangkan ke `broader` kalau kredit masih longgar

Guard yang dipakai pipeline:

- `credit_budget_per_day: 200`
- `credit_buffer: 30`
- `max_pages_per_category: 4`

Artinya pipeline akan berhenti lebih awal supaya ada sisa sekitar 30 credit sebagai buffer harian, jadi tidak habis mentok di limit.

Dengan `page_size: 15`, estimasi untuk preset `balanced` sekarang jadi:

- `5 kategori x 4 page x 15 artikel = 300 artikel` per run maksimal
- konsumsi kredit sekitar `5 kategori x 4 page x 2 credit = 40 credit`
- sisa buffer harian tetap besar di bawah limit `200/day`

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

### Fetch Harian

```bash
./scripts/run_fetch_news.sh
```

Alur:

1. `NewsDataClient.fetch_all_categories()`
2. `clean_articles()`
3. `save_with_fallback(df, OUTPUT_CSV)`

Fetch dilakukan round-robin per kategori, bukan habiskan satu kategori sampai selesai dulu. Jadi hasilnya lebih campur dan lebih enak buat feed.

### Sentiment Worker

```bash
./scripts/run_sentiment_worker.sh
```

Worker ini:

1. klaim maksimal 5 row `pending`
2. urutkan berdasarkan `published_at_wib ASC`
3. klasifikasikan sentiment per artikel
4. update `sentiment`, `sentiment_confidence`, `sentiment_reason`, `sentiment_status`, `sentiment_processed_at`, dan `sentiment_last_error`

### Manual Debug

Kalau mau jalan langsung tanpa wrapper:

```bash
.venv/bin/python pipeline.py --skip-sentiment
.venv/bin/python sentiment_worker.py --batch-size 5
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

## Migration Schema

Schema utama Neon disimpan di satu file:

```text
migrations/001_news_articles.sql
```

File ini jadi source of truth untuk tabel `news_articles`. Kalau nanti ada fitur baru yang butuh perubahan schema, kamu bisa buat migration nomor berikutnya dulu sebagai file terpisah, lalu gabungkan atau squash kembali ke file utama saat sudah stabil.

## Cron Setup

Untuk skenario ini, strategi yang paling aman adalah memisahkan job fetch dan job sentiment.

Rekomendasi cron:

```cron
CRON_TZ=Asia/Jakarta
0 6 * * * /home/devuser/projects/kabar.io/scripts/run_fetch_news.sh
*/10 * * * * /home/devuser/projects/kabar.io/scripts/run_sentiment_worker.sh
```

Arti jadwalnya:

- `run_fetch_news.sh` jalan sekali sehari jam 06:00 WIB
- `run_sentiment_worker.sh` jalan setiap 10 menit
- worker sentiment mengambil maksimal 5 artikel `pending` paling lama
- urutan pemrosesan: `published_at_wib ASC`, lalu `fetched_at ASC`

Script yang dijalankan cron:

```text
scripts/run_fetch_news.sh
scripts/run_sentiment_worker.sh
```

Script fetch:

- pindah ke root repo
- memastikan folder `logs/` ada
- menulis output ke `logs/fetch.log`

Script sentiment:

- pindah ke root repo
- memastikan folder `logs/` ada
- menulis output ke `logs/sentiment.log`
- mengklaim row `pending` lalu menandai `processing` sebelum update hasil

Status sentiment yang dipakai:

- `pending` = belum diproses atau perlu retry
- `processing` = sedang diklaim worker
- `done` = sentiment, confidence, dan reason sudah terisi

Kalau ada row yang gagal terus, worker tetap membatasi retry lewat `sentiment_attempts`.

Contoh cleanup log mingguan:

```cron
0 0 * * 1 find /home/devuser/projects/kabar.io/logs -name "*.log" -mtime +7 -delete
```

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

Di Neon, status sentiment juga tersedia:

- `sentiment_status`
- `sentiment_attempts`
- `sentiment_processed_at`
- `sentiment_last_error`

## Catatan Perilaku

- `fetch_latest()` akan retry sekali kalau kena `ConnectionError`
- Kalau API mengembalikan `429`, artikel pada kategori itu akan dilewati
- Sentiment diproses per batch 10 baris dengan jeda 1 detik antar batch
- Neon dan CSV sama-sama dedupe berdasarkan `article_id`
- Gemini API free tier dipakai lewat `gemini-2.5-flash`
- Kalau ada beberapa key di `GEMINI_API_KEYS`, sistem akan mencoba key berikutnya saat key sebelumnya kena limit atau error jaringan
- `config/settings.yml` jadi source of truth untuk category, country, language, page size, model, dan fallback CSV
- `scripts/run_fetch_news.sh` dipakai untuk cron fetch harian
- `scripts/run_sentiment_worker.sh` dipakai untuk cron sentiment setiap 10 menit

## Lisensi

MIT License. Lihat file [`LICENSE`](./LICENSE) untuk teks lengkap.
