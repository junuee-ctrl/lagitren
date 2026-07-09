import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-md py-16 text-center">
      <p className="text-5xl" aria-hidden>
        🔍
      </p>
      <h1 className="mt-4 text-2xl font-extrabold text-ink">
        Halaman tidak ditemukan
      </h1>
      <p className="mt-2 text-gray-500">
        Tren yang Anda cari mungkin sudah tidak tersedia atau alamatnya salah.
      </p>
      <Link href="/" className="btn-brand mt-6">
        Kembali ke Beranda
      </Link>
    </div>
  );
}
