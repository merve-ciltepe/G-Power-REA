#!/usr/bin/env python3
"""
Clinical AI Agent for Medical Researchers & Clinicians (G*Power ANOVA One-Way).
==============================================================================
Translates natural Turkish clinical questions from doctors into structured MCP tool calls.
Strict Safety Rules:
  1. The LLM / Agent NEVER invents or calculates mathematical numbers (N, power, critical F).
  2. All calculations strictly originate from the MCP server (which calls engine.py).
  3. If information is missing or ambiguous, the agent clarifies or defaults to standard medical research conventions (f=0.25 medium effect, alpha=0.05, power=0.80).
"""

import re
import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MCP_SERVER_PATH = str(BASE_DIR / "src" / "mcp_server.py")

def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    p = subprocess.Popen([sys.executable, MCP_SERVER_PATH],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdout, _ = p.communicate(json.dumps(req) + "\n")
    rpc_res = json.loads(stdout.strip())
    content = rpc_res["result"]["content"][0]["text"]
    return json.loads(content)

def parse_clinical_query(user_query: str) -> dict:
    """
    Sistem 1 / Kural tabanlı sınıflandırıcı & parametre çıkarıcı.
    Klinik sorudaki etki büyüklüğü, grup sayısı, hedef güç ve alfa değerlerini yakalar.
    """
    q = user_query.lower()

    # Test selection
    # Check for ANOVA / multiple groups keywords
    is_oneway = any(w in q for w in ["tedavi kolu", "grup", "kol", "anova", "ilaç", "doz", "varyans", "fark"])
    
    # Mode detection
    if any(w in q for w in ["güç nedir", "gücü nedir", "kaç güç", "gücümüz", "post hoc"]):
        mode = "post-hoc"
    else:
        mode = "a-priori"

    # Groups count k
    k = 3 # default 3 arms if unspecified
    k_match = re.search(r'(\d+)\s*(farklı\s*)?(grup|tedavi\s*kolu|kol|ilaç\s*grubu|doz|cerrahi|antibiyotik|rejim|teknik)', q)
    if k_match:
        k = int(k_match.group(1))
    elif re.search(r'\b4\b|\bdört\b', q):
        k = 4
    elif re.search(r'\b5\b|\bbeş\b', q):
        k = 5
    elif re.search(r'\b3\b|\büç\b', q):
        k = 3
    elif re.search(r'\b2\b|\biki\b', q):
        k = 2

    # Effect size f
    f = 0.25 # Cohen's medium effect default
    f_num = re.search(r'(f\s*=\s*|etki\s*büyüklüğü\s*[:=]?\s*)(0\.\d+)', q)
    if f_num:
        f = float(f_num.group(2))
    elif re.search(r'\bküçük\b|\bdüşük etki\b', q):
        f = 0.10
    elif re.search(r'\bbüyük\b|\byüksek etki\b', q):
        f = 0.40
    elif re.search(r'\borta\b|\bstandart etki\b', q):
        f = 0.25

    # Target power
    power = 0.80 # Standard clinical default
    p_num = re.search(r'(güç\s*[:=]?\s*|power\s*[:=]?\s*)(0\.\d+)', q)
    if p_num:
        power = float(p_num.group(2))
    elif "%95" in q or "0.95" in q or "yüksek güç" in q:
        power = 0.95
    elif "%90" in q or "0.90" in q:
        power = 0.90
    elif "%80" in q or "0.80" in q:
        power = 0.80

    # Alpha
    alpha = 0.05
    if re.search(r'(alfa|alpha|\banlamlılık\b)\s*[:=]?\s*0\.01|%1\b', q):
        alpha = 0.01
    elif re.search(r'(alfa|alpha|\banlamlılık\b)\s*[:=]?\s*0\.10|%10\b', q):
        alpha = 0.10
    elif re.search(r'(alfa|alpha|\banlamlılık\b)\s*[:=]?\s*0\.05|%5\b', q):
        alpha = 0.05

    # Total sample size N for post-hoc
    n_total = None
    n_match = re.search(r'(\d+)\s*(hasta|denek|katılımcı|birey|toplam)', q)
    if n_match:
        n_total = int(n_match.group(1))

    return {
        "test": "anova-oneway",
        "mode": mode,
        "f": f,
        "alpha": alpha,
        "power": power,
        "k": k,
        "n_total": n_total
    }

def answer_doctor(query: str) -> str:
    params = parse_clinical_query(query)
    
    log = []
    log.append(f"[Klinik Soru]: {query}")
    log.append(f"[Parametre Çıkarımı]: test={params['test']}, mode={params['mode']}, k={params['k']}, f={params['f']}, alpha={params['alpha']}, target_power={params['power']}")

    if params["mode"] == "a-priori":
        tool_args = {
            "f": params["f"],
            "alpha": params["alpha"],
            "power": params["power"],
            "k": params["k"]
        }
        log.append(f"[MCP Araç Çağrısı]: calculate_anova_oneway_sample_size({tool_args})")
        res = call_mcp_tool("calculate_anova_oneway_sample_size", tool_args)
        log.append(f"[MCP Yanıtı]: {res}")

        if "error" in res:
            response_text = f"Hesaplama hatası: {res['error']}"
        else:
            response_text = (
                f"Sayın Hocam, {params['k']} tedavi kolunuz için (orta düzey etki f={params['f']}, "
                f"alfa={params['alpha']} ve %{int(params['power']*100)} güç hedeflendiğinde):\n"
                f"- Toplam gereken hasta sayısı: {res['n_total']}\n"
                f"- Her bir gruba düşen hasta sayısı: {res['n_per_group']}\n"
                f"- Ulaşılan gerçek istatistiksel güç: %{round(res['actual_power']*100, 2)}\n"
                f"- Kritik F değeri: {res['critical_f']} (df1={res['df1']}, df2={res['df2']})\n"
                f"(Hesaplama G*Power 3.1.9.7 uyumlu motorumuz ve MCP sunucusu tarafından üretilmiştir.)"
            )
    else:
        if not params["n_total"]:
            params["n_total"] = 159 # fallback
        tool_args = {
            "f": params["f"],
            "alpha": params["alpha"],
            "n_total": params["n_total"],
            "k": params["k"]
        }
        log.append(f"[MCP Araç Çağrısı]: calculate_anova_oneway_power({tool_args})")
        res = call_mcp_tool("calculate_anova_oneway_power", tool_args)
        log.append(f"[MCP Yanıtı]: {res}")

        response_text = (
            f"Sayın Hocam, {params['k']} grup ve toplam {params['n_total']} hasta ile elde edilen "
            f"istatistiksel güç: %{round(res['actual_power']*100, 2)} (Kritik F={res['critical_f']})."
        )

    return response_text, "\n".join(log)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
    else:
        q = "Üç farklı hipertansiyon ilacını karşılaştıracağımız klinik bir çalışma planlıyoruz. Standart anlamlılık ve %80 güç için kaç hasta almalıyız?"
    
    ans, logs = answer_doctor(q)
    print(logs)
    print("\n" + "="*50)
    print(ans)
