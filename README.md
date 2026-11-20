# Bizim Masalar

Arkadaş grubunun favori mekânlarının izometrik 3D maketleri. Her masaya tıklanır; o masada yaşanan anılar, fotoğraflar ve yorumlar açılır.
Mekânlarla resmi bir bağı yoktur.

- **Site:** statik (GitHub Pages). Three.js ve Firebase SDK'sı CDN'den yüklenir; derleme adımı yok.
- **Veri:** Firebase (ücretsiz Spark planı) — Google ile giriş + Firestore. Fotoğraflar sıkıştırılıp Firestore belgelerinde tutulur (Storage kullanılmaz).
- **Maketler:** Blender'da Python betiğiyle üretilir (`scripts/`), `.glb` olarak `assets/models/` altına konur.

## Kurulum

1. **Firebase**
   - console.firebase.google.com → yeni proje.
   - Authentication → Sign-in method → **Google**'ı aç.
   - Authentication → Settings → **Authorized domains** → `KULLANICIADI.github.io` ekle.
   - Firestore Database → Create database (production mode, `eur3`).
   - Firestore → **Rules** → `firestore.rules` dosyasının içeriğini yapıştır → Publish.
   - Proje ayarları → Your apps → Web uygulaması ekle → `firebaseConfig` değerlerini `firebase-config.js` dosyasına yaz.
2. **GitHub Pages**
   - Depoyu push et → Settings → Pages → Source: *Deploy from a branch*, Branch: `main` / `(root)`.
   - Site birkaç dakika içinde `https://KULLANICIADI.github.io/DEPOADI/` adresinde açılır.

Yerelde denemek için: `python -m http.server` → http://localhost:8000 (Firebase'de `localhost` varsayılan olarak yetkilidir).

## Yeni mekân eklemek

1. Blender betiği yaz (`scripts/build_espressolab.py` örnek). Her masa `Masa_XX` adlı bir Empty, üzerinde `masa_id` özelliği; varsa üst kat `UstKat` adlı bir kök altında.
2. `E:\blender\blender.exe -b -P scripts/<betik>.py` → `.glb` çıktısını `assets/models/<id>.glb` olarak kopyala, bir küçük görseli `assets/thumbs/<id>.png` olarak koy.
3. `index.html` içindeki `VENUES` listesine bir kayıt ekle: `id`, `ad`, `baslik` (dev harfler), `alt`, `slogan`, `renk`, `kaide`, `masalar`.

## Veri yapısı (Firestore)

| Koleksiyon | Alanlar |
|---|---|
| `anilar` | `mekan`, `masa`, `tarih`, `kimler[uid]`, `kimlerAd[]`, `metin`, `fotolar[id]`, `yazarUid`, `yazarAd`, `yazarFoto`, `zaman` |
| `yorumlar` | `mekan`, `masa`, `metin`, `yazarUid`, `yazarAd`, `zaman` |
| `fotolar` | `data` (JPEG data URL, < ~900 KB), `yazarUid`, `zaman` |
| `kisiler/{uid}` | `ad`, `foto`, `son` — giriş yapan herkes kendini yazar |

Ücretsiz plan: 1 GB depolama (~3–4 bin fotoğraf), günde 50 bin okuma / 20 bin yazma.

## Siteyi yalnızca gruba kapatmak

`firestore.rules` içindeki `uye()` fonksiyonunda e-posta listesini doldurup yorum satırını aç, sonra Rules'u yeniden yayınla.
