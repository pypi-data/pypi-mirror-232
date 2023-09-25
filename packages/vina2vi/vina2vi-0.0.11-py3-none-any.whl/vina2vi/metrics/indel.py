from typing import (
    Callable,
    Sequence,
)

import numpy as np
from rapidfuzz.distance.Indel import (
    distance,
    normalized_distance,
    similarity,
    normalized_similarity,
)
from tqdm.auto import tqdm

from vina2vi.util import (
    cased_vina_normalizer,
    uncased_vina_normalizer,
)


def quick_eval(
    *,
    pred: Sequence[str] | None = None,
    gt: Sequence[str],
    translate: Callable | None = None,
    similarity: Callable = normalized_similarity,
    cased: bool = True,
    verbose: bool = False,
) -> dict:
    if pred is None:
        vina_normalizer = (
            cased_vina_normalizer if cased else uncased_vina_normalizer)
        pred = [translate(vina_normalizer.normalize_str(s)) for s in tqdm(gt)]

    if not cased:
        gt = [s.lower() for s in gt]

    if verbose:
        width = 80
        for p, g in zip(pred, gt):
            for i in range(0, max(len(p), len(g)), width):
                print(f'(p) "{p[i:i+width]}"')
                print(f'(g) "{g[i:i+width]}"')
            print()

    scores = np.array([similarity(p, g) for p, g in zip(pred, gt)])

    return {
        "mean": np.mean(scores),
        "median": np.median(scores),
    }
