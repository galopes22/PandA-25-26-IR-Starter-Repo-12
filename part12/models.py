from __future__ import annotations
from typing import List, Dict, Any, Tuple, Callable
from nltk.stem import PorterStemmer


class Sonnet:
    def __init__(self, sonnet_data: Dict[str, Any]):
        self.title = sonnet_data["title"]
        # ToDo 0: Make sure the sonnet has an attribute id that contains the number of the Sonnet as an int
        sonnet_no_str = self.title.split(":")[0].split()[1]
        self.id = int(sonnet_no_str)
        self.lines = sonnet_data["lines"]

    @staticmethod
    def find_spans(text: str, pattern: str):
        """Return [(start, end), ...] for all (possibly overlapping) matches.
        Inputs should already be lowercased by the caller."""
        spans = []
        if not pattern:
            return spans

        for i in range(len(text) - len(pattern) + 1):
            if text[i:i + len(pattern)] == pattern:
                spans.append((i, i + len(pattern)))
        return spans

    def search_for(self: Sonnet, query: str) -> SearchResult:
        title_raw = str(self.title)
        lines_raw = self.lines

        q = query.lower()
        title_spans = self.find_spans(title_raw.lower(), q)

        line_matches = []
        for idx, line_raw in enumerate(lines_raw, start=1):  # 1-based line numbers
            spans = self.find_spans(line_raw.lower(), q)
            if spans:
                line_matches.append(LineMatch(idx, line_raw, spans))

        total = len(title_spans) + sum(len(lm.spans) for lm in line_matches)

        return SearchResult(title_raw, title_spans, line_matches, total)


class LineMatch:
    def __init__(self, line_no: int, text: str, spans: List[Tuple[int, int]]):
        self.line_no = line_no
        self.text = text
        self.spans = spans

    def copy(self):
        return LineMatch(self.line_no, self.text, self.spans)


stemmer = PorterStemmer()

def norm_and_stem(token: str) -> str:
    token = token.lower()
    token = token.replace("'", "").replace(",", "").replace(".", "")
    token = stemmer.stem(token)
    return token

class Posting:
    def __init__(self, line_no: int | None, position: int, original_token: str):
        self.line_no = line_no
        self.position = position
        self.original_token = original_token

    def __repr__(self) -> str:
        return f"{self.line_no}:{self.position}"


class Index:
    def __init__(self, sonnets: list[Sonnet]):
        self.sonnets = {sonnet.id: sonnet for sonnet in sonnets}
        self.dictionary = {}

        for sonnet in sonnets:
            # ToDo 0: Copy the logic from your last solution
            for token, pos in self.tokenize(sonnet.title):
                normalized_token = norm_and_stem(token)
                self._add_token(sonnet.id, normalized_token, token, None, pos)
            for line_no, line in enumerate(sonnet.lines):
                for token, pos in self.tokenize(line):
                    normalized_token = norm_and_stem(token)
                    self._add_token(sonnet.id, normalized_token, token, line_no, pos)

    @staticmethod
    def tokenize(text):
        """
         Split a text string into whitespace-separated tokens.

         Each token is returned together with its starting character
         position in the input string.

         Args:
             text: The input text to tokenize.

         Returns:
             A list of (token, position) tuples, where:
             - token is a non-whitespace substring of `text`
             - position is the 0-based start index of the token in `text`
         """
        import re
        tokens = [
            (match.group(), match.start())
            for match in re.finditer(r"\S+", text)
        ]

        return tokens

    def _add_token(self, doc_id: int, normalized_token: str, original_token: str, line_no: int | None, position: int):
        if normalized_token not in self.dictionary:
            self.dictionary[normalized_token] = {}

        postings_list = self.dictionary[normalized_token]

        if doc_id not in postings_list:
            postings_list[doc_id] = []
        postings_list[doc_id].append(Posting(line_no, position, original_token))


    def search_for(self, token: str) -> dict[int, SearchResult]:
        results = {}

        token = norm_and_stem(token)

        if token in self.dictionary:
            postings_list = self.dictionary[token]
            for doc_id, postings in postings_list.items():
                for posting in postings:
                    sonnet = self.sonnets[doc_id]


                    # ToDo 0: Copy your solution from part 11
                    if posting.line_no is None:
                        start = posting.position
                        end = start + len(posting.original_token)
                        result = SearchResult(
                            title=sonnet.title,
                            title_spans=[(start, end)],
                            line_matches=[],
                            matches=1
                        )
                    else:
                        start = posting.position
                        end = start + len(posting.original_token)

                        lm = LineMatch(
                            line_no=posting.line_no + 1,
                            text=sonnet.lines[posting.line_no],
                            spans=[(start, end)]
                        )

                        result = SearchResult(
                            title=sonnet.title,
                            title_spans=[],
                            line_matches=[lm],
                            matches=1
                        )

                    if doc_id not in results:
                        results[doc_id] = result
                    else:
                        results[doc_id] = results[doc_id].combine_with(result)

        return results

class Searcher:
    def __init__(self, sonnets: List[Sonnet]):
        self.index = Index(sonnets)

    def search(self, query: str, search_mode: str) -> List[SearchResult]:
        words = query.split()

        combined_results = {}

        for word in words:
            # Searching for the word in all sonnets
            results = self.index.search_for(word)

            # ToDo 0: Copy your solution from part 11
            if not combined_results:
                combined_results = results.copy()
                continue

            unseen_combined = {}

            if search_mode.upper() == "AND":
                for doc_id in combined_results:
                    if doc_id in results:
                        unseen_combined[doc_id] = combined_results[doc_id].combine_with(results[doc_id])
            elif search_mode.upper() == "OR":
                for doc_id in combined_results:
                    if doc_id in results:
                        unseen_combined[doc_id] = combined_results[doc_id].combine_with(results[doc_id])
                    else:
                        unseen_combined[doc_id] = combined_results[doc_id]

                for doc_id in results:
                    if doc_id not in unseen_combined:
                        unseen_combined[doc_id] = results[doc_id]
            else:
                raise ValueError(f"Unknown search mode: {search_mode}")

            combined_results = unseen_combined

        results = list(combined_results.values())
        return sorted(results, key=lambda sr: sr.title)


class SearchResult:
    def __init__(self, title: str, title_spans: List[Tuple[int, int]], line_matches: List[LineMatch],
                 matches: int) -> None:
        self.title = title
        self.title_spans = title_spans
        self.line_matches = line_matches
        self.matches = matches

    def copy(self):
        return SearchResult(self.title, self.title_spans, self.line_matches, self.matches)

    @staticmethod
    def ansi_highlight(text: str, spans, highlight_mode) -> str:
        """Return text with ANSI highlight escape codes inserted."""
        if not spans:
            return text

        spans = sorted(spans)
        merged = []

        # Merge overlapping spans
        current_start, current_end = spans[0]
        for s, e in spans[1:]:
            if s <= current_end:
                current_end = max(current_end, e)
            else:
                merged.append((current_start, current_end))
                current_start, current_end = s, e
        merged.append((current_start, current_end))

        ansi_sequence = "\033[43m\033[30m" if highlight_mode == "DEFAULT" else "\033[1;92m"

        # Build highlighted string
        out = []
        i = 0
        for s, e in merged:
            out.append(text[i:s])
            out.append(ansi_sequence)  # yellow background, black text
            out.append(text[s:e])
            out.append("\033[0m")  # reset
            i = e
        out.append(text[i:])
        return "".join(out)

    def print(self, idx, highlight_mode: str | None, total_docs):
        title_line = (
            self.ansi_highlight(self.title, self.title_spans, highlight_mode)
            if highlight_mode
            else self.title
        )
        print(f"\n[{idx}/{total_docs}] {title_line}")
        for lm in self.line_matches:
            line_out = (
                self.ansi_highlight(lm.text, lm.spans, highlight_mode)
                if highlight_mode
                else lm.text
            )
            print(f"  [{lm.line_no:2}] {line_out}")

    def combine_with(self: SearchResult, other: SearchResult) -> SearchResult:
        """Combine two search results."""

        combined = self.copy()  # shallow copy

        combined.matches = self.matches + other.matches
        combined.title_spans = sorted(self.title_spans + other.title_spans)

        # Merge line_matches by line number
        lines_by_no = {lm.line_no: lm.copy() for lm in self.line_matches}
        for lm in other.line_matches:
            ln = lm.line_no
            if ln in lines_by_no:
                # extend spans & keep original text
                lines_by_no[ln].spans.extend(lm.spans)
            else:
                lines_by_no[ln] = lm.copy()

        combined.line_matches = sorted(lines_by_no.values(), key=lambda lm: lm.line_no)

        return combined
