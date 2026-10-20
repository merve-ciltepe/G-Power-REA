# LEDGER.md: Kanıt Defteri (G*Power 3.1.9.7 Teardown)

Bu defterde her iddia ve davranış kuralı [DOK] (dokümantasyon), [REA] (ikili dosya ve diferansiyel test kanıtı) ve [AJAN] (çıkarım) etiketleriyle açıkça belgelenmiştir.

---

## 1. Hedef Binary Bilgileri
- **Dosya Adı**: `GPowerNT.exe`
- **Sürüm**: 3.1.9.7 (Windows x86 32-bit PE)
- **SHA-256 Hash**: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`
- **Image Base**: `0x00400000`
- **Derleyici / Runtime**: Microsoft Visual C++ 2015-2022 CRT (MFC/C++)

---

## 2. Binary ve Diferansiyel Kanıt Kayıtları [REA]

### [REA-01] ANOVA Omnibus One-Way Test Varlığı ve UI Bağlantısı
- **Adres / Offset**: Dosya offseti `0x001c8ae4` -> Sanal Adres `0x005c9ae4`
- **Dize**: `"ANOVA: Fixed effects, omnibus, one-way"`
- **Kod Referansı (XREF)**: `0x004ba58d` (file offset `0x000b998d`)
- **Açıklama**: Bu test ailesinin menü ve arayüz seçim listesinde tescil edildiği, ilgili dialog ve hesap yönlendiricisinin bu sanal adresi referans aldığı kanıtlandı.

### [REA-02] Grup Sayısı Sınır Kuralı ($k \ge 2$)
- **Adres / Offset**: Dosya offseti `0x001c5594` -> Sanal Adres `0x005c6594`
- **Dize**: `"There must be at least 2 groups."`
- **Kod Referansı (XREF)**: `0x00487cc3` (file offset `0x000870c3`)
- **Assembly İncelemesi**:
  ```assembly
  0x487cb0: cmp dword ptr [esp + 4], 2   ; k parametresini 2 ile karşılaştır
  0x487cb5: jl  0x487cbc                 ; k < 2 ise hata bloğuna atla
  0x487cb7: mov al, 1                    ; k >= 2 geçerli (True)
  0x487cb9: ret 4
  0x487cbc: lea eax, [ecx + 0x2b0]
  0x487cc2: push 0x5c6594                ; "There must be at least 2 groups."
  0x487cc8: call 0x437db0                ; Hata penceresi / mesaj fırlat
  ```
- **Kural**: $k$ tam sayısı kesinlikle 2 veya daha büyük olmalıdır. Aksi halde program işlemi durdurur.

### [REA-03] Minimum Örneklem Boyutu ve Serbestlik Derecesi Kısıtı
- **Adres / Offset**: Dosya offseti `0x001c8a8e` -> Sanal Adres `0x005c9a8e`
- **Dize**: `"violating of the relation: (groups + covariates) < sample size."`
- **Kod Referansı (XREF)**: `0x004b982a` (file offset `0x000b8c2a`)
- **Açıklama**: ANOVA modelinde payda serbestlik derecesi $df_2 = N - k$ formülü ile hesaplandığından $N > k$ şartı zorunludur ($df_2 \ge 1$).

### [REA-04] Dağılım Fonksiyonları Hata ve Yakınsama Sınırları
- **Adresler**:
  - `0x001c36e8` (`0x005c46e8`): `"FDist-Cdf: input parameter out of range"`
  - `0x001c3710` (`0x005c4710`): `"FDist-Cdf: answer below lower search bound"`
  - `0x001c379c` (`0x005c479c`): `"FDist-Quantile: input parameter out of range"`
- **Kod Referansı**: `0x0045a039`
- **Açıklama**: G*Power, F dağılımının kümülatif olasılık fonksiyonu (CDF) ve ters quantile fonksiyonunu dahili C++ rutinleriyle hesaplamakta ve sayısal arama sırasında alt/üst sınır kontrolleri yapmaktadır.

### [REA-05] Kılavuzda Olmayan Davranış #1: Dengeli Tasarım (Balanced Design) & N'in k'nın Katı Olması
- **Tür**: Diferansiyel Test & A-Priori Arama Kanıtı (`oracle/vectors.csv` ve ekran görüntüleri)
- **Problem**: Standart teorik formülde $f=0.25, \alpha=0.05, power=0.80, k=3$ için sürekli/kesirli N yuvarlandığında $N=158$ çıkmaktadır ($158 / 3 = 52.66$).
- **G*Power Gözlenen Davranışı**: G*Power GUI'sinde `Total sample size = 159` ve `Denominator df = 156` ($159 - 3$) olarak üretilir.
- **Kanıtlanan Kural**: G*Power tek yönlü omnibus ANOVA a-priori analizinde grupları mutlak olarak eşit kabul eder ($n_1 = n_2 = \dots = n_k$). Arama doğrudan toplam $N$ üzerinde değil, tamsayı $n_{per\_group}$ üzerinde yürütülür. Bu nedenle toplam örneklem $N$, her zaman $k$'nın tam katıdır:
  $$N = k \times n_{per\_group}$$
- **Doğrulama**: `oracle/screenshots/gp_apriori_f025_a005_p080_k3.png` ve tüm a-priori test vektörleri.

### [REA-06] Kılavuzda Olmayan Davranış #2: Post-Hoc Modunda k'ya Bölünmeyen N Davranışı (Average Group Size)
- **Tür**: GUI Gözlemi ve Diferansiyel Test Kanıtı
- **Gözlem**: Post-hoc analizinde kullanıcı $k$'ya tam bölünmeyen bir örneklem girdiğinde (Örneğin: $N=100, k=3$ veya $N=50, k=4$):
- **G*Power Dialog Çıktısı**: 
  > *"The total sample size (100) is not a multiple of the number of groups (3). The analysis was based on the average group size."*
- **Hesaplama Kuralı**: G*Power işlemi iptal etmez; ortalama grup boyutu $\bar{n} = N / k$ kabulü ile serbestlik derecesini $df_2 = N - k$ ($100 - 3 = 97$) ve noncentrality parametresini $\lambda = f^2 \times N$ ($0.25^2 \times 100 = 6.25$) alarak gücü $0.5885389$ olarak başarıyla üretir.
- **Doğrulama**: `oracle/screenshots/gp_posthoc_f025_a005_n100_k3_unbalanced.png` ve `gp_posthoc_f025_a005_n50_k4_unbalanced.png`.

---

## 3. Dokümantasyon Bulguları [DOK]
- **[DOK-01]**: Noncentrality parametresi $\lambda = f^2 \times N$. (Faul et al., 2007, 2009).
- **[DOK-02]**: $df_1 = k - 1$ ve $df_2 = N - k$.
- **[DOK-03]**: $F_{crit}$ değeri $(1 - \alpha)$ olasılığına karşılık gelen Fisher-Snedecor quantile değeridir.

---

## 4. Ajan Çıkarımları [AJAN]
- **[AJAN-01]**: G*Power'ın F dağılımını hesaplarken kullandığı C++ iç fonksiyonlarının (DCDFLIB veya benzeri sayısal rutinler) SciPy'nin `scipy.stats.f` ve `scipy.stats.ncf` fonksiyonlarıyla 7 ondalık basamağa kadar tam uyumlu çalıştığı diferansiyel testle teyit edilmiştir.
