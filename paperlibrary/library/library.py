import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path

from alive_progress import alive_bar
from tzlocal import get_localzone

from paperlibrary.api import PaperLibraryAPI
from paperlibrary.api.models import Paper
from paperlibrary.config import basedir


def format_filename(s: str) -> str:
    invalid_chars = {"/"}
    filename = ''.join(c for c in s if c not in invalid_chars)
    # filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    if not filename:
        raise ValueError("empty filename")
    return filename


def link_file(pdf_dir: Path, directory: Path, paper: Paper, filename: str = None) -> None:
    if not paper.main_pdf:
        return
    if filename is None:
        filename = paper.title

    sourcefile = pdf_dir / f"{paper.main_pdf.id}.pdf"
    targetfile = directory / "{}.pdf".format(format_filename(filename))
    targetfile.symlink_to(sourcefile)


def write_symlinks(api: PaperLibraryAPI):
    ...
    pdf_dir = basedir / "pdfs"
    pdf_dir.mkdir(exist_ok=True)

    author_dir = basedir / "by_author"
    keyword_dir = basedir / "by_keyword"
    year_dir = basedir / "by_year"
    title_dir = basedir / "by_title"
    custom_title_dir = basedir / "by_custom_title"
    citation_key_dir = basedir / "by_citation_key"

    for directory in [author_dir, keyword_dir, year_dir, title_dir, custom_title_dir, citation_key_dir]:
        shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir()

    for author in api.fetch_authors():
        author_subdir = author_dir / format_filename(author.display_name)
        author_subdir.mkdir()
        for paper in author.papers:
            link_file(pdf_dir, author_subdir, paper)

    for keyword in api.fetch_keywords():
        keyword_subdir = keyword_dir / format_filename(keyword.name)
        keyword_subdir.mkdir()
        for paper in keyword.papers:
            link_file(pdf_dir, keyword_subdir, paper)

    for paper in api.fetch_papers():
        link_file(pdf_dir, title_dir, paper, paper.title)

        if not paper.custom_title:
            continue
        link_file(pdf_dir, custom_title_dir, paper, paper.custom_title)

        if not paper.custom_title:
            continue
        link_file(pdf_dir, citation_key_dir, paper, paper.citation_key)

    for year, papers in api.fetch_papers_by_year().items():
        year_subdir = year_dir / str(year)
        year_subdir.mkdir()
        for paper in papers:
            link_file(pdf_dir, year_subdir, paper)


def download_file(api: PaperLibraryAPI, url: str, target_file: Path):
    r = api.s.get(url)
    r.raise_for_status()
    with alive_bar(int(r.headers["Content-Length"])) as bar:
        with target_file.open("wb") as f:
            for chunk in r.iter_content(1024):
                for _ in range(1024):
                    bar()
                f.write(chunk)


def hash_file(file: Path, buffer_size=65536) -> str:
    sha256 = hashlib.sha256()
    with file.open("rb") as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def update_pdfs(api: PaperLibraryAPI):
    pdf_dir = basedir / "pdfs"
    pdf_dir.mkdir(exist_ok=True)

    for pdf in api.fetch_pdfs():
        pdf_file = pdf_dir / f"{pdf.id}.pdf"
        if not pdf_file.exists():
            download_file(api, pdf.file, pdf_file)
            continue
        if hash_file(pdf_file) != pdf.sha256:
            modification_date = datetime.fromtimestamp(
                os.path.getmtime(pdf_file),
                get_localzone()
            )
            if modification_date > pdf.updated_at:
                print("local file is newer")
                api.upload_pdf(pdf, pdf_file)
            else:
                print("remote file is newer")
                download_file(api, pdf.file, pdf_file)


def write_bibliography(api: PaperLibraryAPI):
    bib = api.fetch_bibliography()
    target_file = basedir / "bibliography.bib"
    with target_file.open("w") as f:
        f.write(bib)
