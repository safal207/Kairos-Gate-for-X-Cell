#!/usr/bin/env python3
"""Compatibility entrypoint for the GSE184241 donor benchmark.

Pandas applies a scalar dtype to the index field before index_col extraction in
this GEO table. Load identifiers first, then cast only count columns.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

MODULE_PATH = Path(__file__).with_name("run_gse184241_donor_baselines_v2.py")
SPEC = importlib.util.spec_from_file_location("gse184241_baseline_v2", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load benchmark module: {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def load_counts_fixed(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(
        path,
        sep=r"\s+",
        compression="gzip",
        header=0,
        index_col=0,
        quotechar='"',
        engine="c",
    )
    frame.index = pd.Index([MODULE.clean_identifier(value) for value in frame.index], dtype="object")
    frame.columns = pd.Index([MODULE.clean_identifier(value) for value in frame.columns], dtype="object")
    if frame.index.has_duplicates:
        frame = frame.groupby(level=0, sort=False).sum()
    if frame.columns.has_duplicates:
        raise ValueError("duplicate cell identifiers after quote normalization")
    numeric = frame.apply(pd.to_numeric, errors="raise")
    return numeric.astype(np.float32, copy=False)


MODULE.load_counts = load_counts_fixed

if __name__ == "__main__":
    raise SystemExit(MODULE.main())
