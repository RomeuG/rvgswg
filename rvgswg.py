#!/usr/bin/env python3

import glob
import os
import shutil
import subprocess
import sys
import re
import datetime
import pathlib
import json

from http.server import HTTPServer, SimpleHTTPRequestHandler
from joblib import Parallel, delayed

DIR_ID = ".rvgswg"

CONFIG_SOURCE_DIR = "source"
CONFIG_DEST_DIR = "website"
CONFIG_SERVE_DIR = "website"
CONFIG_ORG2HTML_EXEC = "emacs_org2html"

FEATURES_CONFIG = {
    "articles": True,
    "orgmode": True,
}


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


def org_to_html(file: str, org_header: str, org_footer: str, org_binary: str):
    Logger.info(f"Converting {file} to HTML...")

    file_text = get_file_text(file)

    # add header
    with open(file, "r+") as f_object:
        lines = f_object.readlines()
        f_object.seek(0)
        f_object.write(org_header)
        for line in lines:
            f_object.write(line)

    # add footer
    with open(file, "a") as f_object:
        footer = org_footer
        footer = footer_set_date(file_text, footer)
        f_object.write(footer)

    # convert to html
    result = subprocess.run(
        [org_binary, file],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )

    try:
        result.check_returncode()
    except:
        Logger.critical(f"org2html exited with error")


def feature_articles(feature: str):
    Logger.info(f"Executing feature: {feature}")

    article_list = []

    main_html: str = ""
    dest_file = ""
    body_placeholder = ""

    with open("features/articles.json", "r") as f_object:
        data = json.load(f_object)
        body_placeholder = data["body_placeholder"]
        articles = data["articles"]
        dest_file = data["dest_file"]
        main_html = data["main_html"]
        output: str = data["output"]
        for article in articles:
            title = article["title"]
            url = article["url"]
            date = article["date"]
            html_final = output.replace("{{date}}", date).replace(
                "{{url}}", url).replace("{{title}}", title)
            article_list.append(html_final)

    body = "\n".join(article_list)
    finished_html = main_html.replace(body_placeholder, body)
    with open(dest_file, "w") as f_object:
        f_object.write(finished_html)


def feature_orgmode(feature: str):
    Logger.info(f"Executing feature: {feature}")

    org2html_binary = ""
    org2html_header = ""
    org2html_footer = ""

    with open("features/orgmode.json", "r") as f_object:
        data = json.load(f_object)
        org2html_binary = data["binary"]
        org2html_header = data["header"]
        org2html_footer = data["footer"]

    # start finding org-mode files
    files_org = glob.glob("./website/**/*.org", recursive=True)
    # for each org file, execute org2html conversion
    Parallel(n_jobs=4)(delayed(org_to_html)(i, org2html_header,
                                            org2html_footer, org2html_binary)
                       for i in files_org)


def help():
    print("""Arguments:

run - Create HTTP server.
gen - Generate website.
clean - Clean output.
help - Prints this info.""")


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

    # start executing features
    for feature, enabled in FEATURES_CONFIG.items():
        Logger.info(f"Featured {feature} is enabled: {enabled}")

        if feature == "articles":
            feature_articles(feature)

        if feature == "orgmode":
            feature_orgmode(feature)


def clean():
    pass


def main():

    if len(sys.argv) != 2:
        Logger.info("Incorrect number of arguments")
        exit(1)

    arg = sys.argv[1]

    if arg == "help":
        help()
        exit(1)

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
    else:
        Logger.info("No valid argument was passed")
        exit(1)


if __name__ == "__main__":
    main()
