# OpenMontage Teknik Degerlendirme Raporu
# Suvesu & Buzsu Turkce Video Uretim Sistemi

**Tarih:** 2026-06-21
**Durum:** Analiz & Planlama (kod degisikligi yok)
**Hedef:** OpenMontage tabanli, Suvesu ve Buzsu icin Turkce kisa video uretim sistemi kurmak

---

## A. Repository Yapisi

### A.1 Genel Mimari

OpenMontage agent-first (ajan-oncelikli) bir mimari kullaniyor.
Python yalnizca araclar icin kullanilir.
Orkestrasyon, yaratici kararlar ve kalite kontrol tamamen AI ajani tarafindan yurutulur.

```
Ajan -> Pipeline Manifest (YAML) -> Stage Director Skill (MD)
     -> Python Tools (BaseTool) -> Checkpoint (JSON) -> Insan Onayi
```

### A.2 Ana Bilesenler

| Katman               | Konum                    | Islev                                    |
|----------------------|--------------------------|------------------------------------------|
| Pipeline Tanimlari   | pipeline_defs/*.yaml     | 13 video uretim is akisi                 |
| Araclar              | tools/ (57+ Python tool) | Video, ses, grafik, analiz, altyazi      |
| Beceriler            | skills/ (80+ markdown)   | Ajan talimatlari, yonetmen becerileri     |
| Semalar              | schemas/ (20 JSON schema)| Artifact dogrulama                        |
| Stiller              | styles/*.yaml            | Marka kimligi playbook'lari              |
| Kompozisyon          | remotion-composer/       | React/Remotion video render motoru       |
| Altyapi              | lib/                     | Config, checkpoint, pipeline loader      |

### A.3 Pipeline Sistemi

13 pipeline mevcut. Suvesu/Buzsu icin en uygun olanlar:

| Pipeline             | Uygunluk  | Neden                                              |
|----------------------|-----------|----------------------------------------------------|
| animated-explainer   | 5/5       | TDS, su sertligi, filtre degisim aciklayici videolar|
| cinematic            | 4/5       | Marka filmi, urun tanitim trailerlari              |
| documentary-montage  | 4/5       | Sehir suyu belgeselleri, stok goruntularle          |
| avatar-spokesperson  | 3/5       | Avatar ile urun sunumu                              |
| localization-dub     | 3/5       | Mevcut Ingilizce icerigi Turkcelestirme            |
| clip-factory         | 3/5       | Uzun videodan kisa sosyal medya klipleri            |

Her pipeline 7 asamali bir state machine:
idea -> script -> scene_plan -> assets -> edit -> compose -> publish

### A.4 TTS (Seslendirme) Sistemi

| Provider      | Turkce | Ucretsiz             | Kalite              | Maliyet              |
|---------------|--------|----------------------|---------------------|----------------------|
| Google TTS    | EVET   | 1M karakter/ay       | Mukemmel (Chirp 3)  | $0-$30/1M karakter   |
| ElevenLabs    | EVET   | 10K karakter/ay      | Mukemmel             | ~$0.30/1K karakter   |
| OpenAI TTS    | HAYIR  | Yok                  | Iyi                 | $15/1M karakter      |
| Piper TTS     | HAYIR  | Sinirsiz ucretsiz    | Orta                | $0                   |
| Doubao        | HAYIR  | Yok                  | Mukemmel (Cince)    | $0.015/karakter      |

Kritik bulgu: Turkce TTS icin yalnizca Google TTS ve ElevenLabs destekli.
Piper Turkce desteklemiyor.
Oneri: Google TTS Chirp 3 HD (tr-TR dil kodu) - aylik 1M karakter ucretsiz.

### A.5 Video Render Sistemi

Uc render motoru mevcut:

| Motor        | Kullanim                                    | Guc                                  |
|--------------|---------------------------------------------|---------------------------------------|
| Remotion     | Animasyonlu aciklayicilar, veri gorsellestirme| 23 React bileseni, spring animasyonlar|
| HyperFrames  | Kinetik tipografi, urun tanitim             | HTML/CSS/GSAP, Node.js >= 22         |
| FFmpeg       | Basit kesme/birlestirme                     | Video concat, trim, speed            |

Platform profilleri hazir:

| Profil            | Cozunurluk  | En/Boy | Maks Sure |
|-------------------|-------------|--------|-----------|
| youtube_shorts    | 1080x1920   | 9:16   | 60s       |
| instagram_reels   | 1080x1920   | 9:16   | 90s       |
| tiktok            | 1080x1920   | 9:16   | 600s      |
| youtube_landscape | 1920x1080   | 16:9   | -         |
| instagram_feed    | 1080x1080   | 1:1    | 60s       |

### A.6 Asset Yonetimi

- Asset Manifest: Her uretilen dosya JSON artifact olarak izlenir
- Checkpoint sistemi: Her asamada durum kaydedilir, kaldigi yerden devam
- Cost tracker: Butce takibi - tahmin -> rezerv -> mutabakat
- Schema dogrulama: 20 JSON schema ile artifact kalite kontrolu

Stok kaynaklar (ucretsiz):

| Kaynak       | Tur              | Ucretsiz | Turkce Icerik             |
|--------------|------------------|----------|---------------------------|
| Pexels       | Gorsel + Video   | EVET     | Evet (Turkiye sehirleri)  |
| Pixabay      | Gorsel + Video   | EVET     | Sinirli                   |
| Unsplash     | Gorsel           | EVET     | Evet                      |
| Coverr/MixKit| Video            | EVET     | Su/doga klipleri mevcut   |
| NASA/NOAA    | Video            | EVET     | Su dongusu, okyanus       |

---

## B. Suvesu Icin Kullanim Senaryolari

### B.1 Sehir Videolari
Ornek: "Istanbul'un su kalitesi neden farkli?"

- Pipeline: animated-explainer veya documentary-montage
- Stiller: Sehir fotograflari (Pexels: Istanbul water, Ankara cityscape)
- TTS: Google TTS tr-TR-Chirp3-HD - profesyonel anlatici
- Sure: 45-60 saniye (YouTube Shorts / Instagram Reels)
- Icerik: TDS degerleri, su sertligi karsilastirmasi, bolgesel farkliliklar
- Gorsel: StatCard, BarChart (sehirler arasi TDS), harita animasyonlari

### B.2 TDS Videolari
Ornek: "TDS nedir? 500 ppm ne anlama gelir?"

- Pipeline: animated-explainer
- Bilesenler: ProgressBar (TDS olcegi), StatCard (ppm degerleri), TextCard
- Stil: clean-professional playbook tabanli Suvesu marka playbook'u
- Remotion Scenes: StatReveal, BarChart, ComparisonCard
- Sure: 30-45 saniye

### B.3 Su Sertligi Videolari
Ornek: "Sert su muslugunuza ne yapiyor?"

- Pipeline: animated-explainer veya cinematic
- Gorsel: Before/after ComparisonCard, kirec birikimi gorselleri
- Veri: KPIGrid (sertlik dereceleri), PieChart (mineral dagilimi)
- Stok: Pexels - limescale, hard water, faucet
- CTA: Suvesu urun onerisi

### B.4 Filtre Degisim Videolari
Ornek: "Filtrenizi ne zaman degistirmelisiniz?"

- Pipeline: animated-explainer
- Bilesenler: ProgressBar (filtre omru), timeline animasyonu
- Gorsel: Urun fotograflari (ProductReveal), step-by-step talimatlar
- Sure: 30-45 saniye
- Ton: Egitici, pratik bilgi

### B.5 Urun Tanitim Videolari
Ornek: "Suvesu 5 Asamali Aritma Sistemi"

- Pipeline: cinematic veya avatar-spokesperson
- Bilesenler: ProductReveal, HeroTitle, feature highlights
- HyperFrames: Urun promosyon animasyonlari, kinetik tipografi
- Muzik: Pixabay Music (ucretsiz, royalty-free)
- Sure: 45-90 saniye

---

## C. Gereksinimler

### C.1 Yazilim Gereksinimleri

| Gereksinim | Minimum              | Mevcut Durum | Durum    |
|------------|----------------------|--------------|----------|
| Python     | >= 3.10              | 3.11.15      | HAZIR    |
| Node.js    | >= 18 (Remotion)     | 22.22.2      | HAZIR    |
| FFmpeg     | Gerekli              | Kurulu degil | KURULMALI|
| npm        | Gerekli              | Node ile gelir| HAZIR   |
| Git        | Gerekli              | Mevcut       | HAZIR    |

### C.2 Python Paketleri

Cekirdek (requirements.txt):
- pyyaml>=6.0
- pydantic>=2.0
- jsonschema>=4.20
- python-dotenv>=1.0
- Pillow>=10.0
- requests>=2.31

GPU (opsiyonel - requirements-gpu.txt):
- torch>=2.0
- torchaudio>=2.0
- torchvision>=0.15

### C.3 Donanim Gereksinimleri

| Kaynak | Minimum (API Only) | Onerilen (Hibrit) | Tam Yerel   |
|--------|--------------------|--------------------|-------------|
| RAM    | 2 GB               | 8 GB               | 16+ GB      |
| Disk   | 2 GB               | 10 GB              | 50+ GB      |
| CPU    | 2 cekirdek          | 4 cekirdek          | 8+ cekirdek |
| GPU    | Gerekli degil       | Opsiyonel           | NVIDIA 8GB+ |
| Ag     | Gerekli (API)       | Gerekli             | Opsiyonel   |

### C.4 Remotion Paketleri

- remotion@4.0.441
- @remotion/cli
- @remotion/captions
- @remotion/google-fonts
- @remotion/media
- @remotion/player
- @remotion/transitions
- react@18.2
- react-dom@18.2
- typescript@5.3

---

## D. Minimum Ucretsiz Kurulum

### D.1 Sifir Maliyet Yapilandirmasi

| Bilesen          | Ucretsiz Cozum                     | Sinirlama                   |
|------------------|-------------------------------------|-----------------------------|
| TTS (Turkce)     | Google TTS (1M karakter/ay ucretsiz)| API key gerekli (ucretsiz)  |
| Stok Gorsel      | Pexels + Pixabay                    | API key gerekli (ucretsiz)  |
| Stok Video       | Pexels Video + Pixabay Video        | API key gerekli (ucretsiz)  |
| Muzik            | Pixabay Music (scraping)            | API key gerekmez            |
| Render           | Remotion + FFmpeg                   | Ucretsiz, acik kaynak       |
| LLM              | Claude Code (zaten kullanimda)      | Session tabanli             |

### D.2 Ucretsiz API Key'ler (Tumu $0)

| Servis          | Kayit                       | Limit                        |
|-----------------|-----------------------------|------------------------------|
| Google Cloud TTS| console.cloud.google.com    | 1M karakter/ay/ses tipi      |
| Pexels          | pexels.com/api              | 200 istek/saat               |
| Pixabay         | pixabay.com/api/docs        | 100 istek/dakika             |
| Freesound       | freesound.org               | Sinirsiz (CC lisans)         |

### D.3 Piper TTS Durumu

Piper tamamen ucretsiz ve cevrimdisi calisir.
ANCAK Turkce desteklemiyor.
Ingilizce draft'lar icin kullanilabilir ama Turkce uretim icin Google TTS zorunlu.

---

## E. Onerilen Mimari

### E.1 Entegrasyon Karari

KARAR: Vendor Copy (Dogrudan Kopyalama)
OpenMontage icerigini dogrudan root'a kopyala.

| Secenek            | Puan | Neden                                                |
|--------------------|------|------------------------------------------------------|
| Vendor Copy        | 5/5  | Path'ler oldugu gibi calisir, tam kontrol, bos repo  |
| Fork               | 3/5  | Repo kimligi kaybolur, gereksiz bagimlilik            |
| Git Submodule      | 2/5  | CI/CD karmasikligi, nested git sorunlari              |
| Sifirdan Wrapper   | 1/5  | 57+ tool, 80+ skill yeniden yazmak anlamsiz           |

Teknik gerekceler:
1. Path bagimliligi: OpenMontage tum sistemi root-relative calisir.
   CLAUDE.md, config.yaml, .claude/skills/, tools/, skills/ hepsi root-relative.
   Alt klasore koymak yuzlerce path'i kirar.
2. Agent entegrasyonu: .claude/skills/ dizini Claude Code tarafindan root'ta aranir.
   Submodule veya alt klasor olarak bu calismaz.
3. Repo bos: video-factory-studio'da sadece README.md var. Cakisma riski sifir.
4. Genisletilebilirlik: OpenMontage zaten custom pipeline, playbook ve skill eklemeye
   tasarlanmis - YAML + Markdown ile, kod degistirmeden.

### E.2 Onerilen Klasor Yapisi

```
video-factory-studio/                        <- root (OpenMontage base)
|
|-- AGENT_GUIDE.md                           <- OpenMontage (mevcut)
|-- CLAUDE.md                                <- OpenMontage (mevcut)
|-- config.yaml                              <- Turkce/dikey video defaults
|-- Makefile                                 <- OpenMontage (mevcut)
|
|-- content/                                 <- YENI: Suvesu/Buzsu icerik havuzu
|   |-- cities/                              <- Sehir bazli veriler
|   |   |-- istanbul.yaml                    <- TDS, sertlik, su kalitesi verileri
|   |   |-- ankara.yaml
|   |   |-- izmir.yaml
|   |-- products/                            <- Urun bilgileri
|   |   |-- suvesu-5-stage.yaml
|   |   |-- buzsu-premium.yaml
|   |-- scripts/                             <- Hazir script sablonlari
|       |-- tds-explainer.yaml
|       |-- filter-change-guide.yaml
|       |-- city-water-quality.yaml
|
|-- styles/                                  <- OpenMontage (mevcut) + ozel playbook'lar
|   |-- clean-professional.yaml              <- mevcut
|   |-- flat-motion-graphics.yaml            <- mevcut
|   |-- suvesu-brand.yaml                    <- YENI: Suvesu marka kimligi
|   |-- buzsu-brand.yaml                     <- YENI: Buzsu marka kimligi
|
|-- pipeline_defs/                           <- OpenMontage (mevcut) + ozel pipeline'lar
|   |-- animated-explainer.yaml              <- mevcut
|   |-- cinematic.yaml                       <- mevcut
|   |-- turkish-short-video.yaml             <- YENI: Turkce kisa video pipeline
|
|-- skills/                                  <- OpenMontage (mevcut) + ozel beceriler
|   |-- pipelines/
|   |   |-- explainer/                       <- mevcut
|   |   |-- turkish-short-video/             <- YENI: 7 stage director
|   |       |-- executive-producer.md
|   |       |-- idea-director.md
|   |       |-- script-director.md
|   |       |-- scene-director.md
|   |       |-- asset-director.md
|   |       |-- edit-director.md
|   |       |-- compose-director.md
|   |       |-- publish-director.md
|   |-- creative/
|       |-- turkish-content-guide.md         <- YENI: Turkce icerik rehberi
|
|-- tools/                                   <- OpenMontage (mevcut, degistirilmez)
|-- remotion-composer/                       <- OpenMontage (mevcut)
|-- schemas/                                 <- OpenMontage (mevcut)
|-- lib/                                     <- OpenMontage (mevcut)
|-- tests/                                   <- OpenMontage (mevcut)
|
|-- output/                                  <- Render ciktilari (gitignore)
|-- assets/                                  <- Uretilen asset'ler (gitignore)
|   |-- images/
|   |-- audio/
|   |-- video/
|
|-- .env                                     <- API key'ler (gitignore)
```

### E.3 Yeni Dosyalar (Olusturulacak)

| Dosya                                      | Amac                              | Oncelik |
|--------------------------------------------|-----------------------------------|---------|
| styles/suvesu-brand.yaml                   | Suvesu renk paleti, font, ton     | P0      |
| styles/buzsu-brand.yaml                    | Buzsu marka kimligi               | P0      |
| pipeline_defs/turkish-short-video.yaml     | Turkce kisa video pipeline        | P0      |
| skills/pipelines/turkish-short-video/*.md  | 7-8 stage director skill          | P0      |
| skills/creative/turkish-content-guide.md   | Turkce icerik rehberi             | P1      |
| content/cities/*.yaml                      | Sehir bazli su verileri           | P1      |
| content/products/*.yaml                    | Urun bilgileri                    | P1      |
| content/scripts/*.yaml                     | Hazir script sablonlari           | P2      |

---

## F. Risk Analizi

| Risk                    | Seviye  | Detay                                                  | Azaltma                                          |
|-------------------------|---------|--------------------------------------------------------|--------------------------------------------------|
| AGPL v3 Lisans          | ORTA    | Ag uzerinden servis verilirse kaynak kod paylasimi zorunlu | Ic kullanim icin sorun yok                     |
| Turkce TTS Kalitesi     | ORTA    | Google TTS Chirp 3 HD Turkce sesi dogal ama Ingilizce kadar olgun degil | ElevenLabs multilingual_v2 alternatif     |
| API Limitleri           | DUSUK   | Google TTS: 1M karakter/ay; Pexels: 200 istek/saat    | Gunluk 2-3 video ile limit asilmaz               |
| Stok Gorsel Tekrari     | ORTA    | Ayni aramalarla benzer gorseller gelir                 | Ozel prompt prefix, FLUX ile AI gorsel uretimi   |
| Render Performansi      | DUSUK   | 30s video icin 2-5 dakika render suresi                | Kabul edilebilir, paralel render mumkun           |
| FFmpeg Eksikligi        | KRITIK  | Bu ortamda FFmpeg kurulu degil                         | apt install ffmpeg ile kurulum gerekli            |
| Bakim Maliyeti          | ORTA    | Upstream guncellemeler manuel takip gerekir             | Ayda 1 kez upstream kontrol                      |
| Telif Riskleri          | DUSUK   | Pexels/Pixabay royalty-free, atif gerekmez             | Lisans kosullarina uyum                          |
| Turkce Karakter Destegi | DUSUK   | g, s, c, i, o, u karakter destegi                      | Python 3 + UTF-8 dogal destek                    |

---

## G. Kurulum Plani

| Faz   | Adim               | Detay                                              | Bagimlilik |
|-------|---------------------|----------------------------------------------------|------------|
| Faz 0 | Temel kurulum       | OpenMontage icerigini root'a kopyala, .gitignore   | -          |
| Faz 1 | Altyapi             | FFmpeg kur, make setup calistir, Python deps kur   | Faz 0      |
| Faz 2 | Marka Kimlikleri    | suvesu-brand.yaml ve buzsu-brand.yaml playbook     | Faz 0      |
| Faz 3 | Pipeline            | turkish-short-video.yaml + 7 stage director skill  | Faz 0      |
| Faz 4 | Icerik Havuzu       | content/cities/, content/products/, content/scripts/| Faz 2      |
| Faz 5 | API Entegrasyonu    | .env yapilandirmasi (Google TTS, Pexels, Pixabay)  | Faz 1      |
| Faz 6 | Ilk Video           | Test uretimi - "TDS Nedir?" aciklayici video       | Faz 1-5    |
| Faz 7 | Optimizasyon        | Kalite ayarlari, ses tonu, gorsel tutarlilik       | Faz 6      |

---

## H. Sonraki Adimlar

Onay uzerine yapilacak isler (sirasiyla):

1. OpenMontage icerigini root'a kopyala (temp-openmontage/* -> root)
2. .gitignore guncelle (output/, pipeline/, node_modules/, assets/ ekle)
3. config.yaml duzenle (Dikey video 1080x1920 varsayilan, Turkce TTS)
4. styles/suvesu-brand.yaml olustur (Marka renkleri, fontlar, ton bilgisi gerekli)
5. styles/buzsu-brand.yaml olustur
6. pipeline_defs/turkish-short-video.yaml olustur (Kisa video pipeline)
7. Ilk commit ve push

---

Rapor tamamlandi. Kod degisikligi yapilmadi. Deploy yapilmadi. API key istenmedi.
