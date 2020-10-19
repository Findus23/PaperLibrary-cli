import hashlib
import os
import shutil
import string
from datetime import datetime
from pathlib import Path

from tzlocal import get_localzone

from paperlibrary.api import PaperLibraryAPI
from paperlibrary.config import basedir


def format_filename(s: str) -> str:
    additional_letters = ["ä", "Ä", "ö", "Ö", "ü", "Ü"]
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}{''.join(additional_letters)}"
    filename = ''.join(c for c in s if c in valid_chars)
    # filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename


def write_symlinks(api: PaperLibraryAPI):
    ...
    pdf_dir = basedir / "pdfs"
    author_dir = basedir / "by_author"
    shutil.rmtree(author_dir, ignore_errors=True)
    author_dir.mkdir()

    for author in api.fetch_authors():
        author_subdir = author_dir / format_filename(author.name)
        author_subdir.mkdir()
        for paper in author.papers:
            sourcefile = pdf_dir / f"{paper.main_pdf.id}.pdf"
            targetfile = author_subdir / "{}.pdf".format(format_filename(paper.title))
            targetfile.symlink_to(sourcefile)


def download_file(api: PaperLibraryAPI, url: str, target_file: Path):
    r = api.s.get(url)
    r.raise_for_status()
    with target_file.open("wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)


def hash_file(file: Path, buffer_size=65536) -> str:
    sha265 = hashlib.sha256()
    with file.open("rb") as f:
        while True:
            data = f.read(buffer_size)
            if not data:
                break
            sha265.update(data)
    return sha265.hexdigest()


def update_pdfs(api: PaperLibraryAPI):
    pdf_dir = basedir / "pdfs"
    pdf_dir.mkdir(exist_ok=True)

    for pdf in api.fetch_pdfs():
        pdf_file = pdf_dir / f"{pdf.id}.pdf"
        if not pdf_file.exists():
            download_file(api, pdf.file, pdf_file)
            continue
        if hash_file(pdf_file) != pdf.sha265:
            modification_date = datetime.fromtimestamp(
                os.path.getmtime(pdf_file),
                get_localzone()
            )
            print(modification_date)
            print(pdf.updated_at)
            # print(modification_date - pdf.updated_at)
            if modification_date > pdf.updated_at:
                raise ValueError("local file is newer")
            else:
                raise ValueError("remote file is newer")
            # TODO: check if file should be uploaded or downloaded
