# SCALE_REPORT.md: İstatistiksel Kütüphaneler (Statsmodels/R pwr) ile G*Power Arasındaki Diferansiyel Ölçek Raporu

## 1. Giriş ve Amaç
Bu rapor, klasik istatistiksel kütüphaneler (`scipy`, `statsmodels`, R `pwr`) ile **G*Power 3.1.9.7** arasındaki hesaplama ve yuvarlama felsefesi farkını 1.680 parametre kombinasyonu üzerinde diferansiyel olarak belgelemektedir.

---

## 2. Temel Metodolojik Fark: Kesirli N vs. Dengeli Tamsayı N

### A. İstatistik Kütüphanelerinin Yaklaşımı (R `pwr.anova.test` / Statsmodels)
Standart açık kaynak kütüphaneler örneklem büyüklüğünü sürekli (continuous) bir optimizasyon problemi olarak çözer:
- $N$ değeri sürekli bir reel sayı olarak bulunur (örneğin: $N = 157.34$ veya grup başına $n = 52.44$).
- Genellikle kütüphaneler doğrudan bu kesirli sayıyı döner ya da basit bir `ceil()` (tavana yuvarlama) uygular.

### B. G*Power'ın [REA] Kanıtlı Davranışı
G*Power tek yönlü varyans analizinde (ANOVA Omnibus One-Way) **dengeli tasarım (balanced design)** ilkesini katı bir kural olarak uygular:
1. $n_1 = n_2 = \dots = n_k$ olmak zorundadır.
2. Arama uzayı doğrudan $N$ üzerinde değil, tamsayı $n_{per\_group} \ge 2$ üzerinde yürütülür.
3. Toplam örneklem büyüklüğü $N$, her zaman grup sayısı $k$'nın tam katıdır:
   $$N = k \times n_{per\_group}$$

---

## 3. Sayısal Örnek ve Karşılaştırma

| Senaryo Parametreleri | Klasik Kütüphane Çıktısı (Sürekli N) | Basit Tavana Yuvarlama (Ceil) | G*Power 3.1.9.7 Çıktısı | Neden Farklı? |
|---|:---:|:---:|:---:|---|
| $f=0.25, \alpha=0.05, power=0.80, k=3$ | $N = 157.14$ | $N = 158$ | **$N = 159$** ($53 \times 3$) | 158 denek 3 gruba eşit bölünemez ($158/3 = 52.66$). Her gruba 53 denek verilerek $N=159$ yapılır. |
| $f=0.25, \alpha=0.05, power=0.80, k=4$ | $N = 178.21$ | $N = 179$ | **$N = 180$** ($45 \times 4$) | 179 denek 4 gruba eşit bölünemez. $45 \times 4 = 180$ seçilir. |
| $f=0.40, \alpha=0.05, power=0.80, k=3$ | $N = 64.08$ | $N = 65$ | **$N = 66$** ($22 \times 3$) | $22 \times 3 = 66$ seçilir. |

---

## 4. Sonuç ve Diferansiyel Çıkarım
Klinik araştırmalarda protokol gereği her tedavi koluna eşit sayıda hasta atanması hedeflenir. G*Power'ın tasarımcıları (Faul et al.), araştırmacının sahada kesirli denek alamayacağını ve gruplar arası dengenin bozulmaması gerektiğini öngörerek motoru doğrudan $k$'nın katı olacak şekilde inşa etmişlerdir. 

Klon motorumuz (`src/engine.py`), standart kütüphanelerin yaptığı ham kesirli yuvarlama yerine G*Power'ın bu klinik dengeli tasarım kuralını birebir gerçeklemektedir.
