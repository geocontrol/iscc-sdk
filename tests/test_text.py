# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

import iscc_sdk as idk


def test_text_meta_extract_pdf(pdf_file):
    assert idk.text_meta_extract(pdf_file) == {"name": "title from metadata"}


def test_text_meta_extract_docx(docx_file):
    assert idk.text_meta_extract(docx_file) == {"creator": "titusz", "name": "title from metadata"}


def test_text_meta_extract_epub(epub_file):
    assert idk.text_meta_extract(epub_file) == {
        "name": "Children's Literature",
        "creator": "Charles Madison Curry, Erle Elsworth Clippinger",
        "rights": "Public domain in the USA.",
    }


def test_text_meta_embed_pdf(pdf_file):
    meta = {"name": "testname", "description": "testdescription"}
    new_file = idk.text_meta_embed(pdf_file, idk.IsccMeta(**meta))
    assert idk.text_meta_extract(new_file) == meta


def test_text_extract_pdf(pdf_file):
    text = idk.text_extract(pdf_file)
    assert text.strip().startswith("Bitcoin: A Peer-to-Peer Electronic Cash System")


def test_text_extract_empty(tmp_path):
    fp = tmp_path / "empty.txt"
    fp.write_text(" \n")
    with pytest.raises(idk.IsccExtractionError):
        idk.text_extract(fp)


def test_text_extract_docx(docx_file):
    text = idk.text_extract(docx_file)
    assert text.strip().startswith("ISCC Test Document")


def test_text_name_from_uri_str(jpg_file):
    assert idk.text_name_from_uri("http://example.com") == "example"
    assert idk.text_name_from_uri("http://example.com/some-file.txt") == "some file"
    assert idk.text_name_from_uri("http://example.com/some_file.txt?q=x") == "some file"
    assert idk.text_name_from_uri(jpg_file) == "img"


def test_text_name_from_uri_path(jpg_file):
    assert idk.text_name_from_uri(Path(jpg_file)) == "img"


def test_text_chunks(docx_file):
    txt = idk.text_extract(docx_file)
    chunks = list(idk.text_chunks(txt, avg_size=128))
    assert len(chunks) == 56
    assert "".join(chunks) == txt
    assert chunks[0] == (
        "ISCC Test Document\n"
        "\n"
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy "
        "eirmod tempor invid"
    )


def test_text_features(docx_file):
    txt = idk.text_extract(docx_file)
    features = idk.text_features(txt)
    assert features == {
        "maintype": "content",
        "offsets": [0, 997, 1454, 2123, 4942, 5399, 6068],
        "simprints": [
            "k5TpwXVE3j9N5IBxm36c4hkXP6fHOv8bkY2f68_8XSg",
            "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
            "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
            "lp6NgXnE_C1c6ij12-w04RwZN4XJyP0KgIrbKYX81yo",
            "OERRAF2u5WWuLHZLZzgcCSoCoL9R0NYrBJD7s7A43t0",
            "AARYEMzu5WEOfTZq5ixNLcoThJ5AgJYNRICysqEs3v0",
            "JfC6tnH1BuHFMviS2deReiUuelIIMvWWOozU6afjErU",
        ],
        "sizes": [997, 457, 669, 2819, 457, 669, 2],
        "subtype": "text",
        "version": 0,
    }


def test_text_features_stable(doc_file):
    expected = "j4Bo-QrY2phzOfDI2HMlm7t4kgipg5jRiSlIxBHD12I"

    # Robust changes: whitespace, case, control characters, marks (diacritics), and punctuation
    txt_a = "The ISCC is a similarity preserving fingerprint / identifier for digital media assets."
    txt_b = "The Iscc\n is a similärity preserving; fingerprint identifier for digital media assets"

    feat_a = idk.text_features(txt_a)["simprints"][0]
    feat_b = idk.text_features(txt_b)["simprints"][0]
    assert feat_a == expected
    assert feat_b == expected


def test_code_text_no_meta_extract(docx_file, monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "extract_metadata", False)
    meta = idk.code_text(docx_file)
    assert meta.dict() == {"characters": 4951, "iscc": "ISCC:EAAQMBEYQF6457DP"}
