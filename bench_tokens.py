#!/usr/bin/env python3
"""
Token-size benchmark for MCP tool metadata.

This measures the token footprint of what an MCP client typically has to place
in the model context for tool discovery (list_tools / list_resources).

Notes:
- Uses tiktoken's `cl100k_base` encoding as a stable proxy. Actual tokenization
  differs by model/provider, but deltas here are still useful.
"""

from __future__ import annotations

import asyncio
import importlib.metadata as md
import json

import tiktoken

import server


ENCODING_NAME = "cl100k_base"


def _tok_len(enc: tiktoken.Encoding, s: str) -> int:
    return len(enc.encode(s))


async def main() -> None:
    enc = tiktoken.get_encoding(ENCODING_NAME)

    tools = await server.mcp.list_tools()
    tools_obj = [t.model_dump(mode="json") if hasattr(t, "model_dump") else t for t in tools]
    tools_json = json.dumps(tools_obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))

    resources = await server.mcp.list_resources()
    resources_obj = [
        r.model_dump(mode="json") if hasattr(r, "model_dump") else r for r in resources
    ]
    resources_json = json.dumps(resources_obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))

    print("env:")
    print(f"  mcp={md.version('mcp')}")
    print(f"  tiktoken={md.version('tiktoken')}")
    print(f"  encoding={ENCODING_NAME}")

    print("\nlist_tools:")
    print(f"  tools={len(tools_obj)}")
    print(f"  json_chars={len(tools_json)}")
    print(f"  tokens={_tok_len(enc, tools_json)}")

    desc_rows: list[tuple[str, int]] = []
    for t in tools_obj:
        desc = t.get("description") or ""
        desc_rows.append((t.get("name") or "<?>", _tok_len(enc, desc)))
    desc_rows.sort(key=lambda x: x[1], reverse=True)
    print(f"  description_tokens_total={sum(t for _, t in desc_rows)}")
    print("  top_descriptions:")
    for name, toks in desc_rows[:8]:
        print(f"    {name}={toks}")

    print("\nlist_resources:")
    print(f"  resources={len(resources_obj)}")
    print(f"  json_chars={len(resources_json)}")
    print(f"  tokens={_tok_len(enc, resources_json)}")


if __name__ == "__main__":
    asyncio.run(main())

