#!/usr/bin/env python3
"""Run the bounded Geneformer inference through the base BERT encoder only.

The checkpoint remains `BertForMaskedLM`, but the downstream task consumes only
hidden states. This adapter prevents construction of unused vocabulary logits
while preserving the same encoder weights, attention mask, hidden-state index,
and mean-pooling contract.
"""

from __future__ import annotations

from typing import Any

from transformers import BertForMaskedLM


def encoder_only_forward(self: BertForMaskedLM, *args: Any, **kwargs: Any) -> Any:
    """Return base-encoder outputs with hidden states and no MLM vocabulary head."""
    kwargs.pop("labels", None)
    kwargs["output_hidden_states"] = True
    kwargs["return_dict"] = True
    return self.bert(*args, **kwargs)


BertForMaskedLM.forward = encoder_only_forward

from run_gse184241_geneformer_v1_inference import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
