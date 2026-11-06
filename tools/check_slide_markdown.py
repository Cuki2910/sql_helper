import html
import re
import zipfile
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree


SLIDES = Path(__file__).resolve().parents[1] / "slides"
PDF_PAGES = {"M3-Part 7 - Insert, Delete, Update.pdf": 20}
NAMESPACES = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def compact(text):
    return re.sub(r"\s+", "", html.unescape(text).replace("\u200b", ""))


def main():
    sources = sorted([*SLIDES.glob("*.pptx"), *SLIDES.glob("*.pdf")])
    assert len(sources) == 5, f"Expected 5 sources, found {len(sources)}"
    total = 0
    for source in sources:
        markdown = source.with_suffix(".md")
        text = markdown.read_text()
        assert len(re.findall(r"^```", text, re.MULTILINE)) % 2 == 0, markdown.name
        for target in re.findall(r"\]\(<?([^\n)]+?)>?\)", text):
            if target.startswith("#"):
                assert f'id="{target[1:]}"' in text, (markdown.name, target)
            else:
                assert (SLIDES / unquote(target)).is_file(), (markdown.name, target)
        if source.suffix == ".pptx":
            with zipfile.ZipFile(source) as archive:
                slides = [name for name in archive.namelist()
                          if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
                expected = len(slides)
                readable = compact(re.sub(r"^```.*$", "", text, flags=re.MULTILINE))
                for name in slides:
                    root = ElementTree.fromstring(archive.read(name))
                    for paragraph in root.findall(".//a:p", NAMESPACES):
                        native = "".join(node.text or "" for node in paragraph.findall(".//a:t", NAMESPACES))
                        assert not native.strip() or compact(native) in readable, (
                            markdown.name, name, native)
        else:
            expected = PDF_PAGES[source.name]
        unit = "Slide" if source.suffix == ".pptx" else "Trang"
        headings = re.findall(rf"^## {unit} (\d+):", text, re.MULTILINE)
        assert [int(number) for number in headings] == list(range(1, expected + 1)), markdown.name
        total += expected
        print(f"OK {markdown.name}: {expected} sections; links and code fences valid")
    assert total == 84, total
    print(f"PASS: {len(sources)} documents, {total} slides/pages; all native PPTX text retained")


if __name__ == "__main__":
    main()
