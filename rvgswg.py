#!/usr/bin/env python3

import glob
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import shutil
import subprocess
import sys
import re
import datetime
import pathlib

from joblib import Parallel, delayed

DIR_ID = ".rvgswg"

CONFIG_SOURCE_DIR = "source"
CONFIG_DEST_DIR = "website"
CONFIG_SERVE_DIR = "website"
CONFIG_ORG2HTML_EXEC = "emacs_org2html"

CONFIG_HEADER_ORG_MODE = """#+AUTHOR: Romeu Vieira

#+OPTIONS: html-style:nil
#+OPTIONS: html-scripts:nil

#+OPTIONS: author:nil
#+OPTIONS: email:nil
#+OPTIONS: date:nil
#+OPTIONS: toc:nil

#+PROPERTY: header-args :eval no

#+HTML_HEAD: <link rel="stylesheet" type="text/css" href="/style.css"/>

"""

# Placeholders:
#   {{date}}
CONFIG_FOOTER_ORG_MODE = """
* FOOTER                                                                                              :ignore:
:PROPERTIES:
:clearpage: t
:END:
#+BEGIN_EXPORT html
<hr>
<footer>
  <div class="container">
    <ul class="menu-list">
      <li class="menu-list-item flex-basis-100-margin fit-content">
        <a href="/index.html" class="test">Home</a>
      </li>
      <li class="menu-list-item flex-basis-100-margin fit-content">
        <a href="/articles/articles.html">Articles</a>
      </li>
      <li class="menu-list-item flex-basis-100-margin fit-content">
        <a href="/writeups/htb/index.html">Write-Ups</a>
      </li>
      <li class="menu-list-item flex-basis-100-margin fit-content">
        <a class="inactive-link">{{date}}</a>
      </li>
    </ul>
  </div>
</footer>
#+END_EXPORT
"""


class Logger:

    @staticmethod
    def info(text: str):
        print(f"[INFO] - {text}")

    @staticmethod
    def error(text: str):
        print(f"[ERROR] - {text}")

    @staticmethod
    def critical(text: str):
        print(f"[CRIT] - {text}")


class LocalHTTPHandler(SimpleHTTPRequestHandler):
    """set serve directory"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=CONFIG_SERVE_DIR, **kwargs)


def get_current_date_ddmmyyyy() -> str:
    return datetime.datetime.today().strftime("%d-%m-%Y")


def get_file_text(file: str) -> str:
    file_handle = open(file)
    file_text = file_handle.read()
    file_handle.close()
    return file_text


def regex_get_date(file_text: str) -> str | None:
    regex = re.compile(r"\#\+DATE\:\s(\d{2}\-\d{2}\-\d{4})")
    matches = regex.search(file_text)
    if matches is not None:
        return matches.group(1)
    else:
        return None


def footer_set_date_impl(footer_text: str, date: str) -> str:
    return footer_text.replace("{{date}}", date)


def footer_set_date(file_text: str, footer_text: str) -> str:
    date: str | None = regex_get_date(file_text)
    if date is not None:
        # set date in org file
        return footer_set_date_impl(footer_text, date)
    else:
        # calculate current date
        return footer_set_date_impl(footer_text, get_current_date_ddmmyyyy())


def org_to_html(file: str):
    Logger.info(f"Converting {file} to HTML...")

    file_text = get_file_text(file)

    # add header
    with open(file, "r+") as f_object:
        lines = f_object.readlines()
        f_object.seek(0)
        f_object.write(CONFIG_HEADER_ORG_MODE)
        for line in lines:
            f_object.write(line)

    # add footer
    with open(file, "a") as f_object:
        footer = CONFIG_FOOTER_ORG_MODE
        footer = footer_set_date(file_text, footer)
        f_object.write(footer)

    # convert to html
    result = subprocess.run(
        [CONFIG_ORG2HTML_EXEC, file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    try:
        result.check_returncode()
    except:
        Logger.critical(f"org2html exited with error")


def help():
    print("""
            """)


def init():
    if os.path.exists(DIR_ID):
        Logger.info('Directory already identified.')
    else:
        # create .rvgswg file
        Logger.info(f"Creating {DIR_ID} file...")
        pathlib.Path(DIR_ID).touch()


def gen():
    # check if website dir already exists and delete item
    shutil.rmtree(CONFIG_DEST_DIR)

    # copy directory to new directory called `website`
    if (shutil.copytree(CONFIG_SOURCE_DIR, CONFIG_DEST_DIR, dirs_exist_ok=True)
            != CONFIG_DEST_DIR):
        Logger.critical(
            "Pasted directory does not correspond to the target directory, exiting..."
        )
        exit(1)

    # start finding org-mode files
    files_org = glob.glob("./website/**/*.org", recursive=True)
    # for each org file, execute org2html conversion
    Parallel(n_jobs=8)(delayed(org_to_html)(i) for i in files_org)


def clean():
    pass


def main():

    if len(sys.argv) != 2:
        Logger.info("Incorrect number of arguments")
        exit(1)

    arg = sys.argv[1]

    # check if website hidden file exists
    if not os.path.isfile(DIR_ID):
        if arg == "init":
            Logger.info("Directory is not valid, initializing...")
            init()
        else:
            Logger.info("Directory is not valid. Initialization required.")
            exit(1)
    else:
        if arg == "init":
            Logger.info("Directory already initialized.")
            exit(1)

        Logger.info(
            "This directory is now identified as a valid directory for rvgswg")

    # check if website source directory exists
    if not os.path.isdir(CONFIG_SOURCE_DIR):
        Logger.info("Website source directory does not exist!")
        exit(1)
    else:
        Logger.info("Website source directory detected!")

    # check if org-mode2html file exists
    org2htmlexe = shutil.which(CONFIG_ORG2HTML_EXEC)
    if org2htmlexe is None:
        Logger.info("The org2html file does not exist!")
        exit(1)
    else:
        Logger.info(f"org2html file detected: {org2htmlexe}")

    if arg == "run":
        Logger.info("Starting HTTP Server (http://localhost:8800/)...")
        HTTPServer(("localhost", 8800), LocalHTTPHandler).serve_forever()
    elif arg == "gen":
        gen()
    elif arg == "clean":
        clean()
    elif arg == "help":
        help()
    else:
        Logger.info("No valid argument was passed")
        exit(1)


if __name__ == "__main__":
    main()
