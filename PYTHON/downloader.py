#!/usr/bin/env python

from bs4 import BeautifulSoup
from fpdf import FPDF
import os
from PIL import Image
import re
import requests

from externals.pynet import pynet as net

downloader = net.NetHandler()
RE_JPG = re.compile(r'[\s|\S]*.jpg')
DEST = "Downloads"
URL_BASE = "http://www.mangareader.net"


def create_if_not_exists(dir):
    if not os.path.exists(dir):  # check for an existing path
        os.mkdir(dir)  # make directory if it doesn't exist
    else:
        net.m_aviso("Path '%s' already exists" % dir)


def get_html(url):
    """
    Gets html text for the given url
    """
    response = requests.get(url)
    return response.text  # Converts the response into text and return it


def download_chapter(manga, chapter):
    path_chap = "%s/%s/%s" % (DEST, manga, chapter)
    url = "%s/%s/%s" % (URL_BASE, manga, str(chapter))
    html = get_html(url)  # HTML page of the url

    if "not released yet" in html:  # Checks for this string
        net.m_aviso("Chapter " + str(chapter) + " of " + manga + " is not available at www.mangareader.net")
        return -1
    create_if_not_exists(path_chap)
    i = 1
    while True:  # an infinte while loop
        try:
            net.m_aviso("Downloading page %s of chapter %s ....." % (str(i), str(chapter)))
            url = "http://www.mangareader.net/" + \
                  manga + "/" + str(chapter) + "/" + str(i)
            html = get_html(url)  # HTML page of the url
            # Parses the html with lxml parser
            soup = BeautifulSoup(html, "lxml")
            # Selects the suitable image tag with the link
            ans = soup.select("#imgholder img")
            img_link = ans[0]['src']  # Gets the image url
            imagename = "0000%s.jpg" % str(i)
            image_path = "%s/%s" % (path_chap, imagename)
            downloader.download_file(img_link, image_path)
            i += 1
        except:
            break
    return 0


def get_images_from_folder(folder_path):
    files = os.walk(folder_path).next()[2]
    return filter(RE_JPG.match, files)


def convert_to_pdf(image_folder_path, pdf_path):

    print image_folder_path
    print pdf_path
    images = get_images_from_folder(image_folder_path)
    cover = Image.open("%s/%s" % (image_folder_path, images[0]))
    width, height = cover.size

    pdf = FPDF(unit="pt", format=[width, height])

    for page in images:
        pdf.add_page()
        page_path = "%s/%s" % (image_folder_path, page)
        pdf.image(page_path, 0, 0)

    pdf.output(pdf_path, "F")


if __name__ == "__main__":
    create_if_not_exists(DEST)
    manga = raw_input("Enter Manga name : ")
    manga = manga.strip()  # Remove extra whitespaces from the start and end of the string
    manga = manga.lower()  # Change the manga name into lowercase
    # Replace the whitespaces with a hyphen (-)
    manga = manga.replace(' ', '-')
    print "Enter the chapter range :"
    chaps = input("Start : ")
    chape = input("End : ")

    path_manga = "%s/%s" % (DEST, manga)
    create_if_not_exists(path_manga)

    for chap in range(chaps, chape+1):
        value = download_chapter(manga, chap)
        if value == -1:
            break

        net.m_accion("Converting to pdf...")
        chapno = "0000"+str(chap)
        chapno = chapno[len(chapno) - 4:]
        pdf_name = "chap"+chapno+".pdf"
        path_chap = "%s/%s" % (path_manga, chap)
        path_pdf = "%s/%s" % (path_chap, pdf_name)
        convert_to_pdf(path_chap, path_pdf)
        net.m_aviso("Your downloaded file is in this path:\n %s" % path_pdf)
