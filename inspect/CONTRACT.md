# CLI Contract: gpower-clone (ANOVA One-Way Omnibus)

## Komut Satırı Çağrısı
```bash
gpower-clone --test anova-oneway --mode <a-priori|post-hoc> [parametreler]
```

## Parametreler
- `--test anova-oneway`: Test ailesi belirteci (Zorunlu, sabit: `anova-oneway`).
- `--mode <a-priori|post-hoc>`: Analiz türü (Zorunlu).
- `--f <float>`: Cohen's f etki büyüklüğü ($f > 0$).
- `--alpha <float>`: Tip I hata olasılığı ($0 < \alpha < 1$).
- `--power <float>`: Hedef istatistiksel güç ($0 < power < 1$, sadece a-priori modunda zorunlu).
- `--k <int>`: Bağımsız grup sayısı ($k \ge 2$).
- `--n-total <int>`: Toplam örneklem boyutu ($N > k$, sadece post-hoc modunda zorunlu).

## Çıktı Formatı
- **Başarılı Çağrı:** Tek satır JSON, çıkış kodu `0`.
  - A-priori örneği:
    ```json
    {"n_total":159,"n_per_group":53,"actual_power":0.8048873,"critical_f":3.054,"df1":2,"df2":156,"ncp":9.9375}
    ```
  - Post-hoc örneği:
    ```json
    {"actual_power":0.8048873,"critical_f":3.054,"df1":2,"df2":156,"ncp":9.9375}
    ```
- **Hatalı / Geçersiz Çağrı:** Tek satır JSON hata mesajı, sıfırdan farklı çıkış kodu (`1`).
  - Örnek:
    ```json
    {"error":"Number of groups k must be integer >= 2, got 1"}
    ```
