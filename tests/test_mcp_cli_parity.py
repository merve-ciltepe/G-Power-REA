#!/usr/bin/env python3
"""
Test equivalence between CLI output and MCP Server output.
Ensures both thin layers invoke the exact same core engine and produce identical JSON outputs.
"""

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def run_cli(args):
    cmd = [sys.executable, str(BASE_DIR / "src" / "cli.py")] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(res.stdout.strip())

def run_mcp(tool_name, arguments):
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    p = subprocess.Popen([sys.executable, str(BASE_DIR / "src" / "mcp_server.py")],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    stdout, _ = p.communicate(json.dumps(req) + "\n")
    rpc_res = json.loads(stdout.strip())
    content = rpc_res["result"]["content"][0]["text"]
    return json.loads(content)

def test_equivalence():
    cases = [
        ("a-priori", {"f": 0.25, "alpha": 0.05, "power": 0.80, "k": 3},
         ["--test", "anova-oneway", "--mode", "a-priori", "--f", "0.25", "--alpha", "0.05", "--power", "0.80", "--k", "3"],
         "calculate_anova_oneway_sample_size"),
        ("a-priori", {"f": 0.10, "alpha": 0.05, "power": 0.90, "k": 4},
         ["--test", "anova-oneway", "--mode", "a-priori", "--f", "0.10", "--alpha", "0.05", "--power", "0.90", "--k", "4"],
         "calculate_anova_oneway_sample_size"),
        ("post-hoc", {"f": 0.25, "alpha": 0.05, "n_total": 159, "k": 3},
         ["--test", "anova-oneway", "--mode", "post-hoc", "--f", "0.25", "--alpha", "0.05", "--n-total", "159", "--k", "3"],
         "calculate_anova_oneway_power")
    ]

    print("Running CLI vs MCP Equivalence Tests...")
    all_match = True
    for mode, mcp_args, cli_args, tool in cases:
        cli_out = run_cli(cli_args)
        mcp_out = run_mcp(tool, mcp_args)
        match = (cli_out == mcp_out)
        print(f"  [{mode}] match={match} | CLI: {cli_out} | MCP: {mcp_out}")
        if not match:
            all_match = False

    if all_match:
        print("\nALL CLI AND MCP RESPONSES MATCH 100%! PASS [OK]")
    else:
        print("\nMISMATCH DETECTED! FAIL [X]")
        sys.exit(1)

if __name__ == "__main__":
    test_equivalence()
