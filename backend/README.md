# Financial Assistant AI

Backend AI agent untuk financial assistant yang terintegrasi dengan Telegram. Dibangun menggunakan [Strands Agents](https://github.com/strands-agents/sdk-python) dan FastAPI.

User bisa berinteraksi via Telegram untuk:
- Mencatat transaksi (kirim teks atau foto receipt)
- Mengatur budget per kategori per bulan
- Melihat insight pengeluaran dan chart
- Mendapat peringatan jika pengeluaran mendekati batas budget (≥80%)

## Tech Stack

- Python 3.12+ / FastAPI / Uvicorn
- PostgreSQL 16 (Docker)
- Alibaba Cloud Qwen (via OpenAI-compatible API)
- Strands Agents SDK
- Telegram Bot API (webhook)

## Project Structure

```
├── main.py                          # Entrypoint
├── src/
│   ├── main.py                      # FastAPI app, lifespan, middleware
│   ├── agents/
│   │   └── orchastrator.py          # Agent setup (tools, model, session)
│   ├── instructions/
│   │   └── orchastrator.txt         # System prompt untuk agent
│   ├── api/v1/
│   │   ├── router.py               # REST endpoints (users, api-keys)
│   │   ├── schema.py               # Pydantic models
│   │   └── endpoints/webhooks/
│   │       ├── telegram.py          # Telegram webhook handler
│   │       ├── telegram_auth.py     # Auth (login, session, api-key validation)
│   │       └── telegram_client.py   # Telegram Bot API client
│   ├── tools/
│   │   ├── indonesian_current_time.py
│   │   ├── chart/                   # generate_chart tool
│   │   └── sql_db/
│   │       ├── client.py            # SQLAlchemy engine + Category Literal
│   │       ├── get_db_schema.py     # Schema discovery tool
│   │       ├── query_db.py          # Read-only query (CTE email scoping)
│   │       ├── write_transactions.py
│   │       └── write_budgets.py
│   ├── models/__init__.py           # SQLAlchemy ORM models
│   ├── llm/                         # Model resolver (Qwen via OpenAI provider)
│   ├── core/                        # Config (Dynaconf), logger, exceptions
│   └── utils/                       # agent_helper, rds_helper
├── configs/settings.toml            # App settings (dev/prd)
├── docker-compose.yml               # PostgreSQL container
├── scripts/migrate_schema.sql       # DB migration script
└── tests/                           # Bug condition & preservation tests
```

## Agent Tools

| # | Tool | Deskripsi |
|---|------|-----------|
| 1 | `indonesian_current_time` | Waktu Indonesia (WIB/WITA/WIT) |
| 2 | `generate_chart` | Generate chart dari data |
| 3 | `get_db_schema` | Schema tabel `transactions` / `budgets` |
| 4 | `query_db` | SELECT query (auto-scoped by email via CTE) |
| 5 | `write_transactions` | Insert transaksi (email dari agent state) |
| 6 | `write_budgets` | Insert/update budget (email dari agent state) |

Kategori yang tersedia: `food`, `transport`, `shopping`, `entertainment`, `health`, `bills`, `education`, `other`

## Data Isolation

- `write_transactions` dan `write_budgets` mengambil email dari `ToolContext.agent.state` — agent tidak bisa insert ke email lain.
- `query_db` menggunakan CTE wrapping yang otomatis filter tabel `transactions` dan `budgets` by email. Agent bebas menulis SQL apapun, tapi hanya bisa melihat data milik user yang sedang login.


## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker & Docker Compose
- Telegram Bot Token (dari [@BotFather](https://t.me/BotFather))
- Alibaba Cloud Qwen API Key
- [ngrok](https://ngrok.com/) (untuk development lokal)

## Setup

### 1. Clone & Install Dependencies

```bash
git clone <repository-url>
cd financial-assistant

# Install uv jika belum ada
pip install uv

# Install dependencies
uv sync --extra postgres --extra openai
```

### 2. Environment Variables

Buat file `.env` di root project:

```env
ALI_ENV=dev

# Database
ALI_DATABASE_URL=postgresql://alibaba:alibaba@localhost:5432/financial_assistant

# Telegram
ALI_TELEGRAM_BOT_TOKEN=your_bot_token_here

# Alibaba Qwen
ALI_ALIBABA_KEY=your_qwen_api_key_here
ALI_ALIBABA_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
ALI_DEFAULT_MODEL=alibaba_qwen_3.5_plus

# Session
ALI_AGENT_SESSION=agent_session
ALI_SESSION_EXPIRY_HOURS=24
```

> Semua env var menggunakan prefix `ALI_` (Dynaconf `envvar_prefix`).

### 3. Start PostgreSQL

```bash
docker compose up -d
```

Container `alibaba-postgres` akan running di port 5432 dengan user `alibaba`, password `alibaba`, database `financial_assistant`.

### 4. Migrate Database

```bash
docker exec -i alibaba-postgres psql -U alibaba -d financial_assistant < scripts/migrate_schema.sql
```

Ini akan membuat tabel: `user_info`, `api_keys`, `telegram_users`, `transactions`, `budgets`.

### 5. Run Server

```bash
uv run main.py
```

Server berjalan di `http://localhost:8000`. Health check: `GET /health`.

## Testing via Telegram (Step by Step)

### Step 1: Buat Telegram Bot

1. Buka Telegram, cari **@BotFather**
2. Kirim `/newbot`
3. Ikuti instruksi untuk set nama dan username bot
4. Copy token yang diberikan, masukkan ke `.env` sebagai `ALI_TELEGRAM_BOT_TOKEN`

### Step 2: Expose Local Server dengan ngrok

Buka terminal baru:

```bash
ngrok http 8000
```

Copy URL HTTPS yang muncul (contoh: `https://abc123.ngrok-free.app`).

### Step 3: Set Webhook Telegram

```bash
curl -s "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<NGROK_URL>/api/v1/webhook/telegram"
```

Ganti `<BOT_TOKEN>` dan `<NGROK_URL>` sesuai milikmu. Response yang benar:

```json
{"ok":true,"result":true,"description":"Webhook was set"}
```

### Step 4: Buat User & Generate API Key

```bash
# Buat user baru
curl -s -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "zein", "email": "zein@example.com"}'

# Generate API key
curl -s -X POST http://localhost:8000/api/v1/generate-api-key/ \
  -H "Content-Type: application/json" \
  -d '{"username": "zein", "email": "zein@example.com"}'
```

Catat `api_key` dari response.

### Step 5: Login di Telegram

Buka bot di Telegram, lalu kirim:

```
/start
```

Bot akan menyapa. Kemudian login:

```
/login <API_KEY_KAMU>
```

Jika berhasil, bot akan membalas "Login berhasil!".

### Step 6: Test Fitur

Setelah login, kamu bisa langsung chat dengan bot. Beberapa contoh interaksi:

**Catat transaksi via teks:**
```
Hari ini makan siang di warteg 25rb, bayar cash
```

**Catat transaksi via foto:**
> Kirim foto receipt/struk, bot akan extract dan catat otomatis.

**Set budget:**
```
Set budget makan bulan ini 500rb
```

**Cek pengeluaran:**
```
Berapa total pengeluaran saya bulan ini?
```

**Minta chart:**
```
Tampilkan chart pengeluaran per kategori bulan ini
```

**Cek budget vs spending:**
```
Apakah ada budget yang sudah hampir habis?
```

> Bot akan otomatis memberi peringatan jika pengeluaran di suatu kategori sudah mencapai ≥80% dari budget.

### Step 7: Logout

```
/logout
```

## API Endpoints

| Method | Path | Deskripsi | Query Params |
|--------|------|-----------|--------------|
| `POST` | `/api/v1/users/` | Buat user baru | — |
| `GET` | `/api/v1/users/{email}` | Get user by email | — |
| `POST` | `/api/v1/generate-api-key/` | Generate API key | — |
| `POST` | `/api/v1/validate-api-key/` | Validasi API key | — |
| `GET` | `/api/v1/api-keys/` | List API keys (masked) | `email` |
| `DELETE` | `/api/v1/api-keys/{api_key}` | Revoke API key | — |
| `GET` | `/api/v1/transactions/` | List transaksi user | `email`, `month`, `year`, `page`, `per_page` |
| `GET` | `/api/v1/budgets/` | List budget user | `email`, `month`, `year` |
| `GET` | `/api/v1/summary/` | Ringkasan keuangan bulanan | `email`, `month`, `year` |
| `POST` | `/api/v1/webhook/telegram` | Telegram webhook | — |
| `GET` | `/health` | Health check | — |

**Catatan:**
- Rate limiting pada `generate-api-key` belum diimplementasi

## Running Tests

```bash
uv run pytest tests/ -v
```

## Troubleshooting

| Problem | Solusi |
|---------|--------|
| Webhook tidak jalan | Pastikan ngrok running dan URL webhook benar. Cek `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo` |
| Bot tidak merespon | Cek log server. Pastikan `ALI_TELEGRAM_BOT_TOKEN` benar di `.env` |
| Database error | Pastikan Docker PostgreSQL running (`docker ps`). Cek `ALI_DATABASE_URL` |
| Login gagal | Pastikan user sudah dibuat via API dan API key aktif |
| Agent error | Cek `ALI_ALIBABA_KEY` dan `ALI_ALIBABA_URL`. Pastikan model tersedia |
