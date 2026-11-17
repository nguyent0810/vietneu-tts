"""Sentence and [PD] parsing shared by the two Long adapters (stdlib only)."""
import re

ABBR = {"tp", "st", "m", "mr", "mrs", "ms", "dr", "pgs", "ts", "gs"}
CLOSERS = '\"”’»\')]}‖'


def split_sentences(text):
    """Split at sentence endings, preserving every non-whitespace character.

    Ellipses before a lowercase continuation stay inside the sentence. Numbers,
    initials and common Vietnamese abbreviations are not sentence boundaries.
    """
    out, start, i = [], 0, 0
    while i < len(text):
        c = text[i]
        if c not in '.!?…':
            i += 1
            continue
        punct_end = i + 1
        while punct_end < len(text) and text[punct_end] in '.!?…':
            punct_end += 1
        punctuation = text[i:punct_end]
        ellipsis = '…' in punctuation or '...' in punctuation
        if c == '.' and not ellipsis:
            if i + 1 < len(text) and not text[i + 1].isspace() and text[i + 1] not in CLOSERS:
                i += 1
                continue
            word = re.search(r"([\w]+)$", text[:i], re.UNICODE)
            word = word.group(1) if word else ''
            compound = re.search(r'\b(?:v\.v|v\.d)\.$', text[:i + 1], re.I)
            if compound:
                following = text[i + 1:].lstrip()
                if following and not following[0].isupper():
                    i += 1
                    continue
            elif word.casefold() in ABBR or (len(word) == 1 and word.isalpha()):
                i += 1
                continue
        end = punct_end
        while end < len(text) and text[end] in CLOSERS:
            end += 1
        if ellipsis and end == punct_end:
            following = text[end:].lstrip()
            if following and following[0].islower():
                i = end
                continue
        # Quote labels and long pauses belong to the preceding sentence.
        suffix = re.match(r'\s*(?:\[TRÍCH DỊCH\])?(?:\s*‖)?', text[end:])
        if suffix and suffix.group().strip():
            end += suffix.end()
        if end == len(text) or text[end].isspace():
            out.append(text[start:end].strip())
            start = end
        i = end
    if text[start:].strip():
        out.append(text[start:].strip())
    return out


class PDSplitter:
    """Keep PD state across paragraphs; return (sentence, is_pd) pairs."""

    def __init__(self):
        self.pd = False

    def feed(self, text):
        out = []
        buffer = ''
        for token in re.split(r'(\[/?PD\])', text):
            if token in ('[PD]', '[/PD]'):
                if buffer.strip():
                    if not buffer.rstrip().endswith(tuple('.!?…' + CLOSERS)):
                        raise ValueError('Marker PD phải nằm ở ranh giới câu')
                    out.extend((sent, self.pd) for sent in split_sentences(buffer))
                    buffer = ''
                if (token == '[PD]') == self.pd:
                    raise ValueError('Marker PD lồng nhau hoặc đóng khi chưa mở')
                self.pd = token == '[PD]'
            else:
                buffer += token
        out.extend((sent, self.pd) for sent in split_sentences(buffer))
        return out

    def finish(self):
        if self.pd:
            raise ValueError('Marker PD chưa đóng')
