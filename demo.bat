@echo off
color 0a
cls
echo ======================================================================
echo          YZM301 TEARDOWN SPRINT: G*POWER CLONE (ANOVA ONE-WAY)
echo ======================================================================
echo.
timeout /t 2 >nul

echo [1/4] Calistiriliyor: CLI A-Priori Modu (f=0.25, alpha=0.05, power=0.80, k=3)
echo python src/cli.py --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.80 --k 3
python src/cli.py --test anova-oneway --mode a-priori --f 0.25 --alpha 0.05 --power 0.80 --k 3
echo.
timeout /t 3 >nul

echo [2/4] Calistiriliyor: CLI Post-Hoc Modu (Bolunmeyen N=100, k=3)
echo python src/cli.py --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --n-total 100 --k 3
python src/cli.py --test anova-oneway --mode post-hoc --f 0.25 --alpha 0.05 --n-total 100 --k 3
echo.
timeout /t 3 >nul

echo [3/4] Calistiriliyor: Diferansiyel Test Suite (G*Power Oracle vs Klon Motor)
echo python tests/differential_test.py --oracle oracle/vectors.csv --cli src/cli.py
python tests/differential_test.py --oracle oracle/vectors.csv --cli src/cli.py
echo.
timeout /t 4 >nul

echo [4/4] Calistiriliyor: MCP Sunucusu ve Klinik AI Ajani (Turkce Klinik Soru)
echo python src/clinical_agent.py "3 farkli ilac grubu icin %%80 gucle kac hasta gerekir?"
python src/clinical_agent.py "3 farkli ilac grubu icin %%80 gucle kac hasta gerekir?"
echo.
timeout /t 3 >nul

echo ======================================================================
echo                    DEMO BASARIYLA TAMAMLANDI!
echo ======================================================================
pause
