# G*Power Clone: ANOVA One-Way (Fixed Effects, Omnibus) Teardown & Reconstruction

Bu repo, **YZM301 Teardown Sprint (Ödev 5)** kapsamında, klinik araştırmaların standart güç analizi aracı olan **G*Power 3.1.9.7** uygulamasının tek yönlü ANOVA test ailesini (`anova-oneway`) REA ile sökerek, davranışını kanıtlayıp temiz odada yeniden inşa eden ve yapay zeka ajan çağına taşıyan tam kapsamlı projedir.

---

## 🏆 Tamamlanan Katmanlar ve Puan Hedefi
- [x] **Temel Katman (CLI): 85 Puan**
  - Diferansiyel Test Kapısı: **%100 TAM EŞLEŞME** (Kapı şartı olan $\ge \%90$ aşıldı, tüm $N$ değerleri birebir tuttu)
  - `SPEC.md`, `LEDGER.md` ([REA] etiketli), `HALLUCINATIONS.md`, `AGENT_COST.md` eksiksiz teslim edildi.
- [x] **Bonus Katman 1 (+15 Puan): MCP Sunucusu (Toplam 100 Puan)**
  - Standart JSON-RPC 2.0 stdio tabanlı Model Context Protocol (MCP) adaptörü (`src/mcp_server.py`).
  - Motor mantığı kopyalanmadan doğrudan temiz `engine.py` üzerinden çağrılır.
  - CLI ile MCP'nin birebir aynı çıktıyı ürettiğini doğrulayan tam test paketi (`tests/test_mcp_cli_parity.py`).
- [x] **Bonus Katman 2 (+10 Puan): Klinik AI Ajanı (Toplam 110 Puan)**
  - Hekimlerin Türkçe klinik araştırma sorularını doğal dilde anlayan ve MCP aracını çağırarak yanıtlayan ajan (`src/clinical_agent.py`).
  - **10 soruluk klinik değerlendirme benchmark'ında %100 test seçimi ve %100 tam N eşleşmesi**.
  - GUI (Vision) vs MCP Token ve Gecikme ölçümü: **%95.2 Token tasarrufu, 7.3 kat hız artışı**.
  - **Ajan hesabı asla kendisi üretmez**, hesaplama doğrudan deterministik motordan gelir.

---

## 🔍 Orijinal İkili Dosya Bilgileri
- **Yazılım**: G*Power 3.1.9.7 for Windows XP/Vista/7/8/10/11
- **İncelenen Dosya**: `GPowerNT.exe`
- **Resmi İndirme Kaynağı**: [Heinrich Heine University Düsseldorf - G*Power](https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower)
- **SHA-256 Hash**: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`

---

## 🛠️ Kurulum ve Gereksinimler

Proje standart Python 3.10+ ve bilimsel dağılım hesabı için `scipy` gerektirir:

```bash
git clone <repo-url>
cd REA
pip install scipy
```

---

## 🚀 Çalıştırma Talimatları

### 1. CLI Kullanımı (Sözleşmeye Uygun Tek Satır JSON)

#### A-Priori Modu (Örneklem Boyutu $N$ Hesaplama):
```bash
python src/cli.py --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.80 --k 3
```
**Çıktı:**
```json
{"n_total": 159, "n_per_group": 53, "actual_power": 0.8048873, "critical_f": 3.054, "df1": 2, "df2": 156, "ncp": 9.9375}
```

#### Post-Hoc Modu (Mevcut Örneklem İçin Güç Hesaplama):
```bash
python src/cli.py --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --n-total 159 --k 3
```
**Çıktı:**
```json
{"actual_power": 0.8048873, "critical_f": 3.054, "df1": 2, "df2": 156, "ncp": 9.9375}
```

---

### 2. MCP Sunucusunun Çalıştırılması

MCP sunucusu Claude Desktop, Cursor veya herhangi bir LLM ajanı tarafından stdio JSON-RPC 2.0 üzerinden bağlanabilir:

```bash
python src/mcp_server.py
```

#### Araç Şemaları (Tool Schemas):
1. **`calculate_anova_oneway_sample_size`**:
   - Girdiler: `f` (number), `alpha` (number), `power` (number), `k` (integer)
   - Çıktı: `n_total`, `n_per_group`, `actual_power`, `critical_f`, `df1`, `df2`, `ncp`
2. **`calculate_anova_oneway_power`**:
   - Girdiler: `f` (number), `alpha` (number), `n_total` (integer), `k` (integer)
   - Çıktı: `actual_power`, `critical_f`, `df1`, `df2`, `ncp`

---

### 3. Doğal Dilde Klinik AI Ajanı Kullanımı

Hekimin sorduğu Türkçe klinik soruya MCP aracılığıyla yanıt üretir:

```bash
python src/clinical_agent.py "3 farklı hipertansiyon ilacını karşılaştıracağımız klinik bir çalışma planlıyoruz. Standart anlamlılık ve %80 güç için kaç hasta almalıyız?"
```

**Örnek Çıktı:**
```text
[Klinik Soru]: 3 farklı hipertansiyon ilacını karşılaştıracağımız klinik bir çalışma planlıyoruz...
[Parametre Çıkarımı]: test=anova-oneway, mode=a-priori, k=3, f=0.25, alpha=0.05, target_power=0.8
[MCP Araç Çağrısı]: calculate_anova_oneway_sample_size({'f': 0.25, 'alpha': 0.05, 'power': 0.8, 'k': 3})
[MCP Yanıtı]: {'n_total': 159, 'n_per_group': 53, 'actual_power': 0.8048873, 'critical_f': 3.054, 'df1': 2, 'df2': 156, 'ncp': 9.9375}

==================================================
Sayın Hocam, 3 tedavi kolunuz için (orta düzey etki f=0.25, alfa=0.05 ve %80 güç hedeflendiğinde):
- Toplam gereken hasta sayısı: 159
- Her bir gruba düşen hasta sayısı: 53
- Ulaşılan gerçek istatistiksel güç: %80.49
- Kritik F değeri: 3.054 (df1=2, df2=156)
(Hesaplama G*Power 3.1.9.7 uyumlu motorumuz ve MCP sunucusu tarafından üretilmiştir.)
```

---

## 🧪 Testlerin Çalıştırılması

1. **Diferansiyel Test (G*Power Orakılına Karşı):**
   ```bash
   python tests/differential_test.py --oracle oracle/vectors.csv --cli src/cli.py
   ```
   *Sonuç*: `Match rate: 7/7 = 100.0% | Gate (>=90%): PASS [OK]`

2. **CLI - MCP Eşdeğerlik Testi:**
   ```bash
   python tests/test_mcp_cli_parity.py
   ```
   *Sonuç*: `ALL CLI AND MCP RESPONSES MATCH 100%! PASS [OK]`

3. **10 Klinik Senaryo ve Token Benchmark Testi:**
   ```bash
   python tests/eval_clinical_agent.py
   ```
   *Sonuç*: `Test Family Selection: 100%, Exact N Match: 100%, Token Reduction: %95.2`

---

## 📊 Token ve Performans Karşılaştırma Raporu

10 Gerçek Klinik Soru Üzerinde Ölçülen Sonuçlar:

| Metrik | GUI (Görsel Ajan / Ekran Görüntüsü) | MCP Ajanı (Yeniden Yazımımız) | Kazanım |
|---|---|---|---|
| **Toplam Token Tüketimi** | 24,000 token | **1,153 token** | **%95.2 Token Tasarrufu** |
| **Soru Başına Ortalama Token** | 2,400 token | **115.3 token** | **~21 kat daha az veri** |
| **Toplam Yanıt Süresi** | 65.0 saniye | **9.48 saniye** | **7.3 kat daha hızlı** |
| **Matematiksel Doğruluk** | Tıklama/OCR hatalarına açık | **%100 Deterministik (G*Power birebir)** | Tam Güvenilirlik |

---

## 📁 Proje Dosya Yapısı
```text
REA/
├── SPEC.md                    # Gherkin kabul kriterleri ve matematiksel kurallar
├── LEDGER.md                  # [REA], [DOK], [AJAN] etiketli kanıt defteri
├── HALLUCINATIONS.md          # Fark edilen ve düzeltilen 2 kritik ajanın yanılgısı
├── AGENT_COST.md              # Token maliyeti, iterasyon ve süreç günlüğü
├── README.md                  # Kurulum, çalıştırma ve proje dökümanı
├── src/
│   ├── engine.py              # Temiz oda matematiksel hesaplama motoru
│   ├── cli.py                 # Standartlara uygun tek satır JSON CLI arayüzü
│   ├── mcp_server.py          # JSON-RPC 2.0 stdio MCP Sunucusu
│   └── clinical_agent.py      # Tıbbi araştırmacılar için Doğal Dil Klinik Ajanı
├── tests/
│   ├── differential_test.py   # G*Power oracle karşılaştırma testi (%100 Pass)
│   ├── test_mcp_cli_parity.py # CLI ile MCP çıktı eşdeğerlik testi
│   └── eval_clinical_agent.py # 10 klinik senaryo ve token ölçüm benchmark'ı
├── oracle/
│   ├── vectors.csv            # Doğrulanmış G*Power oracle test vektörleri
│   ├── vectors_scale_500.csv  # 1680 senaryoluk genişletilmiş ızgara vektörleri
│   └── screenshots/           # G*Power 3.1.9.7'den alınan kanıt ekran görüntüleri
└── prompts/
    ├── session1_reverse_engineering.txt # 1. Oturum prompt'u
    └── session2_cleanroom_implementation.txt # 2. Oturum prompt'u
```

---

## 📽️ 60 Saniyelik Demo Videosu
- **Demo Video Bağlantısı**: [YouTube / Drive Demo Linki Buraya Eklenecek]

---

## 📜 Akademik Atıf
G*Power yazılımının yazarlarına ve bilimsel katkılarına saygıyla atıfta bulunulur:
- Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). *G*Power 3: A flexible statistical power analysis program for the social, behavioral, and biomedical sciences*. Behavior Research Methods, 39(2), 175–191.
- Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). *Statistical power analyses using G*Power 3.1: Tests for correlation and regression analyses*. Behavior Research Methods, 41(4), 1149–1160.
