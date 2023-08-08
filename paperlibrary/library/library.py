import hashlib
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from alive_progress import alive_bar
from tzlocal import get_localzone

from paperlibrary.api import PaperLibraryAPI
from paperlibrary.api.models import Paper
from paperlibrary.config import Config


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

    notes_dir = pdf_dir.parent / "notes"
    notes_file = notes_dir / f"{paper.id}.md"
    meta_dir = pdf_dir.parent / "meta"
    meta_file = meta_dir / f"{paper.id}.json"
    sourcefile = pdf_dir / f"{paper.main_pdf.id}.pdf"
    targetfile = directory / "{}.pdf".format(format_filename(filename))
    targetfile.symlink_to(sourcefile)
    targetfile.with_suffix(".md").symlink_to(notes_file)
    targetfile.with_suffix(".json").symlink_to(meta_file)


def write_symlinks(api: PaperLibraryAPI, config: Config):
    basedir = config.basedir_path
    pdf_dir = basedir / "pdfs"
    pdf_dir.mkdir(exist_ok=True)

    author_dir = basedir / "by_author"
    keyword_dir = basedir / "by_keyword"
    year_dir = basedir / "by_year"
    tags_dir = basedir / "by_tags"
    title_dir = basedir / "by_title"
    custom_title_dir = basedir / "by_custom_title"
    citation_key_dir = basedir / "by_citation_key"

    tags = set()

    for directory in [author_dir, keyword_dir, year_dir, title_dir, tags_dir, custom_title_dir, citation_key_dir]:
        shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir()

    for author in api.fetch_authors():
        if not author.papers:
            continue
        author_subdir = author_dir / format_filename(author.display_name)
        author_subdir.mkdir()
        for paper in author.papers:
            link_file(pdf_dir, author_subdir, paper)

    for keyword in api.fetch_keywords():
        if not keyword.papers:
            continue
        keyword_subdir = keyword_dir / format_filename(keyword.name)
        keyword_subdir.mkdir(exist_ok=True)
        for paper in keyword.papers:
            link_file(pdf_dir, keyword_subdir, paper)

    for paper in api.fetch_papers():
        link_file(pdf_dir, title_dir, paper, paper.title)
        for tag in paper.tags:
            tag_dir = tags_dir / tag
            tag_dir.mkdir(exist_ok=True, parents=True)
            link_file(pdf_dir, tag_dir, paper, paper.title)
            tags.add(tag)

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

    for tag in tags:
        write_bibliography(api, config, tag)


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


def update_pdfs(api: PaperLibraryAPI, config: Config):
    pdf_dir = config.basedir_path / "pdfs"
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


def update_meta(api: PaperLibraryAPI, config: Config):
    meta_dir = config.basedir_path / "meta"
    meta_dir.mkdir(exist_ok=True)
    for paper in api.fetch_papers():
        with (meta_dir / f"{paper.id}.json").open("w") as f:
            f.write(paper.to_json(indent=2, ensure_ascii=False))


def update_notes(api: PaperLibraryAPI, config: Config):
    notes_dir = config.basedir_path / "notes"
    notes_dir.mkdir(exist_ok=True)

    for paper in api.fetch_papers():
        if paper.notes_md is None:
            paper.notes_md = ""
        notes_file = notes_dir / f"{paper.id}.md"
        if not notes_file.exists():
            notes_file.write_text(paper.notes_md)
            continue

        file_text = notes_file.read_text()
        if file_text == paper.notes_md:
            continue
        print(repr(file_text), repr(paper.notes_md))
        if paper.notes_updated_at is None:
            api.create_note(paper.id, file_text)
            continue
        online_change_date = datetime.fromisoformat(paper.notes_updated_at)
        local_change_date = datetime.fromtimestamp(notes_file.stat().st_mtime, tz=timezone.utc)
        print(online_change_date, local_change_date)
        print(local_change_date - online_change_date)
        if online_change_date > local_change_date:
            print("fetching from online")
            notes_file.write_text(paper.notes_md)
            continue
        print("updating online")
        api.update_note(paper.id, file_text)


def write_bibliography(api: PaperLibraryAPI, config: Config, tag: str = None):
    tags_dir = config.basedir_path / "by_tags"
    if tag:
        dir = tags_dir / tag
    else:
        dir = config.basedir_path
    bib = api.fetch_bibliography(tag)
    target_file = dir / "bibliography.bib"
    if target_file.exists():
        target_file.chmod(0o644)
    with target_file.open("w") as f:
        f.write(bib)
    target_file.chmod(0o444)

