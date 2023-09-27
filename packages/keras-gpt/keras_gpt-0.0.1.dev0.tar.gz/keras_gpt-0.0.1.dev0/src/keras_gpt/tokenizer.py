import json
from ast import literal_eval
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import regex


class Tokenizer:
    r"""Byte-pair encoding (BPE) tokenizer implementation as in the original paper
    'Neural Machine Translation of Rare Words with Subword Units' at https://arxiv.org/pdf/1508.07909.pdf
    """

    regex_pattern = (
        r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"
    )

    def __init__(
        self, vocab_file: Optional[str] = None, merge_rules_file: Optional[str] = None
    ) -> None:
        self.compiled_pattern = regex.compile(self.regex_pattern)

        self.vocab = (
            {int(key): value for key, value in json.load(open(vocab_file)).items()}
            if vocab_file is not None
            else self.generate_starting_vocab()
        )
        self.merge_rules = (
            {
                literal_eval(key): value
                for key, value in json.load(open(merge_rules_file)).items()
            }
            if merge_rules_file is not None
            else {}
        )

    @staticmethod
    def generate_starting_vocab() -> Dict[int, str]:
        starting_byte_chars = (
            list(range(ord("!"), ord("~") + 1))
            + list(range(ord("¡"), ord("¬") + 1))
            + list(range(ord("®"), ord("ÿ") + 1))
        )  # Missing: {128: "", 129: "", 130: "", 132: ""}

        vocab: Dict[int, str] = defaultdict(str)

        last_byte_char = 2**8
        for byte_value in range(2**8):
            byte_char = chr(byte_value)
            if byte_value not in starting_byte_chars:
                byte_char = chr(last_byte_char)
                last_byte_char += 1
            vocab[byte_value] = byte_char

        return dict(vocab)

    @staticmethod
    def compute_word_frequencies(words: List[str]) -> Dict[str, int]:
        word_frequencies: Dict[str, int] = defaultdict(int)
        for word in words:
            word_frequencies[word] += 1
        return dict(word_frequencies)

    @staticmethod
    def generate_splits(word_frequencies: Dict[str, int]) -> Dict[str, List[str]]:
        return {word: list(word) for word in word_frequencies.keys()}

    @staticmethod
    def compute_pair_frequencies(
        splits: Dict[str, List[str]],
        word_frequencies: Dict[str, int],
    ) -> Dict[Tuple[str, str], int]:
        pair_frequencies: Dict[Tuple[str, str], int] = defaultdict(int)
        for word, word_freq in word_frequencies.items():
            word_split = splits[word]
            if len(word_split) < 2:
                continue
            for i in range(len(word_split) - 1):
                pair_frequencies[(word_split[i], word_split[i + 1])] += word_freq
        return dict(pair_frequencies)

    @staticmethod
    def merge_pair(
        pair: Tuple[str, str],
        word_frequencies: Dict[str, int],
        splits: Dict[str, List[str]],
    ) -> Dict[str, List[str]]:
        for word in word_frequencies.keys():
            word_split = splits[word]
            if len(word_split) < 2:
                continue
            idx = 0
            while idx < len(word_split) - 1:
                if (word_split[idx], word_split[idx + 1]) == pair:
                    word_split[idx] += word_split[idx + 1]
                    del word_split[idx + 1]
                idx += 1
            splits[word] = word_split
        return splits

    def pre_tokenize(self, text: str) -> List[str]:
        """Comparable to the following:

        >>> from transformers import AutoTokenizer
        >>> tokenizer = AutoTokenizer.from_pretrained("gpt2")
        >>> tokenizer.backend_tokenizer.pre_tokenizer.pre_tokenize_str("..."))
        """
        return [
            "".join([self.vocab[letter] for letter in token.encode("utf-8")])
            for token in self.compiled_pattern.findall(text)
        ]

    def train(self, corpus: str, target_vocab_size: int) -> None:
        assert target_vocab_size > len(self.vocab), (
            "`target_vocab_size` must be greater than the size of the current `vocab`"
            f" which is {len(self.vocab)}."
        )

        tokens = self.pre_tokenize(corpus)
        word_frequencies = self.compute_word_frequencies(tokens)
        splits = self.generate_splits(word_frequencies)

        while len(self.vocab) < target_vocab_size:
            pair_frequencies = self.compute_pair_frequencies(
                splits, word_frequencies=word_frequencies
            )
            if len(pair_frequencies) < 1:
                break
            pair_to_merge = max(pair_frequencies, key=pair_frequencies.get)  # type: ignore
            splits = self.merge_pair(
                pair=pair_to_merge, word_frequencies=word_frequencies, splits=splits
            )

            if pair_to_merge not in self.merge_rules:
                self.merge_rules[pair_to_merge] = "".join(pair_to_merge)
            if "".join(pair_to_merge) not in self.vocab.values():
                self.vocab[len(self.vocab)] = "".join(pair_to_merge)

    def dump_vocab(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.vocab, f, indent=4)

    def dump_merge_rules(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(
                json.dumps(
                    {str(key): value for key, value in self.merge_rules.items()},
                    indent=4,
                )
            )

    def encode(self, text: str) -> List[int]:
        word_splits = [list(token) for token in self.pre_tokenize(text)]
        for pair in self.merge_rules.keys():
            for idx_split, word_split in enumerate(word_splits):
                idx = 0
                while idx < len(word_split) - 1:
                    if (word_split[idx], word_split[idx + 1]) == pair:
                        word_split[idx] += word_split[idx + 1]
                        del word_split[idx + 1]
                    idx += 1
                word_splits[idx_split] = word_split
        return sum(word_splits, [])  # type: ignore
