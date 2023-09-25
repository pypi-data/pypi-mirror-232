from __future__ import annotations

import re
from collections.abc import Iterable
#from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path
#from typing import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import torch
from huggingface_hub import hf_hub_download
from tqdm.auto import tqdm

from vina2vi.util import (
    Vietnamese,
    uncased_vina_normalizer,
    cased_vi_normalizer,
)


def count(s: str) -> torch.Tensor:
    count_matrix = torch.zeros((len(Bigram.itoc), len(Bigram.itoc)), dtype=torch.int32)
    if s != "":
        # Without normalization, one may obtain a very different count matrix
        s = cased_vi_normalizer.normalize_str(s)
        tokens = list(s.lower())
        unk_index = Bigram.ctoi[Bigram.unk_token]
        c1 = Bigram.bos_token
        for c2 in tokens:
            i1 = Bigram.ctoi.get(c1, unk_index)
            i2 = Bigram.ctoi.get(c2, unk_index)
            count_matrix[i1, i2] += 1
            c1 = c2
        c2 = Bigram.eos_token
        i1 = Bigram.ctoi.get(c1, unk_index)
        i2 = Bigram.ctoi.get(c2, unk_index)
        count_matrix[i1, i2] += 1
    return count_matrix


class Bigram:
    """
    To make the count matrix smaller, we don't take case into consideration.
    That is, this model is uncased.

    """
    # TODO
    # - [ ] Karpathy-like visualization of the count matrix
    # - [x] Methods to load trained matrices (i.e. Model Persistance)
    # - [ ] Make fit() run faster (multiprocessing/threads/async)
    # - [x] A new method to compute proba_matrix from count_matrix
    # - [x] Refactor the smoothing code
    # - [ ] Case-consideration in the method `translate`
    # - [ ] @dataclass
    # - [ ] Hide count_df as __count_df or _count_df
    # - [x] from_pretrained from HFhub
    # - [ ] Shift normalization (Unicode, etc.) from `count` to `map` (of `datasets`)

    bos_token = "<bos>"
    eos_token = "<eos>"
    unk_token = "<unk>"
    # It's important to use `sorted` here because converting a set to
    # a list does not give the same list every time.
    vocab = sorted(Vietnamese.lowers.union(Vietnamese.puncs))
    vocab.extend([str(i) for i in range(10)])
    vocab.extend([bos_token, eos_token, unk_token])
    # char to index
    itoc = vocab
    # index to char
    ctoi = {c: i for i, c in enumerate(itoc)}
    viz_friendly_vocab = vocab[:]
    viz_friendly_vocab[ctoi["\t"]] = r"\t"
    viz_friendly_vocab[ctoi["\n"]] = r"\n"
    viz_friendly_vocab[ctoi[" "]] = r"␣"
    count_matrix = torch.zeros((len(itoc), len(itoc)), dtype=torch.int32)

    def __init__(self, seed: int = 88888888) -> Bigram:
        self.seed = seed
        self.g_cpu = torch.Generator().manual_seed(self.seed)

    @classmethod
    def from_pretrained(cls, count_matrix_pt: str | Path | None = None) -> cls:
        model = cls()
        if count_matrix_pt is None:
            repo_id = "phunc20/vina2vi_bigram"
            filename = "vnexpress_bigram_count_matrix.pt"
            count_matrix_pt = hf_hub_download(
                repo_id=repo_id,
                filename=filename)
        model.count_matrix = torch.load(count_matrix_pt)
        model.update_proba_matrix()
        return model

    def fit(
        self,
        data: Iterable[str],
        *,
        total: int | None = None,
        chunksize: int = 1,
    ) -> None:
        with Pool() as pool:
            # Unable to use a method like self.count in imap_unordered(), it seems,
            # because the class Bigram contains a torch.Generator, which is not picklable.
            matrices = pool.imap_unordered(
                count,
                tqdm(data, total=total),
                chunksize=chunksize,
            )

            for matrix in matrices:
                self.count_matrix += matrix

        self.update_proba_matrix()

    def old_fit(self, data: Iterable[str], *, total: int | None = None) -> None:
        """
        In [1]: from datasets import load_dataset
        
        In [2]: datasets = load_dataset("phunc20/raw_vnexpress")
        Found cached dataset parquet (/home/phunc20/.cache/huggingface/datasets/phunc20___parquet/phunc20--raw_vnexpress-9e98251871d7a456/0.0.0/14a00e99c0d15a23649d0db8944380ac81082d4b021f398733dd84f3a6c569a7)
        100%|██████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 197.57it/s]
        
        In [3]: from vina2vi.models.char_based.bigram import Bigram
        
        In [4]: model = Bigram()
        
        In [6]: total = datasets["train"].num_rows
        
        In [7]: total
        Out[7]: 7531
        
        In [9]: model.old_fit((sample["text"] for sample in datasets["train"]), total=total)
        100%|█████████████████████████████████████████████████████████████████████████████████████| 7531/7531 [08:06<00:00, 15.47it/s]
        
        In [10]: %time model.fit((sample["text"] for sample in datasets["train"]))
        CPU times: user 27.6 s, sys: 3.82 s, total: 31.5 s
        Wall time: 2min 59s
        
        In [14]: import torch
        
        In [15]: torch.equal(model.old_count_matrix, model.count_matrix)
        Out[15]: True

        In [16]: model.fit((sample["text"] for sample in datasets["train"]), total=total)
        100%|█████████████████████████████████████████████████████████████████████████████████████| 7531/7531 [03:03<00:00, 40.94it/s]
        """
        self.old_count_matrix = torch.zeros((len(self.itoc), len(self.itoc)), dtype=torch.int32)
        unk_index = self.ctoi[self.unk_token]
        for s in tqdm(data, total=total):
            if s != "":
                s = cased_vi_normalizer.normalize_str(s)
                tokens = list(s.lower())
                c1 = self.bos_token
                for c2 in tokens:
                    i1 = self.ctoi.get(c1, unk_index)
                    i2 = self.ctoi.get(c2, unk_index)
                    self.old_count_matrix[i1, i2] += 1
                    c1 = c2
                c2 = self.eos_token
                i1 = self.ctoi.get(c1, unk_index)
                i2 = self.ctoi.get(c2, unk_index)
                self.old_count_matrix[i1, i2] += 1

    def update_proba_matrix(self, smoothness: int | None = 1) -> None:
        self.proba_matrix = self.count_matrix.float()
        if smoothness:
            self.add_smoothie(smoothness)
        self.proba_matrix /= self.proba_matrix.sum(
            dim=1,
            keepdim=True,
        )

    def add_smoothie(self, smoothness: int = 1) -> None:
        if isinstance(smoothness, int):
            assert smoothness > 0

        self.proba_matrix += smoothness

    def translate(self, s: str, *, stochastic: bool = False) -> str:
        pred = []
        prev_c = self.bos_token
        unk_index = self.ctoi[self.unk_token]
        for char in s:
            c = uncased_vina_normalizer.normalize_str(char)
            if c in Vietnamese.ambiguous_chars:
                candidates = Vietnamese.ambiguous_chars[c]
                candidate_indices = [self.ctoi[x] for x in candidates]
                prev_i = self.ctoi.get(prev_c, unk_index)
                candidate_weights = self.proba_matrix[prev_i, candidate_indices]
                if stochastic:
                    ii = torch.multinomial(
                        candidate_weights,
                        num_samples=1,
                        replacement=True,
                        generator=self.g_cpu,
                    )
                else:
                    ii = torch.argmax(candidate_weights)

                i = candidate_indices[ii]
                pred_c = self.itoc[i]
            else:
                pred_c = char

            pred.append(pred_c.upper() if char.isupper() else pred_c)
            prev_c = pred_c

        return "".join(pred)

    def visualize(self) -> None:
        #plt.figure(figsize=(32,32), dpi=500)
        #plt.figure()
        plt.figure(figsize=(64,64))
        plt.imshow(self.proba_matrix, cmap="Blues")

        #k = 28
        k = len(self.itoc)
        print(f'{k = }')
        plt.imshow(self.proba_matrix[:k, :k], cmap="Blues")
        for i in range(k):
            for j in range(k):
                #bigram_str = self.itoc[i] + self.itoc[j]
                ## Replace \t, \n and <space> by \\t, \\n and  , resp.
                #bigram_str = re.sub("\t", r"\\t", bigram_str)
                #bigram_str = re.sub("\n", r"\\n", bigram_str)
                #bigram_str = re.sub(" ", "␣", bigram_str)
                bigram_str = self.viz_friendly_vocab[i] + self.viz_friendly_vocab[j]
                plt.text(x=j, y=i, s=bigram_str,
                         ha="center", va="bottom", color="gray")
                plt.text(x=j, y=i, s=f'{self.proba_matrix[i,j].item():.2f}', fontsize=7,
                         ha="center", va="top", color="gray")

        plt.axis("off")
        plt.show()

    def save(self, count_matrix_pt: str | Path | None = None) -> None:
        if count_matrix_pt is None:
            count_matrix_pt = f'{datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")}_count_matrix.pt'
        torch.save(self.count_matrix, count_matrix_pt)

    def equip_df(self) -> None:
        self.count_df = pd.DataFrame(
            data=self.count_matrix.numpy(),
            index=self.viz_friendly_vocab,
            columns=self.viz_friendly_vocab,
        )
        self.update_proba_matrix()
        self.proba_df = pd.DataFrame(
            data=self.proba_matrix.numpy(),
            index=self.viz_friendly_vocab,
            columns=self.viz_friendly_vocab,
        )

    def get_nonzero_count(self, c: str):
        if c == "\t":
            c = r"\t"
        elif c == "\n":
            c = r"\n"
        elif c == " ":
            c = r"␣"

        if not hasattr(self, "count_df"):
            self.equip_df()

        nonzero_df = self.count_df.loc[[c], self.count_df.loc[c] > 0].sort_values(by=[c], axis=1, ascending=False)
        return nonzero_df
