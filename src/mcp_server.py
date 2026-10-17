#!/usr/bin/env python3
"""
Lightweight, zero-dependency JSON-RPC 2.0 stdio MCP Server for G*Power Clone (ANOVA: Fixed effects, omnibus, one-way).
=====================================================================================================================
Follows Model Context Protocol (MCP) standard over standard I/O (JSON-RPC 2.0).
Directly imports and delegates to the clean clean-room math engine (src.engine).
Does NOT duplicate or re-implement any calculation logic.

Protocol Support:
  - initialize
  - tools/list
  - tools/call
"""

import sys
import os
import json
from pathlib import Path

# Add src folder to sys.path so it runs standalone
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import a_priori, post_hoc

TOOLS = [
    {
        "name": "calculate_anova_oneway_sample_size",
        "description": "Compute required minimum total sample size (A priori analysis) for one-way omnibus ANOVA across multiple independent groups, given Cohen's f, alpha, target power, and group count k. Matches G*Power 3.1.9.7 exact calculations.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "f": {
                    "type": "number",
                    "description": "Cohen's effect size f (e.g., 0.10 small, 0.25 medium, 0.40 large)"
                },
                "alpha": {
                    "type": "number",
                    "description": "Significance level / Type I error probability (e.g. 0.05)"
                },
                "power": {
                    "type": "number",
                    "description": "Target power 1 - beta (e.g. 0.80 or 0.95)"
                },
                "k": {
                    "type": "integer",
                    "description": "Number of groups (must be an integer >= 2)"
                }
            },
            "required": ["f", "alpha", "power", "k"]
        }
    },
    {
        "name": "calculate_anova_oneway_power",
        "description": "Compute achieved statistical power (Post hoc analysis) for one-way omnibus ANOVA, given Cohen's f, alpha, total sample size N, and group count k.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "f": {
                    "type": "number",
                    "description": "Cohen's effect size f"
                },
                "alpha": {
                    "type": "number",
                    "description": "Significance level (e.g. 0.05)"
                },
                "n_total": {
                    "type": "integer",
                    "description": "Total sample size across all groups"
                },
                "k": {
                    "type": "integer",
                    "description": "Number of groups (must be an integer >= 2)"
                }
            },
            "required": ["f", "alpha", "n_total", "k"]
        }
    }
]

def handle_rpc_message(msg):
    req_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "gpower-anova-mcp",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS
            }
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "calculate_anova_oneway_sample_size":
                res = a_priori(
                    f=float(arguments["f"]),
                    alpha=float(arguments["alpha"]),
                    power=float(arguments["power"]),
                    k=int(arguments["k"])
                )
                payload = {
                    "n_total": res.n_total,
                    "n_per_group": res.n_per_group,
                    "actual_power": round(res.actual_power, 7),
                    "critical_f": round(res.critical_f, 4),
                    "df1": res.df1,
                    "df2": res.df2,
                    "ncp": round(res.ncp, 4)
                }
            elif tool_name == "calculate_anova_oneway_power":
                res = post_hoc(
                    f=float(arguments["f"]),
                    alpha=float(arguments["alpha"]),
                    n_total=int(arguments["n_total"]),
                    k=int(arguments["k"])
                )
                payload = {
                    "actual_power": round(res.actual_power, 7),
                    "critical_f": round(res.critical_f, 4),
                    "df1": res.df1,
                    "df2": res.df2,
                    "ncp": round(res.ncp, 4)
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method / tool '{tool_name}' not found"
                    }
                }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(payload)
                        }
                    ],
                    "isError": False
                }
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"error": str(e)})
                        }
                    ],
                    "isError": True
                }
            }

    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Unrecognized RPC method '{method}'"
                }
            }
        return None

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_rpc_message(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as err:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(err)}"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
