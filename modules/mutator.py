"""Password mutation engine — محرك تحوير كلمات المرور."""

import itertools
from typing import List, Set

class PasswordMutator:
    """Apply common human password patterns to base words."""

    COMMON_SUFFIXES = [
        "", "123", "1234", "12345", "123456", "123456789",
        "!", "@", "#", "$", "%", "&", "*", "?", ".", "_", "-",
        "1", "12", "123!", "!123", "@123", "#123",
        "2020", "2021", "2022", "2023", "2024", "2025", "2026",
        "00", "01", "07", "10", "11", "12", "99",
    ]

    COMMON_PREFIXES = [
        "", "!", "@", "#", "$",
        "1", "2", "3",
    ]

    LEET_MAP = {
        'a': ['a', 'A', '@', '4'],
        'b': ['b', 'B', '8'],
        'c': ['c', 'C', '('],
        'e': ['e', 'E', '3'],
        'g': ['g', 'G', '9', '6'],
        'i': ['i', 'I', '1', '!', '|'],
        'l': ['l', 'L', '1', '|'],
        'o': ['o', 'O', '0'],
        's': ['s', 'S', '$', '5', 'z'],
        't': ['t', 'T', '7', '+'],
        'z': ['z', 'Z', '2'],
    }

    @staticmethod
    def leet_variations(word: str) -> Set[str]:
        """Generate leet speak variations of a word."""
        results = {word}
        chars = []
        for c in word:
            chars.append(PasswordMutator.LEET_MAP.get(c.lower(), [c]))

        # Limit combinatorial explosion
        for combo in itertools.product(*chars[:4]):  # max 4 chars for leet
            w = "".join(combo) + word[len(combo):]
            if w != word:
                results.add(w)

        return results

    @staticmethod
    def case_variations(word: str) -> Set[str]:
        """Capitalization patterns humans use."""
        results = {word, word.lower(), word.upper(), word.capitalize()}
        if len(word) > 1:
            results.add(word[0].upper() + word[1:].lower())
            results.add(word[0].lower() + word[1:].upper())
        return results

    @staticmethod
    def date_formats(day: int = None, month: int = None, year: int = None) -> Set[str]:
        """Generate common date formats from birthdate components."""
        results = set()
        if year:
            y2 = str(year)[2:]
            y4 = str(year)
            results.update([y2, y4])
        if day and month:
            results.update([
                f"{day:02d}{month:02d}",
                f"{month:02d}{day:02d}",
                f"{day}{month:02d}",
                f"{month:02d}{day}",
            ])
        if day and month and year:
            y2, y4 = str(year)[2:], str(year)
            results.update([
                f"{day:02d}{month:02d}{y2}",
                f"{day:02d}{month:02d}{y4}",
                f"{month:02d}{day:02d}{y2}",
                f"{month:02d}{day:02d}{y4}",
                f"{y2}{month:02d}{day:02d}",
                f"{y4}{month:02d}{day:02d}",
            ])
        return results

    @staticmethod
    def mutate(word: str, suffixes: List[str] = None, prefixes: List[str] = None) -> Set[str]:
        """Full mutation: case + leet + prefix/suffix combinations."""
        if suffixes is None:
            suffixes = PasswordMutator.COMMON_SUFFIXES
        if prefixes is None:
            prefixes = PasswordMutator.COMMON_PREFIXES

        bases = set()
        for w in PasswordMutator.case_variations(word):
            bases.update(PasswordMutator.leet_variations(w))

        results = set()
        for base in bases:
            for pre in prefixes:
                for suf in suffixes:
                    results.add(f"{pre}{base}{suf}")
                    if pre and suf:
                        results.add(f"{base}{suf}")   # no prefix
                        results.add(f"{pre}{base}")   # no suffix

        return results
