# LEDGER.md: Kanıt Defteri (G*Power 3.1.9.7 Teardown)

Bu defterde her iddia ve davranış kuralı [DOK] (dokümantasyon), [REA] (ikili dosya kanıtı) ve [AJAN] (çıkarım) etiketleriyle açıkça belgelenmiştir.

---

## 1. Hedef Binary Bilgileri
- **Dosya Adı**: `GPowerNT.exe`
- **Sürüm**: 3.1.9.7 (Windows x86 32-bit PE)
- **SHA-256 Hash**: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`
- **Image Base**: `0x00400000`
- **Derleyici / Runtime**: Microsoft Visual C++ 2015-2022 CRT (MFC/C++)

---

## 2. Kanıt Kayıtları

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

### [REA-05] Cohen Etki Büyüklüğü Konvansiyonları
- **Adresler**:
  - `0x001c89b8`: `"f = .10 - small"`
  - `0x001c89c8`: `"f = .25 - medium"`
  - `0x001c89d9`: `"f = .40 - large"`
- **Açıklama**: G*Power GUI'sinde "Determine" tıklandığında sunulan standart klinik etki büyüklüğü seviyeleri ikili dosyada bu sabit dizelerle tanımlanmıştır.

### [REA-06] İkili Dosya Harici Bağımlılıkları
- PE Import Tablosu incelenmiş; `mfc140u.dll`, `KERNEL32.dll`, `api-ms-win-crt-math-l1-1-0.dll` kullanıldığı, herhangi bir harici sayısal Fortran/BLAS/R DLL'i içermediği, tüm dağılım ve N arama algoritmalarının doğrudan `GPowerNT.exe` içine statik olarak derlendiği kanıtlanmıştır.

---

## 3. Dokümantasyon Bulguları [DOK]
- **[DOK-01]**: Noncentrality parametresi $\lambda = f^2 \times N$. (Faul et al., 2007, 2009).
- **[DOK-02]**: $df_1 = k - 1$ ve $df_2 = N - k$.
- **[DOK-03]**: $F_{crit}$ değeri $(1 - \alpha)$ olasılığına karşılık gelen Fisher-Snedecor quantile değeridir.

---

## 4. Ajan Çıkarımları ve Diferansiyel Doğrulama [AJAN]
- **[AJAN-01] Eşit Grup Arama Kuralı**:
  - G*Power a-priori modunda $N$'i doğrudan tek tek artırmak yerine, eşit grup varsayımıyla ($n_1 = n_2 = \dots = n_k$) grup başına denek sayısı olan $n_{per\_group}$ üzerinden arama yapar.
  - *Kanıt Süreci*: İlk başta doğrusal $N$ araması yapıldığında $f=0.25, \alpha=0.05, power=0.80, k=3$ için $N=158$ çıkmıştı. Ancak G*Power GUI'sinde $N=159$ ($53 \times 3$) çıktığı görüldü. Arama stratejisi $n_{per\_group}$ olarak güncellendiğinde tüm G*Power değerleriyle %100 birebir tam eşleşme sağlandı.
