# Grace - Your Financial Assistant

Web app untuk Grace, financial assistant AI yang terintegrasi dengan Telegram.

## Prerequisites

- Node.js 18+
- Backend server berjalan di `http://localhost:8000` (lihat `backend/`)

## Setup

```bash
# Install dependencies
npm install

# Buat file environment (sudah ada .env.local)
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Menjalankan Aplikasi

### 1. Jalankan Backend dulu

```bash
cd backend
python main.py
```

Backend akan berjalan di `http://localhost:8000`.

### 2. Jalankan Frontend

```bash
cd frontend
npm run dev
```

Buka [http://localhost:3000](http://localhost:3000) di browser.

## Alur Testing Manual

1. Buka `http://localhost:3000` — landing page Grace
2. Klik "Daftar" atau "Mulai Sekarang"
3. Isi username dan email, lalu submit
4. Setelah berhasil, kamu akan diarahkan ke halaman login
5. Masukkan email yang sudah didaftarkan, lalu login
6. Di dashboard, klik "Generate API Key" untuk mendapatkan API key
7. Salin API key, lalu buka bot Grace di Telegram
8. Kirim `/login <API_KEY>` di Telegram untuk mulai chat

## Halaman

| Route | Deskripsi |
|-------|-----------|
| `/` | Landing page produk |
| `/register` | Halaman registrasi |
| `/login` | Halaman login |
| `/dashboard` | Dashboard (perlu login) |

## Scripts

```bash
npm run dev        # Development server
npm run build      # Production build
npm run start      # Start production server
npm run lint       # ESLint
npm run test       # Jalankan unit tests (Vitest)
npm run test:watch # Jalankan tests dalam watch mode
```

## Tech Stack

- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS + shadcn/ui
- Framer Motion (animasi)
- Recharts (chart keuangan)
- Vitest + React Testing Library (testing)

## Environment Variables

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | URL backend API |
