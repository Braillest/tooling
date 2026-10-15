"""
Convert a PDF book into clean plain text for the braillest pipeline.

    python pdf_to_text.py <pdf_file_path> [output_text_file_path] [options]

Output goes to /data/1-texts/<pdf name>.txt by default, ready for generate_all_page_molds.py.

What it does:
- Reads text in reading order (blocks sorted top to bottom, then left to right; or by column with --columns 2).
- Strips running headers, footers, and page numbers (lines near the top/bottom margin that repeat across pages).
- Rejoins words hyphenated across line breaks (soft hyphens always; hard hyphens unless the
  hyphenated form appears elsewhere in the book).
- Rebuilds paragraphs from wrapped lines, including paragraphs that continue onto the next page,
  and reattaches drop caps.
- Puts each chapter heading on its own paragraph preceded by a form feed (\\f) line.
- Normalizes text for liblouis: ligatures, soft hyphens, non breaking and zero width spaces,
  private use glyphs. Curly quotes are kept by default because UEB distinguishes single and double quotes.
- Reports pages that have images but no text. Pass --ocr to OCR them (requires tesseract).
"""

import argparse
import collections
import os
import re
import statistics
import sys
import unicodedata

import pymupdf

# Characters liblouis can't translate or that only exist for typesetting.
CHARACTER_REPLACEMENTS = {
    "\u00ad": "",   # soft hyphen
    "\u200b": "",   # zero width space
    "\u200c": "",   # zero width non joiner
    "\u200d": "",   # zero width joiner
    "\ufeff": "",   # byte order mark
    "\u00a0": " ",  # non breaking space
    "\u2002": " ", "\u2003": " ", "\u2004": " ", "\u2005": " ", "\u2006": " ",
    "\u2007": " ", "\u2008": " ", "\u2009": " ", "\u200a": " ", "\u202f": " ",
    "\u2010": "-",  # hyphen
    "\u2011": "-",  # non breaking hyphen
    "\u2212": "-",  # minus sign
}

ASCII_QUOTE_REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2032": "'", "\u2033": '"',
}

LIGATURES = "\ufb00\ufb01\ufb02\ufb03\ufb04\ufb05\ufb06"

ROMAN_NUMERAL = r"[IVXLCDM]+"
NUMBER_WORDS = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|[a-z]+-[a-z]+)"
CHAPTER_PATTERN = re.compile(
    rf"^(?:(?:chapter|book|part|section)\s+(?:\d+|{ROMAN_NUMERAL}|{NUMBER_WORDS})\b.*|{ROMAN_NUMERAL}\.?|\d{{1,3}}\.?)$",
    re.IGNORECASE,
)
GUTENBERG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG", re.IGNORECASE)
GUTENBERG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG|^End of (?:the )?Project Gutenberg", re.IGNORECASE)
TERMINAL_PUNCTUATION = tuple(".!?:;\u2019\u201d'\")]\u2026")


def normalize_text(text, ascii_quotes=False):
    for character, replacement in CHARACTER_REPLACEMENTS.items():
        text = text.replace(character, replacement)
    for ligature in LIGATURES:
        text = text.replace(ligature, unicodedata.normalize("NFKC", ligature))
    if ascii_quotes:
        for character, replacement in ASCII_QUOTE_REPLACEMENTS.items():
            text = text.replace(character, replacement)
    # Drop private use area glyphs (decorative fonts, page number glyphs, etc).
    text = "".join(c for c in text if not (0xE000 <= ord(c) <= 0xF8FF))
    return re.sub(r"[ \t]+", " ", text)


def margin_key(text):
    """Key used to match running headers/footers across pages: digits and roman numerals collapse to '#'."""
    text = normalize_text(text).strip().lower()
    text = re.sub(r"\d+", "#", text)
    text = re.sub(r"\b[ivxlcdm]+\b", "#", text)
    return re.sub(r"\s+", " ", text)


def is_page_number(text):
    text = normalize_text(text).strip()
    return bool(re.fullmatch(r"(?:page\s*)?(?:\d{1,4}|[ivxlcdm]{1,7})", text, re.IGNORECASE)) or text == ""


def extract_lines(page, columns):
    """Return lines in reading order as dicts with text, bbox, size, and block index."""
    page_dict = page.get_text("dict", flags=pymupdf.TEXT_PRESERVE_WHITESPACE | pymupdf.TEXT_MEDIABOX_CLIP)
    blocks = [b for b in page_dict["blocks"] if b.get("type") == 0]
    width = page.rect.width

    def order(block):
        x0, y0 = block["bbox"][0], block["bbox"][1]
        column = min(int(x0 / (width / columns)), columns - 1) if columns > 1 else 0
        return (column, round(y0, 1), x0)

    lines = []
    for block_index, block in enumerate(sorted(blocks, key=order)):
        for line in block["lines"]:
            spans = [s for s in line["spans"] if s["text"].strip()]
            if not spans:
                continue
            text = "".join(s["text"] for s in line["spans"])
            size = max(s["size"] for s in spans)
            bold = any(s["flags"] & 16 for s in spans)
            entry = {"text": text, "bbox": tuple(line["bbox"]), "size": round(size, 1), "bold": bold, "block": block_index}
            # Lines split at the same baseline (e.g. around an inline margin note) are one line.
            previous = lines[-1] if lines else None
            if (previous is not None and previous["block"] == block_index
                    and abs(previous["bbox"][1] - entry["bbox"][1]) < 2 and entry["bbox"][0] >= previous["bbox"][2] - 1):
                previous["text"] = previous["text"].rstrip() + " " + text.lstrip()
                previous["bbox"] = (previous["bbox"][0], min(previous["bbox"][1], entry["bbox"][1]),
                                    entry["bbox"][2], max(previous["bbox"][3], entry["bbox"][3]))
                previous["size"] = max(previous["size"], entry["size"])
                continue
            lines.append(entry)
    return lines


def in_margin_band(line, height, margin_ratio):
    center = (line["bbox"][1] + line["bbox"][3]) / 2
    return center <= height * margin_ratio or center >= height * (1 - margin_ratio)


def find_running_lines(pages_lines, page_heights, margin_ratio, min_repeat_ratio, body_size):
    """Keys of lines in the top/bottom margin band that repeat across many pages."""
    counts = collections.Counter()
    for lines, height in zip(pages_lines, page_heights):
        keys = set()
        for line in lines:
            if in_margin_band(line, height, margin_ratio) and line["size"] <= body_size + 0.5 and line["size"] <= body_size + 0.5:
                keys.add(margin_key(line["text"]))
        counts.update(keys)
    threshold = max(2, int(len(pages_lines) * min_repeat_ratio))
    return {key for key, count in counts.items() if count >= threshold}


PAGE_ANCHOR = re.compile(r"^\s*\[(?:\d{1,4}|[ivxlcdm]{1,7})\]\s*$", re.IGNORECASE)


def strip_margins(lines, height, running_keys, margin_ratio, body_size):
    """Remove running headers/footers and page numbers. Lines larger than body text (chapter headings) are kept.
    Also removes original edition page anchors such as "[23]" set smaller than body text (common in Gutenberg PDFs)."""
    kept, removed = [], []
    body_bottom = max((l["bbox"][3] for l in lines if abs(l["size"] - body_size) < 0.6), default=height)
    for line in lines:
        # Footnotes: small text below the body text that starts with a marker.
        if (line["size"] <= body_size * 0.85 and line["bbox"][1] >= body_bottom - 1
                and re.match(r"^\s*[\d*†‡§]+\s", line["text"])):
            removed.append(line["text"].strip())
            continue
        if PAGE_ANCHOR.match(line["text"]) and line["size"] < body_size:
            removed.append(line["text"].strip())
            continue
        if in_margin_band(line, height, margin_ratio) and line["size"] <= body_size + 0.5 and (margin_key(line["text"]) in running_keys or is_page_number(line["text"])):
            removed.append(line["text"].strip())
        else:
            kept.append(line)
    return kept, removed


def clean_line(text):
    """Light cleanup for paragraph building. Soft hyphens are kept until lines are joined."""
    text = "".join(c for c in text if not (0xE000 <= ord(c) <= 0xF8FF))
    return re.sub(r"\s+", " ", text).strip()


VERSE_LINE_BREAK = "\u2028"


def is_heading_line(line, text, body_size):
    return line["size"] >= body_size * 1.15 or (line["bold"] and len(text) < 60)


def group_paragraphs(lines, body_size, text_width):
    """Split one page's lines into paragraphs. Each paragraph: dict(lines=[...], heading=bool)."""
    body_lines = [l for l in lines if abs(l["size"] - body_size) < 0.6]
    left = statistics.median([l["bbox"][0] for l in body_lines]) if body_lines else 0
    line_height = statistics.median([l["bbox"][3] - l["bbox"][1] for l in body_lines]) if body_lines else body_size * 1.2

    # Verse: runs of 3+ consecutive capitalized lines that end well short of the right margin keep their line breaks.
    # Measured against the book's full line width, since a page of only verse has no full lines.
    # Verse lines also start with a capital letter, which keeps ragged right prose out.
    short = [l["bbox"][2] < left + text_width * 0.85 and abs(l["size"] - body_size) < 0.6
             and bool(re.match(r"^[\W_]*[A-Z]", clean_line(l["text"]))) for l in lines]
    verse = [False] * len(lines)
    run_start = None
    for index, is_short in enumerate(short + [False]):
        if is_short and run_start is None:
            run_start = index
        elif not is_short and run_start is not None:
            if index - run_start >= 3:
                for j in range(run_start, index):
                    verse[j] = True
            run_start = None

    paragraphs = []
    current = None
    previous = None
    previous_index = None
    pending_cap = None
    cap_bottom = -1

    for index, line in enumerate(lines):
        text = clean_line(line["text"])
        if not text:
            continue

        # Drop cap: a large one or two letter line with body text starting to its right on the same band.
        following = lines[index + 1] if index + 1 < len(lines) else None
        if (line["size"] >= body_size * 1.5 and len(text) <= 2 and text.isalpha() and following is not None
                and following["bbox"][0] >= line["bbox"][2] - 1 and following["bbox"][1] < line["bbox"][3]):
            pending_cap = text
            cap_bottom = line["bbox"][3]
            continue

        heading = is_heading_line(line, text, body_size)
        in_verse = verse[index] and previous_index is not None and verse[previous_index]
        if pending_cap is not None:
            text = pending_cap + text
            pending_cap = None
            new_paragraph = True
        elif in_verse and current is not None and not current["heading"]:
            # Within a stanza: new paragraph only on a stanza gap. Lines keep their breaks.
            new_paragraph = line["bbox"][1] - previous["bbox"][3] > line_height * 0.6
            if not new_paragraph:
                text = VERSE_LINE_BREAK + text
        else:
            wrapped_around_cap = line["bbox"][1] < cap_bottom
            new_paragraph = (
                current is None
                or heading != current["heading"]
                or (line["block"] != previous["block"]  # new block, unless the sentence clearly runs on
                    and not (text[:1].islower() and not clean_line(previous["text"]).endswith(TERMINAL_PUNCTUATION)))
                or (not wrapped_around_cap and not heading and line["bbox"][0] - left > body_size * 0.8)  # first line indent
                or line["bbox"][1] - previous["bbox"][3] > (line_height * 0.6 if not heading else line["size"] * 1.5)  # vertical gap
            )

        if new_paragraph:
            if current is not None:
                paragraphs.append(current)
            current = {"lines": [text.lstrip(VERSE_LINE_BREAK)], "heading": heading, "size": line["size"]}
        else:
            current["lines"].append(text)
            current["size"] = max(current["size"], line["size"])
        previous = line
        previous_index = index

    if current is not None:
        paragraphs.append(current)
    return paragraphs


def join_lines(lines, hyphenated_words):
    """Join wrapped lines, removing line break hyphenation."""
    text = ""
    for line in lines:
        if not text:
            text = line
            continue
        if line.startswith(VERSE_LINE_BREAK):
            text += "\n" + line[1:]
            continue
        if text.endswith("\u00ad"):
            text = text[:-1] + line
            continue
        match = re.search(r"(\w+)-$", text)
        next_word = re.match(r"(\w+)", line)
        if match and next_word and line[0].islower():
            compound = (match.group(1) + "-" + next_word.group(1)).lower()
            if compound in hyphenated_words:
                text += line
            else:
                text = text[:-1] + line
        else:
            text += " " + line
    return text


def main():
    parser = argparse.ArgumentParser(description="Convert a PDF book into clean text for the braillest pipeline.")
    parser.add_argument("pdf_file_path")
    parser.add_argument("output_text_file_path", nargs="?", help="Default: /data/1-texts/<pdf name>.txt")
    parser.add_argument("--first-page", type=int, default=1, help="First page to convert (1 based). Use to skip front matter.")
    parser.add_argument("--last-page", type=int, default=None, help="Last page to convert (1 based).")
    parser.add_argument("--columns", type=int, default=1, help="Number of text columns per page. Default: 1")
    parser.add_argument("--margin", type=float, default=0.15, help="Fraction of page height at top and bottom searched for headers/footers. Default: 0.15")
    parser.add_argument("--repeat", type=float, default=0.3, help="Fraction of pages a margin line must repeat on to count as a running header/footer. Default: 0.3")
    parser.add_argument("--no-chapter-breaks", action="store_true", help="Don't insert form feeds before chapter headings.")
    parser.add_argument("--keep-gutenberg-boilerplate", action="store_true", help="Keep the Project Gutenberg header and license text. By default everything before *** START OF ... and after *** END OF ... is dropped.")
    parser.add_argument("--ascii-quotes", action="store_true", help="Replace curly quotes with straight quotes.")
    parser.add_argument("--ocr", action="store_true", help="OCR pages that have images but no text. Requires tesseract.")
    parser.add_argument("--ocr-language", default="eng")
    args = parser.parse_args()

    if not os.path.isfile(args.pdf_file_path):
        print(f"{args.pdf_file_path} was not found")
        sys.exit(1)

    output_path = args.output_text_file_path
    if output_path is None:
        name = os.path.splitext(os.path.basename(args.pdf_file_path))[0]
        output_path = os.path.join("/data/1-texts", name + ".txt")

    document = pymupdf.open(args.pdf_file_path)
    first = max(1, args.first_page) - 1
    last = min(args.last_page or document.page_count, document.page_count)

    pages_lines, page_heights, image_only_pages, ocr_pages = [], [], [], []
    for page_number in range(first, last):
        page = document[page_number]
        lines = extract_lines(page, args.columns)
        if not lines and page.get_images():
            image_only_pages.append(page_number + 1)
            if args.ocr:
                try:
                    textpage = page.get_textpage_ocr(language=args.ocr_language, dpi=300, full=True)
                    page_dict = page.get_text("dict", textpage=textpage)
                    lines = [
                        {"text": "".join(s["text"] for s in line["spans"]), "bbox": line["bbox"],
                         "size": round(max(s["size"] for s in line["spans"]), 1), "bold": False, "block": block_index}
                        for block_index, block in enumerate(page_dict["blocks"]) if block.get("type") == 0
                        for line in block["lines"] if line["spans"]
                    ]
                    ocr_pages.append(page_number + 1)
                except Exception as error:
                    print(f"OCR failed on page {page_number + 1}: {error}")
        pages_lines.append(lines)
        page_heights.append(page.rect.height)

    # Body font size: the size covering the most characters.
    size_counts = collections.Counter()
    for lines in pages_lines:
        for line in lines:
            size_counts[line["size"]] += len(line["text"])
    body_size = size_counts.most_common(1)[0][0] if size_counts else 10

    running_keys = find_running_lines(pages_lines, page_heights, args.margin, args.repeat, body_size)

    removed_count = 0
    stripped_pages = []
    for lines, height in zip(pages_lines, page_heights):
        kept, removed = strip_margins(lines, height, running_keys, args.margin, body_size)
        removed_count += len(removed)
        stripped_pages.append(kept)

    # Hyphenated words that appear mid line are real compounds and keep their hyphen when split across lines.
    hyphenated_words = set()
    for lines in stripped_pages:
        for line in lines:
            hyphenated_words.update(w.lower() for w in re.findall(r"\b\w+-\w+\b", normalize_text(line["text"])))

    # Full text line width: most lines in a book are full justified lines.
    widths = sorted(l["bbox"][2] - l["bbox"][0] for lines in stripped_pages for l in lines if abs(l["size"] - body_size) < 0.6)
    text_width = widths[int(len(widths) * 0.9)] if widths else 0

    # Build paragraphs across pages.
    paragraphs = []
    for lines in stripped_pages:
        page_paragraphs = group_paragraphs(lines, body_size, text_width)
        if page_paragraphs and paragraphs and not paragraphs[-1]["heading"] and not page_paragraphs[0]["heading"]:
            previous_text = paragraphs[-1]["lines"][-1]
            next_text = page_paragraphs[0]["lines"][0]
            if not previous_text.endswith(TERMINAL_PUNCTUATION) or next_text[:1].islower() or previous_text.endswith(("-", "\u00ad")):
                paragraphs[-1]["lines"].extend(page_paragraphs[0]["lines"])
                page_paragraphs = page_paragraphs[1:]
        paragraphs.extend(page_paragraphs)

    texts = []
    for paragraph in paragraphs:
        text = join_lines(paragraph["lines"], hyphenated_words)
        text = "\n".join(normalize_text(part, args.ascii_quotes).strip() for part in text.split("\n")).strip()
        if text:
            texts.append((text, paragraph))

    # Project Gutenberg license header and footer.
    boilerplate_removed = 0
    if not args.keep_gutenberg_boilerplate:
        starts = [i for i, (text, _) in enumerate(texts) if GUTENBERG_START.search(text)]
        ends = [i for i, (text, _) in enumerate(texts) if GUTENBERG_END.search(text)]
        first_kept = starts[0] + 1 if starts else 0
        last_kept = ends[-1] if ends and ends[-1] > first_kept else len(texts)
        boilerplate_removed = len(texts) - (last_kept - first_kept)
        texts = texts[first_kept:last_kept]

    output = []
    chapter_count = 0
    last_heading_key = None
    body_since_heading = True
    for text, paragraph in texts:
        large_heading = paragraph["heading"] and paragraph["size"] >= body_size * 1.4 and len(paragraph["lines"]) <= 2
        is_chapter = large_heading or (len(paragraph["lines"]) <= 2 and CHAPTER_PATTERN.match(text) and (
            paragraph["heading"] or re.match(r"(?:chapter|book|part)\b", text, re.IGNORECASE)))
        if is_chapter:
            text = re.sub(r"(?<=[^\W\d])\d{1,2}$", "", text)  # footnote marker on a heading
            heading_key = re.sub(r"\W+", " ", text).strip().lower()
            if output and heading_key == last_heading_key and not body_since_heading:
                continue  # same title repeated (half title page, then chapter head)
            last_heading_key = heading_key
            if not body_since_heading and output:
                output.append(text)
                continue  # several headings in a row share one break
            body_since_heading = False
        else:
            body_since_heading = True
        if is_chapter and not args.no_chapter_breaks and output:
            chapter_count += 1
            output.append("\f")
        output.append(text)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write("\n\n".join(output) + "\n")

    print(f"Pages converted: {last - first}")
    print(f"Body font size: {body_size}")
    print(f"Running headers/footers detected: {sorted(k for k in running_keys if k) or 'none'}")
    print(f"Header/footer/page number lines removed: {removed_count}")
    print(f"Paragraphs: {len(output) - output.count(chr(12))}")
    print(f"Chapter breaks: {chapter_count}")
    if boilerplate_removed:
        print(f"Project Gutenberg boilerplate paragraphs removed: {boilerplate_removed}")
    if image_only_pages:
        print(f"Image only pages (no text layer): {image_only_pages}")
        if not args.ocr:
            print("Pass --ocr to OCR these pages.")
    if ocr_pages:
        print(f"OCR'd pages: {ocr_pages}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
