# Hazirlik Raporu: Suvesu & Buzsu Turkce Video Uretim Sistemi
# Faz 0 Oncesi Detayli Analiz

**Tarih:** 2026-06-21
**Durum:** Hazirlik tamamlandi, kod degisikligi yok
**Sonraki adim:** Bilgisayara geciste Faz 0 ve Faz 1 baslatilacak

---

## BOLUM 1: OpenMontage Mimari Detay Analizi

### 1.1 Routing ve Giris Noktalari

AGENT_GUIDE.md (38KB) tum sistemi yonetiyor:

- Belirsiz istek ("video yap"): Once skills/meta/onboarding.md oku
- Referans video verildiyse: skills/meta/video-reference-analyst.md oku
- Kural Sifir: TUM uretim pipeline uzerinden gider. Ad-hoc script yok

Routing sirasi:
1. Kullanici mesajini siniflandir
2. Pipeline sec
3. Preflight calistir (provider_menu_summary)
4. Pipeline manifest'i (YAML) oku
5. Stage director skill'i (MD) oku
6. Araclari calistir
7. Checkpoint yaz
8. Insan onayina sun

### 1.2 Executive Producer Orkestrasyon Modeli

EP cumulative state tutar - her asamada guncellenir:

```
EP_STATE:
  pipeline: animated-explainer
  playbook: suvesu-brand
  target_duration_seconds: 60
  budget_total_usd: 2.00
  budget_spent_usd: 0.0
  budget_remaining_usd: 2.00
  narration_durations: {section_id -> actual_seconds}
  revision_counts: {stage_name -> count}
  style_anchors: {}
```

Her asama icin dongu:
1. PREPARE: Director skill yukle, EP_STATE enjekte et
2. SPAWN: Director calistir, artifact uret
3. REVIEW: Schema dogrulama + review_focus + success_criteria kontrol
4. GATE: PASS / REVISE (max 3) / SEND_BACK (onceki asamaya)

### 1.3 Provider Skorlama Motoru (lib/scoring.py)

Naive "ilk bulunan" degil, cok boyutlu skorlama:

```
weighted_score =
  task_fit      * 0.30   (brief intent/stil eslesme)
  output_quality * 0.20   (stabilite + tier + kalite)
  control       * 0.15   (controlnet, seed, reference)
  reliability   * 0.15   (availability + basari orani)
  cost_efficiency * 0.10  (maliyet vs kalan butce)
  latency       * 0.05   (olculmus p50 veya runtime sinifi)
  continuity    * 0.05   (kilitli provider'larla uyum)
```

Turkce icin: Turkish synonym cluster eklenmeli
("sinematik" <-> "film" <-> "video")

### 1.4 Checkpoint Protokolu

Her stage sonrasi checkpoint yazilir:

```
checkpoint_required | human_approval | Aksiyon
true               | true           | Checkpoint + insana sor
true               | false          | Checkpoint + devam et
false              | *              | Atlama (nadir)
```

Resume: Pipeline crash olursa stage 6'dan devam, stage 1'den degil.

### 1.5 Reviewer Protokolu

CHAI kurallari:
- Her bulgu somut artifact alani/satir/frame referans etmeli
- Kritik bulgular proposed_fix icermeli
- Severity: critical | suggestion | nitpick | investigation

Karar:
- 0 critical -> PASS
- 1+ critical -> REVISE (max 2 tur)
- 2 turdan sonra hala critical -> PASS_WITH_WARNINGS (asla sonsuza bloklamaz)

### 1.6 Maliyet Yonetisimi

CostTracker akisi:
1. estimate(tool, operation, estimated_usd) -> entry_id
2. reserve(entry_id) -> butce asarsa hata
3. [araci calistir]
4. reconcile(entry_id, actual_usd, success)

Modlar:
- OBSERVE: Logla, bloklamaz
- WARN: Logla, uyar, devam et
- CAP: Logla, esik asarsa BLOKLA

### 1.7 Tool Registry Otomatik Kesfi

```python
# tools/ altindaki tum BaseTool alt siniflarini otomatik bulur
registry.discover()

# Yeni Turkce TTS eklemek icin:
# 1. tools/audio/turkish_tts.py olustur
# 2. class TurkishTTS(BaseTool) yaz
# 3. capability = "tts", provider = "provider_name" ayarla
# 4. execute() implement et
# 5. Otomatik kesfedilir, tts_selector yonlendirir
```

### 1.8 Runtime Secim Zorunlulugu

Kritik kural: Hem Remotion hem HyperFrames mevcutsa
IKISINI DE kullaniciya sunmak ZORUNLU:
- Remotion icin tek satirlik uygunluk + tradeoff
- HyperFrames icin tek satirlik uygunluk + tradeoff
- Bir tanesi oneri olarak belirt
- Acik kullanici onayi bekle
- Tek runtime sunmak = KRITIK IHLAL

### 1.9 Turkce Pipeline Icin Gerekli Uzanti Noktalari

1. Registry: Turkce TTS araclari ekle (capability: "tts")
2. Manifest: pipeline_defs/turkish-short-video.yaml olustur
3. Director Skills: skills/pipelines/turkish-short-video/ (7-8 dosya)
4. Layer 3 Skills: .agents/skills/turkish-tts/, turkish-cultural-sensitivity/
5. Scoring: Turkce synonym cluster ekle
6. Playbooks: styles/suvesu-brand.yaml, buzsu-brand.yaml
7. Artifacts: source_language: "tr" metadata alani ekle

---

## BOLUM 2: Turkce TTS Karsilastirmasi

### 2.1 Provider Matrisi

| Provider | Model | Turkce | Kalite | TR Ses Sayisi | Maliyet/1M kar | Gecikme | SSML | Duygu Kontrolu |
|----------|-------|--------|--------|---------------|----------------|---------|------|-----------------|
| ElevenLabs | Multilingual v2 | EVET | EN YUKSEK | 15+ | $100 (API) | Standart | Sinirli | Stability, Style |
| ElevenLabs | Flash v2.5 | EVET | Cok Iyi | 15+ | $50-100 | DUSUK ~75ms | Evet | Ayni | 
| Google Cloud | Chirp 3 HD | EVET | Mukemmel | 8 (4E/4K) | $30 | Standart | Evet | Pitch, Rate |
| Google Cloud | Neural2 | EVET | Cok Iyi | 8 | $16 | Standart | Evet | Pitch, Rate |
| Azure | Neural HD | EVET | Cok Iyi | 2 (Ahmet, Emel) | $22 | Standart | Evet | Sinirli |
| Piper | ONNX (yerel) | EVET | Iyi | 3 | UCRETSIZ | Anlik | Yok | Yok |
| OpenAI TTS | gpt-4o-mini-tts | HAYIR | Iyi | 6 | $15 | Standart | Yok | Sinirli |
| Doubao | seed-tts-2.0 | HAYIR | Mukemmel | 10+ (Cince) | $15 | 8s p50 | Yok | Yok |

### 2.2 Turkce Ses Onerileri

ElevenLabs Turkce sesler:
- Enes: Guvenen, kendinden emin (kurumsal sozcuk)
- Defne: Sicak, davetkar (musteri odakli)
- Selim: Samimi, enerjik (yaklasilabilir marka sesi)
- Bilgehan: Orta yasli, otoriter (premium konumlandirma)

Google Cloud tr-TR sesleri:
- 4 erkek + 4 kadin ses (Chirp 3 HD tier)
- language_code: "tr-TR"
- v1beta1 endpoint (Chirp 3 HD icin otomatik)

Piper Turkce sesler:
- dfki, fahrettin, fettah (3 ses)
- Tamamen ucretsiz ve cevrimdisi
- Draft/test icin uygun, premium marka isi icin yetersiz

### 2.3 5 Dakikalik Video Basina Maliyet

3,750 karakter (750 kelime x 5 karakter) varsayimiyla:

| Provider | Video Basina Maliyet |
|----------|---------------------|
| Piper | UCRETSIZ |
| Google Neural2 | $0.00006 |
| Google Chirp 3 HD | $0.00011 |
| Azure Neural HD | $0.00008 |
| ElevenLabs v2 | $0.00038 |

Pratik sonuc: TTS maliyeti ihmal edilebilir duzeyde.

### 2.4 Turkce Telaffuz Ozel Konulari

1. Yumusak g (g): ElevenLabs dogal isler; Piper'da sorun rapor edilmis
2. Unlu uyumu: ElevenLabs Multilingual v2 en iyi destek
3. Ek degisimi (Turkce agglutination): ElevenLabs ve Google iyi isler
4. Turkce metin Ingilizce'den ~%25-30 daha uzun: Text card hold surelerini 0.3-0.5s uzat

### 2.5 Oneri

- Birincil: ElevenLabs Multilingual v2 (Creator plan $22/ay)
- Ikincil: Google Cloud Chirp 3 HD (kullanima gore, $30/1M)
- Yedek: Piper (cevrimdisi test/draft icin)
- Gelecek: Azure TTS tool eklenebilir (tools/audio/azure_tts.py)

---

## BOLUM 3: Suvesu Marka Playbook Tasarimi

### 3.1 Arastirma Bulgulari

- Buzsu: 12+ yil ticari, 7+ yil sektorde, bilimsel guvenilirlik vurgusu
- Paslanmaz celik tank, Amerikan Filmtec filtre, guven odakli
- Turkce su aritma pazari: ergonomik tasarim, bilimsel guvenilirlik, cevre sorumlulugu
- Rakipler (AquaTurk, Rainwater, Puretech): temizlik, safilik, teknoloji, surdurulebilirlik

### 3.2 Suvesu Playbook: "Bilimsel Guven & Saf Teknoloji"

```yaml
identity:
  name: "Suvesu - Bilimsel Guven & Saf Teknoloji"
  category: motion-graphics
  mood: trustworthy, scientific, clean, progressive, professional
  pace: moderate
  best_for: "Urun demolari, su safligi egitim videolari, saglik icerikleri, kurumsal videolar"

visual_language:
  color_palette:
    primary: ["#0066CC", "#0052A3"]        # Profesyonel su mavisi (guven + bilim)
    accent: ["#00A651", "#1AC74C"]         # Taze yesil (safilik, doga, saglik)
    background: "#FFFFFF"                   # Temiz beyaz (safilik)
    text: "#1A1A2E"                        # Derin lacivert (okunabilirlik)
    muted: "#7A8A99"                       # Serin gri
    water_highlight: "#E8F5FF"             # Yumusak mavi ton

typography:
  headings:
    font: "Noto Sans"                      # Tam Turkce karakter destegi
    weight: 700
    tracking: "-0.01em"
  body:
    font: "Noto Sans"
    weight: 400
    line_height: 1.6
  stat_card:
    font: "Noto Sans"
    weight: 800
    size_multiplier: 3.2
  scale_system: "major_third"

motion:
  transitions: [fade, dissolve, slide-left, cross-fade]
  animation_style: "ease-in-out, precise, scientific, no bounce"
  pacing_rules:
    min_scene_hold_seconds: 2.8
    max_scene_hold_seconds: 10
    text_card_hold_seconds: 3.5
    stat_card_hold_seconds: 3.2
    transition_duration_seconds: 0.45
  entrance: "fade-up with precise scale (0.98 -> 1.0)"

audio:
  voice_style: "profesyonel, olculu, sicak ama otoriter Turkce anlatici"
  music_mood: "modern kurumsal ambient, minimalist elektronik"
  music_volume: 0.10
  sfx_style: "hafif su sesleri (damlalar, akan su), veri gosterimlerinde bip sesleri"

asset_generation:
  image_prompt_prefix: "clean professional scientific illustration, Turkish water purification, white background, blue and green color scheme, "
  image_negative_prompt: "photorealistic, 3d render, dark, grungy, cluttered, low quality"
  consistency_anchors:
    - "Mavi (#0066CC) tum illustrasyon ve teknik diyagramlarda birincil vurgu"
    - "Yesil (#00A651) saglik sonuclari ve safilik onaylari icin"
    - "Beyaz/acik mavi arka planlar bilimsel netlik icin"
    - "Su molekulleri, damlalar ve akis desenleri tekrarlayan gorsel motif"

overlays:
  stat_card:
    bg: "#F0F7FF"
    border: "#0066CC"
    radius: 8
  key_term:
    bg: "#E8F5FF"
    text: "#0052A3"

quality_rules:
  - "Minimum kontrast orani 4.5:1 (WCAG AA)"
  - "Ekranda ayni anda en fazla 3 vurgu rengi"
  - "720p mobilde okunabilir yazi"
  - "Turkce karakterler (c, s, g, i, o, u) tum fontlarda dogru render"
  - "Saglik iddialari gorsel kaynak veya sertifika rozeti icermeli"

chart_palette: ["#0066CC", "#00A651", "#FF6B35", "#FFB81C", "#6B5CE6", "#00BCD4"]

color_rules:
  harmony_type: "analogous"
  contrast_validation: true
  colorblind_safe: true
```

### 3.3 Buzsu Playbook: "Ileri Teknoloji & Surdurulebilirlik"

```yaml
identity:
  name: "Buzsu - Ileri Teknoloji & Surdurulebilirlik"
  category: motion-graphics
  mood: innovative, engineering-forward, environmentally conscious, premium
  pace: moderate-fast
  best_for: "Teknik ozellik videolari, marka miras hikayeleri, surdurulebilirlik etki videolari"

visual_language:
  color_palette:
    primary: ["#1C3A70", "#003D82"]        # Derin teknik mavi (muhendislik, hassasiyet)
    accent: ["#00A86B", "#2ECC71"]         # Canli surdurulebilirlik yesili
    background: "#F5F7FA"                   # Hafif serin beyaz (premium, teknoloji)
    text: "#0F1419"                        # Neredeyse siyah (maksimum okunabilirlik)
    tech_teal: "#00BCD4"                   # Parlak teal (ileri teknoloji)
    highlight_gold: "#D4AF37"              # Hafif altin (premium konumlandirma)

typography:
  headings:
    font: "Noto Sans"
    weight: 800
    tracking: "-0.02em"
  body:
    font: "Noto Sans"
    weight: 400
  scale_system: "perfect_fourth"

motion:
  transitions: [wipe-up, zoom-in, fade, cross-fade]
  animation_style: "ease-out, precise mechanical motion, engineering aesthetic"
  pacing_rules:
    min_scene_hold_seconds: 2.5
    max_scene_hold_seconds: 9
    text_card_hold_seconds: 3.2
    stat_card_hold_seconds: 3.0
    transition_duration_seconds: 0.5

audio:
  voice_style: "net, guvenen, biraz hizli tempo, muhendislik mukemmelligi vurgusu"
  music_mood: "modern tech ambient, minimal elektronik, hafif futuristik synth"
  music_volume: 0.11
  sfx_style: "mekanik hassasiyet sesleri, filtreden gecen su sesi, teknoloji cimlari"

asset_generation:
  image_prompt_prefix: "advanced engineering illustration, Turkish water filtration technology, premium styling, deep blue and green, Filmtec membrane filter diagrams, "
  consistency_anchors:
    - "Derin mavi (#1C3A70) teknik hassasiyet icin birincil vurgu"
    - "Canli yesil (#00A86B) cevreci etki ve surdurulebilirlik icin"
    - "Teal (#00BCD4) ileri teknoloji vurgulari icin"
    - "Filmtec filtre performansi, TDS azaltma, atiksu tasarrufu gorselleri"

quality_rules:
  - "Minimum kontrast orani 7:1 (WCAG AAA premium konumlandirma)"
  - "Muhendislik spesifikasyonlari gorsel hassasiyetle gosterilmeli"
  - "Anti-bakteriyel paslanmaz celik tank yapisi gorsel olarak vurgulanmali"
  - "Oduller, sertifikalar ve uluslararasi standartlar acikca gorunmeli"

chart_palette: ["#1C3A70", "#00A86B", "#00BCD4", "#FFB81C", "#FF6B35", "#D4AF37"]

color_rules:
  harmony_type: "complementary"
  contrast_validation: true
  colorblind_safe: true
```

### 3.4 Tasarim Kararlari Gerekceleri

1. Font: Noto Sans - tam Turkce karakter destegi (c, s, g, noktasiz i, o, u)
2. Suvesu mavisi (#0066CC): Guven, bilim - saglik/su urunleri icin kritik
3. Yesil (#00A651): Saglik, doga, cevre sorumlulugu - Turkiye'de guclu pozitif cagrisim
4. Beyaz arka plan: Safilik, temizlik - su sektoru icin zorunlu
5. Suvesu tempo: Olculu (2.8-10s) egitici, guvenir konumlandirma
6. Buzsu tempo: Biraz hizli (2.5-9s) premium teknik konumlandirma
7. Turkce metin %25-30 daha uzun: Text card hold sureleri uzatildi

---

## BOLUM 4: Water Intelligence Veri Cekme Stratejisi

### 4.1 Veri Kaynak Envanteri

Tier 1 - Resmi Su Idareleri (En Guvenilir):

| Sehir | Idare | Web | Veri Durumu |
|-------|-------|-----|-------------|
| Istanbul | ISKI | iski.istanbul | Gunluk kalite raporlari, lab hizmetleri |
| Ankara | ASKI | aski.gov.tr | Gunluk analiz sonuclari, aylik TS 266 PDF |
| Izmir | IZSU | izsu.gov.tr | Lab hizmetleri raporlari |
| Bursa | BUSKI | buski.gov.tr | Baraj verileri, kalite raporlari |
| Antalya | ASAT | asat.gov.tr | 240 gunluk test noktasi, 38 parametre |
| Kocaeli | ISU | isu.gov.tr | Analiz raporlari |

Tier 2 - Devlet Standartlari:
- TS 266 Standardi (TSE): AB Direktifi 98/83/EC'den uyarlama
  - pH: 6.5-9.2 (onerilen 6.5-8.5)
  - TDS: max 1500 mg/L
  - Serbest klor: max 0.5 mg/L (onerilen 0.1 mg/L)
  - Arsenik: max 10 ug/L

Tier 3 - Su Aritma Sektoru Verileri (En Zengin Sehir Verisi):
- ethicwater.com.tr: Turkiye icme suyu sertlik haritasi
- rainwater.com.tr: Su sertlik haritasi 2026 il il
- puretronwater.com: Sehir bazli TDS rehberleri

### 4.2 Sehir Su Kalitesi Verileri

| Sehir | Nufus | Idare | TDS (ppm) | Sertlik (mg/L) | Sinif | Kaynaklar |
|-------|-------|-------|-----------|----------------|-------|-----------|
| Istanbul | 15.7M | ISKI | 150-300 | 120-180 | Orta Sert | Omerli, Terkos, Melen |
| Ankara | 5.9M | ASKI | 250-471 | 250-350+ | Cok Sert | Camlidere, Kurtbogazi |
| Izmir | 4.5M | IZSU | 150-250 | 150-200 | Orta | Tahtali, Gordes |
| Bursa | 3.3M | BUSKI | 250-400 | 250-350 | Sert/C.Sert | Doganci |
| Antalya | 2.8M | ASAT | 150-280 | 120-180 | Orta | Kirkgoz, Duden |
| Adana | 2.3M | ASKI | 350-650 | 320-625 | Cok Sert | Seyhan |
| Konya | 2.3M | KOSKI | 100-200 | 107-214 | Yumusak-Orta | Yeralti/kaynaklar |
| Gaziantep | 2.1M | GASKI | 150-250 | Orta | Orta | Yeralti/baraj |
| Kayseri | 1.4M | KASKI | Dusuk-Orta | Dusuk-Yumusak | Yumusak | Erciyes kaynaklari |
| Mersin | 1.9M | MESKI | Orta | Orta | Orta | Tarsus/baraj |

### 4.3 Oncelikli 10 Sehir Siralamasi

Nufus (pazar buyuklugu) x Su sorunlari (satis motivasyonu) x Veri erisilebilirligi:

| Sira | Sehir | Gerekce |
|------|-------|---------|
| 1 | Istanbul | En buyuk pazar (15.7M), orta sertlik, mukemmel ISKI verisi |
| 2 | Ankara | 2. en buyuk (5.9M), COK sert su (TDS 460+), 2026 su krizi |
| 3 | Adana | Turkiye'nin en yuksek TDS'i (350-650), guclu aci noktasi |
| 4 | Bursa | Sert su (250-350 mg/L), 3.3M nufus, kirec sikayetleri |
| 5 | Izmir | 3. en buyuk (4.5M), orta sertlik, iyi IZSU verisi |
| 6 | Antalya | 2.8M + turizm, karstik jeoloji, ASAT 240 nokta/gun test |
| 7 | Konya | 2.3M, karisik yumusak-orta, tarim bolgesi |
| 8 | Gaziantep | 2.1M, orta sertlik, GA pazari |
| 9 | Mersin | 1.9M, Akdeniz kiyisi, orta sertlik |
| 10 | Kayseri | 1.4M, yumusak su ama volkanik mineral icerigi |

### 4.4 Sehir Veri YAML Semasi

```yaml
# Schema: city-water-intelligence/v1
# Dosya konumu: content/cities/{sehir_slug}.yaml

city_name_tr: "Istanbul"
city_name_en: "Istanbul"
slug: "istanbul"
region: "marmara"    # marmara|ege|akdeniz|ic_anadolu|karadeniz|dogu|guneydogu
population: 15754053
population_source: "TUIK 2025"

water_utility:
  name: "ISKI"
  full_name: "Istanbul Su ve Kanalizasyon Idaresi"
  website: "https://iski.istanbul"
  report_url: "https://iski.istanbul/su-kalite-raporlari/"

sources:
  - name: "Omerli Baraji"
    type: "dam"          # dam|underground|spring|river|mixed
    capacity_hm3: 220
  - name: "Terkos Golu"
    type: "dam"
    capacity_hm3: 142
  - name: "Buyuk Melen"
    type: "river"
    capacity_hm3: 268

metrics:
  tds_ppm:
    value_min: 150
    value_max: 300
    value_typical: 200
    unit: "ppm"
    measurement_date: "2025-01"
    source: "puretronwater.com"
    confidence: "medium"    # high|medium|low|estimated

  hardness_mgl:
    value_min: 120
    value_max: 180
    value_typical: 150
    unit: "mg/L CaCO3"
    hardness_class: "orta_sert"  # yumusak|az_sert|orta_sert|sert|cok_sert

  ph:
    value_typical: 7.4
    unit: "pH"
    ts266_limit: "6.5-9.2"

  free_chlorine_mgl:
    value_typical: 0.3
    unit: "mg/L"
    ts266_limit_max: 0.5

problems:
  - id: "kireclenme"
    tr: "Kirec birikintisi"
    severity: "medium"     # low|medium|high|critical
    affected: ["kettle", "musluk", "dus", "bulasik_makinesi"]
  - id: "klor_tadi"
    tr: "Klor tadi ve kokusu"
    severity: "medium"
  - id: "eski_tesisat"
    tr: "Eski bina tesisati"
    severity: "high"

suvesu_solution:
  primary_product: "suvesu-pro"
  product_reason_tr: "Orta sert su icin ideal ters ozmoz aritma"
  recommended_filter_change_months: 6

video_hooks:
  headline_tr: "Istanbul'un suyu gercekten icilebilir mi?"
  facts:
    - tr: "Istanbul'un suyu 10 farkli baraj ve kaynak suyundan geliyor"
      visual_suggestion: "map_animation"
    - tr: "Omerli Baraji yilda 220 milyon m3 su sagliyor"
      visual_suggestion: "stat_counter"
    - tr: "TDS degeri ortalama 200 ppm - WHO idealinin ustunde"
      visual_suggestion: "gauge_meter"
  before_after:
    before_tds: 200
    after_tds: 15
    reduction_percent: 92.5

seo:
  title_tr: "Istanbul Su Kalitesi | TDS ve Sertlik | Suvesu"
  keywords_tr:
    - "Istanbul su kalitesi"
    - "Istanbul TDS degeri"
    - "Istanbul su sertligi"
    - "ISKI su analizi"

data_meta:
  last_updated: "2025-03-15"
  next_review: "2025-09-15"
  data_quality_score: 0.7
```

### 4.5 Veri Toplama Stratejisi

Faz 1 - Hemen (Manuel Tohumlama):
- Ethicwater, rainwater, puretronwater kaynaklarindan ilk 10 sehir verisini cikar
- ASKI aylik TS 266 PDF'lerini indir (Ankara icin yapilandirilmis tablo verisi)
- Tahmini efor: 2-3 gun, 10 sehir YAML dosyasi, orta guven verisi

Faz 2 - Yapilandirilmis Kazima:
- ASKI gunluk analiz sayfasi (en yapilandirilmis acik veri)
- Puretronwater sehir bazli TDS sayfalari
- Ethicwater ve rainwater sertlik haritalari

Faz 3 - Topluluk Zenginlestirme:
- Suvesu musterilerinden TDS olcum verisi toplama
- DonanımHaber forum verileriyle carpraz referans
- Guven skoru sistemi: resmi > ticari > topluluk

Faz 4 - Surdurulebilir Tazelik:
- Ceyrekllik gozden gecirme dongusu
- Su idaresi web sitelerini yeni rapor icin izleme

### 4.6 En Guclu Video Konulari (Sehir Bazli)

1. Ankara: Aktif su krizi (baraj %4.7), cok sert su (TDS 460+)
   Hook: "Ankara'nin suyu bitiyor - ve kalan su da sert"
2. Adana: Turkiye'nin en yuksek TDS'i (350-650 ppm)
   Hook: "Turkiye'nin en kirecli suyu Adana'da"
3. Bursa: Gorunur kirec sorunlari, yuksek sertlik
   Hook: "Kettle'inizdaki beyaz tabaka Bursa suyundan"
4. Istanbul: Devasa kitle, Melen boru hatti hikayesi
   Hook: "Suyunuz 130 km uzaktan geliyor - yolda ne oluyor?"
5. Antalya: Karstik jeoloji, turist vs yerel su kalitesi farki

---

## BOLUM 5: Ilk 20 Video Konusu

### Kategori A: Egitici (1-6)

**1. Musluk Suyu Gercekten Icilebilir mi?**
- Pipeline: explainer | Sure: 60s | Maliyet: $0.80 | Oncelik: P0
- Platform: Tumu (Shorts, Reels, TikTok)
- Hook: "Bu su temiz gorunuyor. Ama gercekten oyle mi?"
- Gorseller: Turkiye haritasi animasyonu, eski boru kesiti, TDS olcum
- CTA: "Evinizdeki suyun TDS degerini olctunuz mu? Yorumlara yazin!"

**2. TDS Nedir? 60 Saniyede Anlat**
- Pipeline: animation | Sure: 60s | Maliyet: $0.60 | Oncelik: P0
- Platform: Tumu
- Hook: TDS metre suya daldiriliyor, rakamlar hizla yukseliyor
- Gorseller: Animasyonlu gostergeler, karsilastirma cubuk grafikleri, WHO limiti
- CTA: "Suyunuzun TDS degerini ogrenin - bio'daki linke tiklayin"

**3. Su Sertligi Nedir? Kirecli Su Vucudunuza Ne Yapar?**
- Pipeline: explainer | Sure: 60s | Maliyet: $0.90 | Oncelik: P0
- Platform: Tumu
- Hook: Ceydanligin icindeki beyaz kirec close-up
- Gorseller: Molekul animasyonu, vucut silueti, Turkiye sertlik haritasi
- CTA: "Sehrinizin su sertligini bilmek ister misiniz? Yoruma sehrinizi yazin!"

**4. Ters Ozmoz Nedir? Su Aritma Nasil Calisir?**
- Pipeline: animation | Sure: 45s | Maliyet: $0.50 | Oncelik: P1
- Platform: Tumu
- Hook: Kirli su / temiz su arasinda membran duvari
- Gorseller: RO membran kesiti, 5 asamali filtre diyagrami, basinc gostergesi
- CTA: "Ters ozmozu anlamak bu kadar kolay. Kaydedin, lazim olacak!"

**5. Suda Gorunmeyen 5 Tehlike**
- Pipeline: cinematic | Sure: 60s | Maliyet: $1.20 | Oncelik: P1
- Platform: TikTok, Reels
- Hook: "Bu bir damla suda 50.000'den fazla mikro parcacik var."
- Gorseller: Mikroskop zoom, tehlike ikonlari, neon parcacik efektleri
- CTA: "Ailenizi koruyun. Ucretsiz su testi icin bio'daki linke tiklayin."

**6. Bebek Suyu Nasil Olmali? Ebeveyn Rehberi**
- Pipeline: explainer | Sure: 45s | Maliyet: $0.70 | Oncelik: P1
- Platform: Instagram Reels
- Hook: "Bebeginize verdiginiz su gercekten guvenli mi?"
- Gorseller: Pastel renkler, ideal mineral icerigi infografik, karsilastirma tablosu
- CTA: "Bebek icin ideal su rehberimizi indirin - link bio'da"

### Kategori B: Sehir Bazli (7-10)

**7. Istanbul'un Suyu Icilebilir mi? 2026 Gercekleri**
- Pipeline: documentary-montage | Sure: 60s | Maliyet: $1.50 | Oncelik: P0
- Platform: Tumu (Istanbul = en buyuk pazar)
- Hook: "16 milyon kisi her gun bu sehrin suyunu iciyor. Guvenli mi?"
- Gorseller: Istanbul siluetin, ISKI tesisi, mahalle bazli TDS haritasi
- CTA: "Istanbul'da yasiyorsaniz ucretsiz su analizi icin bize ulasin!"

**8. Ankara Suyu Neden Bu Kadar Sert?**
- Pipeline: explainer | Sure: 45s | Maliyet: $0.80 | Oncelik: P1
- Platform: Tumu
- Hook: Tireli musluk basligi close-up
- Gorseller: Jeolojik kesit, Ankara TDS karsilastirma, oncesi/sonrasi
- CTA: "Ankara'daki eviniz icin dogru aritma cihazini secmenize yardimci olalim"

**9. Antalya ve Izmir: Turkiye'nin En Kirecli Sulari**
- Pipeline: documentary-montage | Sure: 60s | Maliyet: $1.30 | Oncelik: P1
- Platform: Tumu
- Hook: Iki musluktanda kirec: "Ege ve Akdeniz'de su neden bu kadar farkli?"
- Gorseller: Split-screen iki sehir, karstik arazi, hasar galerisi
- CTA: "Sehrinize ozel su analizi icin ucretsiz randevu alin"

**10. Turkiye Su Sertligi Haritasi: Senin Sehrin Kacinci Sirada?**
- Pipeline: animation | Sure: 45s | Maliyet: $0.60 | Oncelik: P0
- Platform: TikTok, Reels (yuksek etkilesim - kisiler sehirlerini etiketler)
- Hook: "Turkiye'nin en kirecli sehri hangisi? Tahmin edin!"
- Gorseller: Interaktif Turkiye haritasi, sehir baloncuklari, siralama tablosu
- CTA: "Sehrinizi yorumlara yazin, biz de TDS degerini soyleyelim!"

### Kategori C: Urun (11-14)

**11. Damacana mi, Aritma Cihazi mi? Matematik Konusuyor**
- Pipeline: animation | Sure: 60s | Maliyet: $0.50 | Oncelik: P0
- Platform: Tumu
- Hook: Damacana yiginlari buyuyor: "Yilda damacana suya ne kadar harciyorsunuz?"
- Gorseller: Maliyet hesaplayici, 12 aylik kosu grafigi, basabasss noktasi
- CTA: "Hesaplamayi kendiniz yapin - ucretsiz karsilastirma araci bio'da"

**12. Su Aritma Cihazi Secerken 5 Kritik Hata**
- Pipeline: explainer | Sure: 60s | Maliyet: $0.70 | Oncelik: P0
- Platform: Tumu
- Hook: "Bu hatalar paranizi cop ediyor."
- Gorseller: Geri sayim, hata kartlari (kirmizi X), dogru yaklasim (yesil tik)
- CTA: "Dogru secim rehberi icin bio'daki linke tiklayin"

**13. Kutu Acilimi: Buzsu Aritma Cihazi Ilk Bakis**
- Pipeline: hybrid | Sure: 45s | Maliyet: $1.00 | Oncelik: P1
- Platform: Tumu
- Hook: "Turkiye'nin en cok tercih edilen aritma cihazi kutusundan cikiyor."
- Gorseller: Urun hero shot, bilesen etiketleri, spec rozetleri
- CTA: "Detayli inceleme icin kanalimizdaki tam videoyu izleyin"

**14. 1 Ay Sonra: Aritma Cihazi Hayatimizi Nasil Degistirdi?**
- Pipeline: avatar-spokesperson | Sure: 60s | Maliyet: $1.80 | Oncelik: P2
- Platform: Instagram Reels, TikTok
- Hook: Avatar iki bardak su tutuyor: "Bir ay once fark goremezdim..."
- Gorseller: Avatar sunucu, oncesi/sonrasi TDS, gunluk rutin, tasarruf
- CTA: "Siz de farki yasayin - ucretsiz deneme icin bio'daki linke tiklayin"

### Kategori D: Nasil Yapilir (15-17)

**15. Su Aritma Filtre Degisimi: Adim Adim Rehber**
- Pipeline: explainer | Sure: 60s | Maliyet: $0.60 | Oncelik: P0
- Platform: YouTube Shorts
- Hook: Kirli, rengi degismis filtre cikartiliyor: "6 aydir suyunuzu 'aritiyordu.'"
- Gorseller: Numarali adim dizisi, filtre tanimlama rehberi, zamanlama tablosu
- CTA: "Filtre degisim zamanini kacirmayin - Buzsu hatirlaticisini kurun"

**16. Evde Su Kalitesi Nasil Test Edilir? (3 Kolay Yontem)**
- Pipeline: explainer | Sure: 45s | Maliyet: $0.50 | Oncelik: P1
- Platform: Tumu
- Hook: "Evinizde 3 dakikada suyunuzun kalitesini olcebilirsiniz."
- Gorseller: TDS metre kullanimi, pH seridi renk tablosu, kaynatma testi
- CTA: "TDS metreniz yoksa yoruma OLCUM yazin, ozel indirimli link gonderelim"

**17. Montaj: Profesyonel mi Yoksa Kendin Yap mi?**
- Pipeline: hybrid | Sure: 45s | Maliyet: $0.80 | Oncelik: P2
- Platform: YouTube Shorts, TikTok
- Hook: Kotu baglantidan su fiskiriyor: "Kendiniz takmadan once bunu izleyin."
- Gorseller: Split-screen DIY vs profesyonel, hata galerisi, sure karsilastirma
- CTA: "Ucretsiz profesyonel montaj icin Buzsu'yu arayin"

### Kategori E: Karsilastirma (18-20)

**18. Ters Ozmoz vs Ultrafiltrasyon: Hangisi Size Uygun?**
- Pipeline: animation | Sure: 60s | Maliyet: $0.60 | Oncelik: P1
- Platform: Tumu
- Hook: Iki farkli membrana buyutec: "Iki teknoloji, hangisi dogru?"
- Gorseller: Gozemek boyutu animasyonu, filtreleme matrisi, karar agaci
- CTA: "Karar veremiyorsaniz ucretsiz danismanlik hattimizi arayin"

**19. Sise Suyu vs Musluk Suyu vs Aritilmis Su: Buyuk Karsilastirma**
- Pipeline: cinematic | Sure: 60s | Maliyet: $1.00 | Oncelik: P0
- Platform: Tumu
- Hook: Uc bardak su: "Biri 50 kurus, biri 5 lira, biri bedava. Hangisini secerdiniz?"
- Gorseller: 6 boyutlu karsilastirma, skor tablosu, cevre etkisi, kazanan aciklama
- CTA: "Akilli secimi yapin. Ucretsiz su testi icin bio'daki linke tiklayin"

**20. Yazin Suyunuz Neden Daha Kotu? Mevsimsel Su Kalitesi**
- Pipeline: explainer | Sure: 45s | Maliyet: $0.70 | Oncelik: P1
- Platform: TikTok, Reels (mevsimsel/zamanli icerik)
- Hook: 40 derece termometre + su bardagi: "Sicaklar basladiginda suyunuzun tadi neden degisiyor?"
- Gorseller: Mevsim carki, baraj buharlasmasi, bakteri buyumesi, mevsimsel TDS grafigi
- CTA: "Yaza hazir olun - filtrelerinizi simdi kontrol edin"

### Uretim Oncelik Ozeti

P0 - Ilk Yapilacak (9 video, toplam ~$7.20):
- #1 Musluk Suyu Icilebilir mi
- #2 TDS Nedir
- #3 Su Sertligi Nedir
- #7 Istanbul Su Kalitesi
- #10 Turkiye Su Sertligi Haritasi
- #11 Damacana vs Aritma
- #12 5 Kritik Hata
- #15 Filtre Degisimi Rehberi
- #19 Buyuk Karsilastirma

P1 - Yakinda (8 video, toplam ~$6.30):
- #4, #5, #6, #8, #9, #16, #18, #20

P2 - Sonra (3 video, toplam ~$3.60):
- #13, #14, #17

### Pipeline Kullanim Dagilimi

| Pipeline | Adet | Konular |
|----------|------|---------|
| explainer | 8 | 1, 3, 6, 8, 12, 15, 16, 20 |
| animation | 5 | 2, 4, 10, 11, 18 |
| cinematic | 2 | 5, 19 |
| documentary-montage | 2 | 7, 9 |
| hybrid | 2 | 13, 17 |
| avatar-spokesperson | 1 | 14 |

### Mevsimsel Icerik Takvimi

| Mevsim | Konular | Yayinlama |
|--------|---------|-----------|
| Yaz (Haz-Agu) | #20 mevsimsel kalite, #3 sert su/cilt, #5 gorunmez tehlikeler | Mayis-Haziran |
| Ramazan | #6 bebek/aile suyu, #1 musluk suyu guvenligi | Ramazan'dan 2 hafta once |
| Okula Donus (Eyl) | #6 bebek/cocuk suyu, #16 evde test | Agustos |
| Kis (Ara-Sub) | #8 Ankara sert su, #17 montaj | Kasim |

### Ilk 3 Yayinlanacak Video

1. #2 TDS Nedir (en ucuz, en egitici, en yuksek etkilesim)
2. #10 Turkiye Haritasi (izleyiciler sehirlerini yoruma yazar = algoritma destekcisi)
3. #11 Damacana vs Aritma (para tasarrufu = guclu motivasyon)

---

## SONRAKI ADIMLAR

Bilgisayara geciste:

Faz 0: OpenMontage icerigini root'a kopyala
Faz 1: FFmpeg kur, make setup, Python deps

Sonra sirasyla:
- suvesu-brand.yaml ve buzsu-brand.yaml olustur (Bolum 3 tasarimlarindan)
- turkish-short-video.yaml pipeline olustur
- content/cities/ ilk 10 sehir YAML dosyasi olustur (Bolum 4 semasindan)
- Ilk test videosu: "TDS Nedir? 60 Saniyede Anlat"

---

Rapor tamamlandi. Kod degisikligi yapilmadi. Commit atilmadi. Deploy yapilmadi. API key istenmedi.
