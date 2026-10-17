# AGENT_COST.md: Ajan Maliyet ve Süreç Günlüğü

## 1. Kullanılan Ajanlar ve Modeller
- **Tersine Mühendislik Oturumu (Oturum 1 - İnceleme)**:
  - Antigravity REA Asistanı (Claude Sonnet 4.6 & Gemini Flash)
  - Araçlar: REA Native Toolset, Capstone Disassembler, Python PE Parser, Ghidra Analiz Araçları
- **Temiz Oda Yazım Oturumu (Oturum 2 - Yazım ve Doğrulama)**:
  - Temiz Oda Kodlama Ajanı
  - Yalnızca `SPEC.md` ve `LEDGER.md` kabul kriterlerine bakarak Python motoru, CLI, MCP Server ve Klinik Doğal Dil Ajanını inşa etti.

---

## 2. Token ve Maliyet Tahmini
| Aşama | İstek Sayısı | Giriş Token (Yaklaşık) | Çıkış Token (Yaklaşık) | Tahmini Maliyet ($) |
|---|---|---|---|---|
| REA İnceleme & Binary Taraması | 12 | 48,000 | 8,500 | ~$0.18 |
| Motor Kodlama & Temiz Oda Yazımı | 8 | 32,000 | 6,200 | ~$0.12 |
| Diferansiyel Test & Hata Düzeltme | 10 | 38,000 | 7,100 | ~$0.15 |
| MCP & Doğal Dil Ajanı Geliştirme | 9 | 35,000 | 6,800 | ~$0.14 |
| **Toplam** | **39** | **~153,000** | **~28,600** | **~$0.59** |

---

## 3. İterasyon ve Döngü Sayısı
- Toplam iterasyon sayısı: **4 ana döngü**
  1. *İterasyon 1*: Binary PE başlıkları, string ofsetleri (`0x001c8ae4`) ve PE importlarının taranması.
  2. *İterasyon 2*: Temel motorun ve CLI'nın yazılması -> $N=158$ uyuşmazlığının yakalanması.
  3. *İterasyon 3*: Eşit grup boyutu ($n_{per\_group}$) düzeltmesi -> G*Power ile %100 tam eşleşmenin sağlanması (Gate geçildi).
  4. *İterasyon 4*: MCP Sunucusu ve Doğal Dil Ajanının eklenmesi -> 10/10 klinik senaryoda tam doğruluk.

---

## 4. Neyi Farklı Yapardık? (Öz Eleştiri & Gelecek Önerileri)
1. **Ghidra Otomasyonu**: Ghidra zip arşivi (~540MB) indirilmeye çalışılırken arka plan işlem iptali yaşandı. Bunun yerine yerel hafif statik analiz araçları (Capstone / pefile) doğrudan kullanılarak hedefe çok daha hızlı ulaşıldı. Gelecekte büyük araçlar yerine doğrudan hafif disassembly motorları tercih edilmeli.
2. **Kural Tabanlı Ön Filtre**: Klinik doğal dil çıkarımında ilk başta serbest regex kullanılması $f=0.10$ ile $\alpha=0.10$ değerlerinin karışmasına yol açtı. Tıbbi jargon için Pydantic ve yapılandırılmış Function Calling şeması baştan tanımlansaydı 1 iterasyon tasarruf edilebilirdi.
