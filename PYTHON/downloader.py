#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import os
import shutil

from externals.pynet import pynet as net

downloader = net.NetHandler()
dest = "Downloads"


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

if __name__ == "__main__":
    create_if_not_exists(dest)
    manga = raw_input("Enter Manga name : ")
    manga = manga.strip()  # Remove extra whitespaces from the start and end of the string
    manga = manga.lower()  # Change the manga name into lowercase
    # Replace the whitespaces with a hyphen (-)
    manga = manga.replace(' ', '-')
    print "Enter the chapter range :"
    chaps = input("Start : ")
    chape = input("End : ")

    path_manga = "%s/%s" % (dest, manga)
    create_if_not_exists(path_manga)

    for chap in range(chaps, chape+1):
        path_chap = "%s/%s" % (path_manga, chap)
        url = "http://www.mangareader.net/%s/%s"%(manga, str(chap))
        html = get_html(url)  # HTML page of the url

        if "not released yet" in html:  # Checks for this string
            net.m_aviso("Chapter "+str(chap)+" of "+manga+" is not available at www.mangareader.net")
            break
        create_if_not_exists(path_chap)
        i = 1
        while True:  # an infinte while loop
            try:
                net.m_aviso("Downloading page %s of chapter %s ....." % (str(i), str(chap)))
                url = "http://www.mangareader.net/" + \
                    manga+"/"+str(chap)+"/"+str(i)
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

        net.m_accion("Converting to pdf...")
        chapno = "0000"+str(chap)
        chapno = chapno[len(chapno) - 4:]
        pdf_name = "chap"+chapno+".pdf"
        path_pdf = "%s/%s" % (path_chap, pdf_name)
        pdf_command = "convert %s/*.jpg %s" % (path_chap, path_pdf)
        os.system(pdf_command)
        net.m_aviso("Cleaning up.....")
        path = os.getcwd()
        net.m_aviso("Your downloaded file is in this path:\n %s" % path_pdf)
        open_command = "gnome-open %s" % path_pdf
        os.system(open_command)
