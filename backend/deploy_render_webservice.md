# Deploy Backend ke Render (Web Service)

## Persiapan

### 1. Buat `requirements.txt`

Render butuh `requirements.txt` untuk Python. Generate dari pyproject.toml:

```bash
cd backend
pip freeze > requirements.txt
```

Atau buat manual dengan dependencies minimal:

```
fastapi>=0.135.1
uvicorn>=0.41.0
sqlalchemy>=2.0.48
psycopg2-binary>=2.9.0
dynaconf>=3.2.12
python-dotenv>=1.2.2
requests>=2.32.5
strands-agents>=1.29.0
uuid-utils>=0.14.1
pandas>=3.0.1
matplotlib>=3.10.8
```

### 2. Push ke GitHub

Pastikan folder `backend/` sudah di-push ke GitHub repository.

---

## Step-by-Step Deploy

### Step 1: Buat Akun Render

1. Buka https://render.com
2. Sign up dengan GitHub (recommended, supaya bisa connect repo langsung)

### Step 2: Buat PostgreSQL Database (Free)

1. Di Render Dashboard, klik **New** → **PostgreSQL**
2. Isi:
   - **Name**: `grace-db`
   - **Region**: pilih yang terdekat (Singapore jika ada)
   - **Instance Type**: **Free**
3. Klik **Create Database**
4. Setelah dibuat, buka database dan catat **Internal Database URL** (format: `postgresql://user:pass@host/dbname`)
   - Ini akan dipakai sebagai `DATABASE_URL` di web service

> ⚠️ Free tier PostgreSQL di Render berlaku 90 hari. Setelah itu perlu upgrade atau migrate ke Supabase.

### Step 3: Buat Web Service

1. Di Render Dashboard, klik **New** → **Web Service**
2. Connect GitHub repository kamu
3. Konfigurasi:
   - **Name**: `grace-backend`
   - **Region**: sama dengan database
   - **Branch**: `main` (atau branch utama kamu)
   - **Root Directory**: `backend` (PENTING: karena backend ada di subfolder)
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free**

### Step 4: Set Environment Variables

Di halaman Web Service, buka tab **Environment** dan tambahkan:

| Key | Value | Keterangan |
|-----|-------|------------|
| `ALI_ENV` | `prd` | Production environment |
| `ALI_DATABASE_URL` | `postgresql://...` | Internal Database URL dari Step 2 |
| `ALI_POSTGRES_URL` | `postgresql://...` | Sama dengan DATABASE_URL |
| `ALI_TELEGRAM_BOT_TOKEN` | `<token_kamu>` | Token bot Telegram |
| `ALI_ALIBABA_KEY` | `<api_key_kamu>` | API key untuk AI model |
| `ALI_ALIBABA_URL` | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | AI model endpoint |
| `ALI_DEFAULT_MODEL` | `alibaba_qwen_3.5_plus` | Model AI yang dipakai |
| `ALI_SESSION_EXPIRY_HOURS` | `24` | Session expiry |
| `PYTHON_VERSION` | `3.12.0` | Versi Python |

### Step 5: Deploy

1. Klik **Create Web Service**
2. Render akan otomatis build dan deploy
3. Tunggu sampai status **Live**
4. Catat URL service kamu (format: `https://grace-backend-xxxx.onrender.com`)

### Step 6: Verifikasi

Buka di browser:

```
https://grace-backend-xxxx.onrender.com/health
```

Harus mengembalikan response JSON dengan status OK.

---

## Catatan Penting

- **Cold start**: Free tier Render akan spin down setelah 15 menit idle. Request pertama setelah idle butuh ~30 detik untuk wake up.
- **Database 90 hari**: Free PostgreSQL di Render expired setelah 90 hari. Pertimbangkan Supabase untuk long-term.
- **Logs**: Cek logs di Render Dashboard jika ada error saat deploy.
- **CORS**: Backend sudah dikonfigurasi `allow_origins=["*"]`, jadi frontend dari domain manapun bisa akses.
