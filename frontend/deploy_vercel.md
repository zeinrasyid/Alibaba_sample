# Deploy Frontend ke Vercel

## Persiapan

Pastikan:
- Backend sudah di-deploy dan punya URL publik (misal: `https://grace-backend-xxxx.onrender.com`)
- Folder `frontend/` sudah di-push ke GitHub

---

## Step-by-Step Deploy

### Step 1: Buat Akun Vercel

1. Buka https://vercel.com
2. Sign up dengan GitHub (recommended)

### Step 2: Import Project

1. Di Vercel Dashboard, klik **Add New** → **Project**
2. Pilih GitHub repository kamu
3. Vercel akan auto-detect Next.js

### Step 3: Konfigurasi Project

1. **Framework Preset**: Next.js (auto-detected)
2. **Root Directory**: klik **Edit** dan isi `frontend` (PENTING: karena frontend ada di subfolder)
3. **Build Command**: `npm run build` (default, tidak perlu diubah)
4. **Output Directory**: biarkan default (`.next`)
5. **Install Command**: `npm install` (default)

### Step 4: Set Environment Variables

Di bagian **Environment Variables**, tambahkan:

| Key | Value | Keterangan |
|-----|-------|------------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://grace-backend-xxxx.onrender.com` | URL backend yang sudah di-deploy di Render |

> Ganti `grace-backend-xxxx` dengan URL asli backend kamu dari Render.

### Step 5: Deploy

1. Klik **Deploy**
2. Tunggu build selesai (biasanya 1-2 menit)
3. Setelah berhasil, Vercel akan memberikan URL (format: `https://grace-xxxx.vercel.app`)

### Step 6: Verifikasi

1. Buka URL Vercel di browser
2. Pastikan landing page tampil dengan benar
3. Coba daftar akun baru
4. Login dengan email yang sudah didaftar
5. Generate API key di dashboard
6. Test copy API key

---

## Custom Domain (Opsional)

Kalau kamu punya domain sendiri:

1. Di Vercel Dashboard, buka project → **Settings** → **Domains**
2. Tambahkan domain kamu
3. Update DNS records sesuai instruksi Vercel

---

## Update Deployment

Setiap kali kamu push ke branch `main` di GitHub, Vercel akan otomatis re-deploy. Tidak perlu manual deploy lagi.

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| API call gagal / CORS error | Pastikan `NEXT_PUBLIC_API_BASE_URL` sudah benar dan backend sudah running |
| Build error | Cek logs di Vercel Dashboard → Deployments → klik deployment → View Build Logs |
| Halaman kosong setelah login | Pastikan backend bisa diakses (cek `<backend_url>/health`) |
| Slow response pertama kali | Normal — Render free tier butuh ~30 detik untuk wake up dari idle |

---

## Urutan Deploy

1. **Deploy backend dulu** di Render (supaya punya URL)
2. **Deploy frontend** di Vercel (pakai URL backend dari step 1)
3. **Test** end-to-end: daftar → login → generate API key → test di Telegram
