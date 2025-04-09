#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import itertools

import bs4
import requests
from PyPDF2 import PdfMerger, PdfReader


def scrape(html_body: str) -> list[str]:
    soup = bs4.BeautifulSoup(html_body, "html.parser")
    # base_url = "https://ambiente.regione.emilia-romagna.it/{}"
    page_docs = soup.find("div", id="page-document")
    if not page_docs:
        print("can't find #page-document")
        return []
    cards = page_docs.find_all("div", class_=["block", "listing", "simpleCard"])
    if not cards:
        print("can't find table")
        return []
    anchors = itertools.chain.from_iterable(map(lambda x: x.find_all("a"), cards))
    if anchors is None:
        print("can't find anchors")
        return []
    return [a.get("href") for a in anchors]


def download_book(urls: list[str]):
    def download(url):
        url = url.strip()
        res = requests.get(url)
        if not res.ok:
            return None
        return PdfReader(io.BytesIO(res.content))

    merger = PdfMerger()
    for url in urls:
        print("downloading ", url)
        pdf = download(url)
        print("download: ", "OK" if pdf else "FAILED")
        if pdf:
            merger.append(pdf)
    with open("book.pdf", "wb") as fout:
        merger.write(fout)


if __name__ == "__main__":
    # the site is built with react so no easy "get" using requests, coulnd't make selenium work
    # open the following link and save the html to the file "normativa.html"
    # "https://ambiente.regione.emilia-romagna.it/it/parchi-natura2000/sistema-regionale/GEV/la-formazione-delle-gev/normativa-gev"
    file = ""
    with open("normativa.html", "r") as f_in:
        file = f_in.read()
    urls = scrape(file)
    download_book(urls)
