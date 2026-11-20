# Müşterek Mekanlar — Proje Notu

Selim, Yafes, Serdar, Erden ve Bilal'in ortak mekânları. Her mekân, kaide üstünde duran izometrik bir 3D maket; maketteki her masaya dokununca o masada yaşanan anılar, fotoğraflar ve yorumlar açılır. Herkes kendi Google hesabıyla girer, eklediği her şey kendi adıyla görünür.

**Site:** https://ahmetbill.github.io/musterek-mekanlar/
**Depo:** https://github.com/ahmetbill/musterek-mekanlar
**Firebase projesi:** `musterek-mekanlar` (Spark, ücretsiz plan)

Mekânlarla resmi bir bağı yoktur; arkadaş grubunun kendi anı defteridir.

---

## Fikir

- Maket sitenin kahramanı: tam ekran, döndürülebilir, yakınlaştırılabilir.
- Yazı az, tipografi güçlü: mekânın adı dev harflerle maketin arkasından ve önünden geçer; her mekânın kendi rengi ve italik bir sloganı var.
- Anılar masaya bağlı: oturduğumuz masalarda iğne çıkar, anı sayısı arttıkça iğne kızarır ("bizim masa"), en son oturduğumuz masanın etrafında yeşil halka döner.
- Mekânlar arasında geçiş bir sergi gibi: eski maket iner, yenisi süzülür, harfler sırayla değişir.

## Mekânlar

| # | Mekân | Durum | Masa | Renk | Not |
|---|---|---|---|---|---|
| 01 | Espressolab Esentepe (Şişli, Topkapı Üni. yakını) | Yayında | 39 | Terakota | En karmaşık mekân: 2 kat, asma kat, atriyum, kapalı dış alan, teras |
| 02 | — | Sırada | | | |

### 01 · Espressolab Esentepe

Sokaktan içeri sıra:

1. **Şemsiyeli teras** — 4 masa (Teras 1–4)
2. **Üstü kapalı dış alan** — tavanı yüksek, çıtalı sandalyeler, 4 masa (Kapalı dış 1–4)
3. **Giriş** — bar sağda, üst kata çıkan merdiven hemen solda; 2 masa
4. **Orta salon** — oval ortak masa (tavanda oval ayna), solda turkuaz Eames masaları, sağda terakota duvar ve bank
5. **Atriyum ("LOVE salonu")** — iki kat yüksekliğinde; yuvarlak saksı adası ve kavisli bank, LOVE aynalı duvar, frizin altındaki masalar, asma katın altındaki masalar; en arkada manzaraya (bina, yokuş yol, yeşillik) açılan büyük boşluk
6. **Üst kat** — alçak tavanlı; merdivenden çıkınca sağda uzun çalışma masası ve ilerisinde birkaç masa, solda lavabolar, atriyuma bakan kenarda küçük masalar
7. **Asma kat** — üst katla arası kapalı; atriyumdan, manzara boşluğunun yanından başlayan dönen merdivenle çıkılır

Kaynaklar: Google Maps fotoğrafları (yalnızca referans, depoda yok) + Bilal'in çizimleri.

## Kararlar

| Konu | Karar | Neden |
|---|---|---|
| Barındırma | GitHub Pages | Site tamamen statik; Vercel gereksiz. |
| Veri | Firebase Firestore (Spark) | Ücretsiz, kartsız, projeler uykuya geçmez (Supabase ücretsizde 1 hafta sonra duruyor). |
| Fotoğraflar | Sıkıştırılmış JPEG, Firestore belgesinde | Firebase Storage kart istiyor. 1280 px ≈ 200–300 KB; 1 GB ≈ 3–4 bin fotoğraf. |
| Giriş | Google ile tek tık | İsim/fotoğraf eşlemesi otomatik; şifre gerekmiyor. |
| Yetki | Giriş yapan görür ve ekler; herkes yalnız kendi eklediğini siler | İstenirse `firestore.rules` içindeki e-posta listesiyle yalnız gruba kapatılabilir. |
| Maket üretimi | Blender + Python betiği | Tekrarlanabilir; düzeltmeler betikte yapılıp yeniden üretilir. |
| Özel alan adı | Şimdilik yok | Pages'te ücretsiz bağlanır, alan adının kendisi ücretli. |

## Yeni mekân ekleme akışı

1. **Referans topla:** Google Maps fotoğraflarının linkleri (bar, giriş, iç mekân, varsa üst kat ve dış alan) + kuşbakışı kaba bir kroki: dış sınır, kapı, bar, masalar (numaralı), merdiven, en çok oturduğumuz masa (yıldız).
2. **Modelle:** `scripts/` altına yeni bir Blender betiği (Esentepe betiği şablon). Kural: her masa `Masa_XX` adlı bir Empty ve üzerinde `masa_id`; üst kat varsa `UstKat` kökü altında.
3. **Gözden geçir:** render al, kroki üzerinden düzeltmeleri işle (Esentepe'de 6 tur sürdü).
4. **Ekle:** `.glb` → `assets/models/<id>.glb`, küçük görsel → `assets/thumbs/<id>.png`, `index.html` → `VENUES` listesine kayıt (ad, dev başlık, slogan, renkler, masalar).
5. **Yayınla:** commit + push; Pages birkaç dakikada günceller.

## Yapılacaklar

- [ ] Firebase kurulumunu bitir: Google girişi, Authorized domains (`ahmetbill.github.io`), Firestore, kurallar
- [ ] İlk anıyı ekleyip uçtan uca dene (giriş → anı → fotoğraf → yorum → silme)
- [ ] Arkadaşlara linki gönder, herkes bir kere giriş yapsın ("Kimler vardı" listesi dolsun)
- [ ] 02 numaralı mekân
- [ ] İsteğe bağlı: siteyi e-posta listesiyle yalnız gruba kapat
- [ ] İsteğe bağlı: özel alan adı
- [ ] İsteğe bağlı: maketlerde küçük karakterler (biz), gece/gündüz ışığı
