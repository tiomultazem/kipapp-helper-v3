# KiPApp Helper v3

Masih pake versi 2? Ga mau pindah ke versi ini yang berkali lipat lebih cepat? Gapapa, emang ga semua siap dengan perubahan.

FYI, kalo v2 bisa entri satu baris SKP anda dalam **10 detik**, v3 ini cuma butuh **1.5 detik untuk entri 12 baris**.

Ini ga bohong. Ini hasil 1x uji coba dummy SKP.

Masih gak mau pindah ke v3? Yaudah.

---

## Persiapan
Saya asumsikan anda lanjut membaca karena ingin pindah ke versi 3. Here we go.
1. Download dan instal Git.
> [!NOTE]
> Git itu wajib ya. Titik. Buat apa? Untuk download dan update. Selain pakai Git, anda harus download dan update manual.
2. Download dan instal Python (kalo anda pengguna KiPApp Helper versi 2, gausah instal lagi)
3. Siapkan excel SKP dengan 10 kolom urut dari kiri. Yang tidak berbintang berarti boleh kosongan.
- *Start Date     : Format tanggal "YYYY-MM-DD".
- End Date        : Diisi hanya bila menggunakan rentang tanggal. Format tanggal YYYY-MM-DD.
- Jam Mulai       : Diisi hanya bila menggunakan rentang jam. Pastikan formatnya "HH:MM" 24 jam dengan angka menit kelipatan 15.
- Jam Selesai     : Diisi hanya bila menggunakan rentang jam. Pastikan formatnya "HH:MM" 24 jam dengan angka menit kelipatan 15.
- *Rencana Kinerja: Kosongkan dulu aja. Nanti diisi di bagian [**Panduan Penggunaan**](#panduan-penggunaan) di bawah ini.
- *Kegiatan       : Minimal 10 karakter.
- *Capaian        : Minimal 10 karakter.
- *Progres        : Diisi 1-100, aku biasa kuisi 100.
- *Link Bukti     : Diisi berupa link. Upload dulu ke drive mu.
- *Centang        : Diisi 1 bila masuk ke capaian, dan 0 bila tidak. Biasanya aku selalu 1.

---

## Instalasi
1. Buka CMD di direktori tempat anda mau simpan KiPApp Helper v3.
2. Ketikkan dan enter satupersatu baris:
   ```cmd
   git clone https://github.com/tiomultazem/kipapp-helper-v3
   cd kipapp-helper-v3
   python main.py
   ```
3. (Bila anda ngeyel tidak menginstal Git) Download manual, ekstrak ke file manager anda. Jalankan dengan klik 2x file `run.bat` 
4. Jendela KiPApp Helper v3 akan terbuka.
5. Buka file env, isi username dan password SSO anda. Lalu simpan dan edit namanya menjadi ".env"
pake titik di depannya.

> [!NOTE]
> Anda tidak perlu pusing instal dependensi manual. Cukup jalankan `python main.py`, dan aplikasi akan otomatis menyiapkan semuanya untuk anda.

---

## Panduan Penggunaan
1. Saya asumsikan udah ada .env berisi SSO BPS anda. klik "impor SSO".
2. Klik login. Pop-up OTP akan muncul bila SSO anda menggunakan OTP. Login berhasil ditandai dengan pesan log "Login sukses!" dan
tombol logout merah muncul.
3. SKP dan RK akan dimuat otomatis setelah login. Pilih SKP yang akan anda entri dari dropdown. Pastikan sudah membuat wadah periodiknya di KiPApp.
> Saya berencana menambahkan fitur pembuatan wadah periodik ini, tapi nanti ketika tidak malas.
4. Perhatikan bahwa baris-baris RK memiliki nomor di kolom "No.".
5. Buka Excel SKP anda yang sudah disiapkan. Isi di kolom Rencana Kinerja dengan nomor sesuai nomor di KiPApp Helper. Simpan.
6. Impor Excel SKP tersebut ke aplikasi dengan klik "Impor Kegiatan". 
7. Akan muncul tombol "Ubah RK". Klik untuk mengubah angka-angka RK di SKP anda yang mau dientri dengan RK yang sesungguhnya. KiPApp Helper akan otomatis mengubahnya.
8. Pastikan kolom berbintang sudah diisi semua, dan isian sudah benar. Siap entri? klik tombol biru "Entri".
9. Bila SKP anda berjumlah 100 baris, estimasi saya tidak akan sampai 10 detik seluruhnya sudah terinput ke KiPApp. Bisa dilihat di pesan log, berapa lama entri KiPApp anda berjalan.
10. Silakan buka browser anda dan login ke KiPApp, buka periode SKP yang barusan anda entri. SKP anda sudah terentri seluruhnya kan?
11. (Opsional) Klik tombol logout dan tutup aplikasi. 

Sekarang tau kan, bahwa kecepatan entri KiPApp Helper v3 **sangat sangat brutal**? Bikin v2 terasa seperti alat purba. Sudah, tutup mulut anda yang menganga itu.

---

## QnA
Silakan ke [QnA KiPApp Helper](https://s.bps.go.id/kipapp-helper-qna)  untuk bertanya jawab.

---

## FAQ

| Pertanyaan | Jawaban |
|---|---|
| **Apakah ini aman untuk SSO? Mengingat loginnya butuh SSO?** | Sangat aman dari ekspose ke pihak luar, termasuk ke saya sendiri. Saya tidak mencantumkan method apapun untuk mencuri SSO anda—buat apa? SSO saya sendiri sudah cukup membuat pusing. |
| **Apa jaminan bahwa SSO saya (pengguna) pasti aman?** | Kode saya sangat mudah dibongkar. Silakan dibongkar dan dicari bagian mana yang anda curigai melakukan pencurian SSO anda. |
| **Apa motivasi anda (developer) mengembangkan aplikasi ini, bila anda tidak berniat mencuri data pegawai lain maupun tidak memonetisasi?** | Cuma sekedar berbagi kebahagiaan. Saya pusing entri SKP satu-persatu manual, maka saya membuat alat ini. Mau tidak pusing juga? Ayo pake alat saya juga. Harapannya sih pusing anda berkurang. Saya hepi, anda hepi juga. Ga mau karena trust issue? Yasudah, ga maksa. |
| **Bisakah kami review kode bersama anda?** | Bisa. Baik untuk kepentingan satker maupun pribadi, silakan kontak saya terlebih dahulu untuk janjian tanggal dan waktunya. |

---

## Kompatibilitas Versi
Aplikasi ini mendukung versi 3.12, 3.13, dan 3.14. Gausah repot-repot hapus versi python anda
demi mencocokkan versi pengembangan saya yang menggunakan python 3.12.7 ini. Pokoknya,
`main.py` akan pintar mendeteksi versi Python yang anda gunakan dan menjalankan modul yang paling sesuai.

---

## Lisensi
Hak Cipta © 2025 Gilang Wahyu Prasetyo, BPS Kabupaten Tabalong.  
Seluruh hak cipta dilindungi undang-undang. Penggunaan perangkat lunak ini tunduk pada ketentuan dalam file [LICENSE](LICENSE).