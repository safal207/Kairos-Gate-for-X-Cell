#!/usr/bin/env python3
"""Retrieve publisher sources from a Kairos manifest and emit SHA-256 evidence.

The script does not alter the source manifest and does not commit downloaded
publisher binaries. It is research infrastructure, not experiment authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USER_AGENT = "Kairos-Gate-source-audit/0.1 (+https://github.com/safal207/Kairos-Gate-for-X-Cell)"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema") != "kairos.smacgmax-source-manifest.v0.1":
        raise ValueError("unexpected manifest schema")
    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("manifest must contain a non-empty sources list")
    return payload


def digest_url(url: str, timeout: float) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    sha256 = hashlib.sha256()
    size = 0
    final_url = url
    content_type: str | None = None

    with tempfile.NamedTemporaryFile(prefix="kairos-smacgmax-", delete=True) as tmp:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - pinned audit URLs
            final_url = response.geturl()
            content_type = response.headers.get_content_type()
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
                sha256.update(chunk)
                size += len(chunk)

    return {
        "status": "RETRIEVED",
        "requested_url": url,
        "final_url": final_url,
        "content_type": content_type,
        "bytes": size,
        "sha256": f"sha256:{sha256.hexdigest()}",
    }


def main() -> int:
    args = parse_args()
    manifest = load_manifest(args.manifest)
    results: list[dict[str, Any]] = []

    for source in manifest["sources"]:
        source_id = source.get("id")
        url = source.get("url")
        if not isinstance(source_id, str) or not isinstance(url, str):
            raise ValueError("every source requires string id and url")
        try:
            result = digest_url(url, args.timeout)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            result = {
                "status": "RETRIEVAL_FAILED",
                "requested_url": url,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        result["id"] = source_id
        results.append(result)

    output = {
        "schema": "kairos.smacgmax-source-digests.v0.1",
        "case_id": manifest["case_id"],
        "manifest_schema": manifest["schema"],
        "authority": {
            "classification": "RESEARCH_ONLY",
            "experiment_authorization": False,
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    failed = [entry for entry in results if entry["status"] != "RETRIEVED"]
    print(
        f"RESEARCH_ONLY sources={len(results)} "
        f"retrieved={len(results) - len(failed)} failed={len(failed)}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
