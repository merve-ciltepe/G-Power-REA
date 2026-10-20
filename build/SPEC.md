# SPEC.md: G*Power ANOVA One-Way (Fixed Effects, Omnibus) Specification

## 1. Genel Bakış
Bu spesifikasyon, **G*Power 3.1.9.7 (Windows)** uygulamasının `F tests` -> `ANOVA: Fixed effects, omnibus, one-way` ailesinin REA ile yapılan tersine mühendislik incelemesinden elde edilen doğrulanmış davranışını tanımlar.

- **Hedef Test**: ANOVA: Fixed effects, omnibus, one-way (K3)
- **Modlar**: `a-priori` (örneklem boyutu N hesapla) ve `post-hoc` (ulaşılan istatistiksel gücü hesapla)
- **Tersine Mühendislik Temeli**: Temiz oda prensibi uyarınca ikili dosyadan (GPowerNT.exe) çıkarılan matematiksel model, sınır kuralları ve arama stratejisi.

---

## 2. Kabul Kriterleri (Gherkin Formatında)

### Senaryo 1: Standart A-Priori Örneklem Boyutu Hesabı (Orta Düzey Etki)
```gherkin
Feature: ANOVA One-Way A-Priori Örneklem Boyutu
  Scenario: Standart 3 grup, orta düzey etki, %80 güç
    Given test ailesi "anova-oneway"
    And analiz modu "a-priori"
    And etki büyüklüğü f = 0.25
    And alfa anlamlılık düzeyi = 0.05
    And hedef güç = 0.80
    And grup sayısı k = 3
    When hesaplama motoru çalıştırıldığında
    Then toplam örneklem boyutu N tam olarak 159 olmalıdır
    And her gruba düşen denek sayısı 53 olmalıdır
    And ulaşılan gerçek güç en az 0.8048873 olmalıdır
    And kritik F değeri 3.0540 olmalıdır
    And df1 = 2 ve df2 = 156 olmalıdır
    And noncentrality parametresi lambda = 9.9375 olmalıdır
```

### Senaryo 2: Yüksek İstatistiksel Güç (%95)
```gherkin
  Scenario: Yüksek güç (%95) hedefiyle 3 grup
    Given analiz modu "a-priori"
    And f = 0.25, alpha = 0.05, power = 0.95, k = 3
    When hesaplama motoru çalıştırıldığında
    Then toplam örneklem boyutu N tam olarak 252 olmalıdır
    And grup başına düşen denek sayısı 84 olmalıdır
    And ulaşılan güç 0.9514888 olmalıdır
    And kritik F değeri 3.0321 olmalıdır
```

### Senaryo 3: Küçük Etki Büyüklüğü (f = 0.10)
```gherkin
  Scenario: Küçük etki büyüklüğü için büyük örneklem gereksinimi
    Given analiz modu "a-priori"
    And f = 0.10, alpha = 0.05, power = 0.80, k = 3
    When hesaplama motoru çalıştırıldığında
    Then toplam örneklem boyutu N tam olarak 969 olmalıdır
    And grup başına düşen denek sayısı 323 olmalıdır
    And ulaşılan güç 0.8011010 olmalıdır
```

### Senaryo 4: Büyük Etki Büyüklüğü (f = 0.40)
```gherkin
  Scenario: Büyük etki büyüklüğü için düşük örneklem
    Given analiz modu "a-priori"
    And f = 0.40, alpha = 0.05, power = 0.80, k = 3
    When hesaplama motoru çalıştırıldığında
    Then toplam örneklem boyutu N tam olarak 66 olmalıdır
    And grup başına düşen denek sayısı 22 olmalıdır
    And ulaşılan güç 0.8180744 olmalıdır
```

### Senaryo 5: Post-Hoc Güç Analizi
```gherkin
  Scenario: Belirli bir örneklem için elde edilen gücün hesabı
    Given analiz modu "post-hoc"
    And f = 0.25, alpha = 0.05, n_total = 159, k = 3
    When hesaplama motoru çalıştırıldığında
    Then hesaplanan gerçek güç 0.8048873 olmalıdır
    And kritik F değeri 3.0540 olmalıdır
    And df1 = 2, df2 = 156 olmalıdır
    And noncentrality lambda = 9.9375 olmalıdır
```

### Senaryo 6: Geçersiz Girdi ve Sınır Değer Doğrulamaları
```gherkin
  Scenario: Grup sayısı 2'den az olduğunda hata üretilmesi
    Given grup sayısı k = 1
    When hesaplama motoru çalıştırıldığında
    Then sistem "Number of groups k must be integer >= 2" hatasıyla sonlanmalıdır
    And çıkış kodu sıfırdan farklı (1) olmalıdır

  Scenario: Negatif veya sıfır etki büyüklüğü
    Given etki büyüklüğü f = -0.1
    When hesaplama motoru çalıştırıldığında
    Then sistem "Effect size f must be > 0" hatası vermelidir

  Scenario: Gücün alfadan küçük veya eşit girilmesi
    Given alpha = 0.05 ve power = 0.04
    When hesaplama motoru çalıştırıldığında
    Then sistem "Power must be greater than alpha" hatası vermelidir
```

---

## 3. Matematiksel Model ve Formüller
1. **Grup Sayısı ve Serbestlik Dereceleri**:
   - Pay serbestlik derecesi: $df_1 = k - 1$
   - Payda serbestlik derecesi: $df_2 = N - k$
2. **Noncentrality Parametresi ($\lambda$)**:
   $$\lambda = f^2 \times N$$
3. **Kritik F Değeri**:
   $$F_{crit} = F^{-1}(1 - \alpha; df_1, df_2)$$
4. **Gerçek Güç (Actual Power)**:
   $$Power = 1 - F_{nc}(F_{crit}; df_1, df_2, \lambda) = P(F_{nc} > F_{crit})$$
5. **Eşit Grup Büyüklüğü Kısıtı**:
   - G*Power ANOVA Omnibus one-way tasarımında grupları daima eşit varsayar ($n_1 = n_2 = \dots = n_k$).
   - Arama adımı $n_{per\_group} \ge 2$ tamsayısı üzerinden ilerler ve toplam örneklem daima $N = k \times n_{per\_group}$ olarak üretilir.
