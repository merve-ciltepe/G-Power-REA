# HALLUCINATIONS.md: Halüsinasyon ve Hata Günlüğü

Tersine mühendislik ve temiz oda geliştirme sürecinde ajanın yanlış çıkardığı, varsaydığı ve diferansiyel testler/ikili analizle yakalanıp düzeltilen en az 2 kritik bulgu aşağıdadır.

---

## 1. Halüsinasyon #1: Tekil Örneklem Artırımı (N = 158 vs N = 159)
- **Ajanın İlk Yanılgısı**: Ajan, G*Power'ın a-priori modunda $N$ toplam örneklem sayısını $N = k+1$'den başlatarak tek tek ($N = N + 1$) artırdığını ve ilk $Power \ge 0.80$ olan $N$'i döndürdüğünü varsaydı.
- **Nasıl Fark Edildi?**: 
  - İlk kod yazıldığında $f=0.25, \alpha=0.05, power=0.80, k=3$ girdiğinde motorumuz `{"n_total": 158}` sonucunu üretti.
  - Ancak araştırmacı G*Power 3.1.9.7 grafik arayüzünde aynı parametrelerle hesaplama yaptığında ekran görüntüsünde `Total sample size = 159` ve `Denominator df = 156` görüldü.
- **Hangi Test Yakaladı?**: 
  - `tests/differential_test.py` diferansiyel testi ve kullanıcı tarafından sağlanan oracle ekran görüntüsü (`gp_apriori_f025_a005_p080_k3.png`).
- **Kök Neden ve Düzeltme**: 
  - G*Power'ın One-Way ANOVA omnibus tasarımında **eşit grup büyüklüğü (balanced design)** varsaydığı ve iterasyonu doğrudan toplam $N$ üzerinde değil, $n_{per\_group}$ ($n_1 = n_2 = \dots = n_k$) üzerinde yürüttüğü anlaşıldı. 
  - $N = 158$ sayısı 3'e tam bölünemez ($158 / 3 = 52.66$). G*Power her gruba tam 53 denek vererek $N = 53 \times 3 = 159$ değerini seçmektedir.
  - Arama döngüsü `n_per_group += 1` ve `n = n_per_group * k` olarak güncellendiğinde G*Power ile %100 tam eşleşme sağlandı.

---

## 2. Halüsinasyon #2: Metin İçi Sayısal Karışıklık (0.10 Etki Büyüklüğü vs 0.10 Alfa Değeri)
- **Ajanın İlk Yanılgısı**: Doğal dil ajanı (Clinical Agent) geliştirilirken, sorgu içinde geçen `%10` veya `0.10` sayısının her zaman alfa anlamlılık düzeyi olduğu varsayıldı.
- **Nasıl Fark Edildi?**: 
  - 10 soruluk klinik test senaryosu çalıştırıldığında (Senaryo 3): *"Onkoloji alanında 3 tedavi kolunda küçük bir biyobelirteç farkını (küçük etki f=0.10) %80 güçle saptamak için toplam kaç hasta alınmalıdır?"* sorusunda ajan, `f=0.10` değerini alfa olarak algılayıp `alpha=0.10` atadı.
  - Sonuçta $N=969$ yerine $N=774$ hesaplandı ve test başarısız oldu (`FAIL`).
- **Hangi Test Yakaladı?**: 
  - `tests/eval_clinical_agent.py` içindeki 10 klinik benchmark değerlendirme testi.
- **Kök Neden ve Düzeltme**: 
  - Tıbbi metinlerde `f=0.10` ile `alpha=0.10` ifadelerinin birbirine karışmaması için `parse_clinical_query` fonksiyonundaki düzenli ifadeler (regex) kelime sınırları (`\b`) ve net bağlam (`alfa=`, `anlamlılık=`, `f=`) önceliklendirmesi ile yeniden yapılandırıldı. Düzeltme sonrasında 10 klinik senaryonun 10'unda da (%100) doğru parametre ve tam $N$ eşleşmesi sağlandı.
