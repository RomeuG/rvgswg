#!/usr/bin/env python3

import glob
import os
import shutil
import subprocess
import sys
import re
import datetime
import time
import pathlib
import json
import html

from contextlib import contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler
from joblib import Parallel, delayed

DIR_ID = ".rvgswg"

rvgswg_source_dir = ""
rvgswg_dest_dir = ""
rvgswg_serve_dir = ""
rvgswg_features = {}


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
        super().__init__(*args, directory=rvgswg_serve_dir, **kwargs)


@contextmanager
def open_with_error(filename: str, mode):
    try:
        f = open(filename, mode)
    except IOError as err:
        yield None, err
    else:
        try:
            yield f, None
        finally:
            f.close()


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
    with open_with_error(file, "r+") as (f_object, err):
        if err:
            pass
        elif f_object is not None:
            lines = f_object.readlines()
            f_object.seek(0)
            f_object.write(org_header)
            for line in lines:
                f_object.write(line)

    # add footer
    with open_with_error(file, "a") as (f_object, err):
        if err:
            pass
        elif f_object is not None:
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
    except subprocess.CalledProcessError as e:
        Logger.critical(f"{org_binary} exited with error: {e.returncode}")


def feature_articles(feature: str):
    Logger.info(f"Executing feature: {feature}")

    main_html: str = ""
    dest_file = ""
    body_placeholder = ""

    with open_with_error("features/articles.json", "r") as (f_object, err):
        if err:
            pass
        elif f_object is not None:
            data_list = json.load(f_object)
            for data in data_list:
                article_list = []

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
                with open_with_error(dest_file, "w") as (f_object, err):
                    if err:
                        pass
                    elif f_object is not None:
                        f_object.write(finished_html)


def feature_orgmode(feature: str):
    Logger.info(f"Executing feature: {feature}")

    org2html_binary = ""
    org2html_header = ""
    org2html_footer = ""

    with open_with_error("features/orgmode.json", "r") as (f_object, err):
        if err:
            pass
        elif f_object is not None:
            data = json.load(f_object)
            org2html_binary = data["binary"]
            org2html_header = data["header"]
            org2html_footer = data["footer"]

    # verify if binary actually exists
    org2htmlexe = shutil.which(org2html_binary)
    if org2htmlexe is None:
        Logger.info("The org2html file does not exist!")
        Logger.info(f"Skipping {feature} feature...")
        pass
    else:
        Logger.info(f"org2html file detected: {org2htmlexe}")

    # start finding org-mode files
    files_org = glob.glob("./website/**/*.org", recursive=True)
    # for each org file, execute org2html conversion
    Parallel(n_jobs=4)(delayed(org_to_html)(i, org2html_header,
                                            org2html_footer, org2html_binary)
                       for i in files_org)


def feature_rss(feature: str):
    Logger.info(f"Executing feature: {feature}")

    if rvgswg_features["articles"] is False:
        Logger.error(
            "RSS feature couldn't execute because Articles feature is not enabled"
        )
        pass

    rss_file = ""
    rss_body = ""
    rss_item_body = ""
    rss_articles_list = []

    with open_with_error("features/rss.json", "r") as (f_object, err):
        if err is None and f_object is not None:
            rss_data = json.load(f_object)
            rss_file = rss_data["rss_file"]
            rss_body = rss_data["rss_body"]
            rss_item_body = rss_data["rss_item_body"]

    with open_with_error("features/articles.json", "r") as (f_object, err):
        if err is None and f_object is not None:
            articles_data_list = json.load(f_object)
            for articles_data in articles_data_list:
                articles = articles_data["articles"]
                for article in articles:
                    title = html.escape(article["title"])
                    url = html.escape(article["url"])
                    description = html.escape(article["description"])
                    date = article["date"]

                    rss_article_body = rss_item_body.replace(
                        "{{title}}",
                        title).replace("{{url}}",
                                       url).replace("{{description}}",
                                                    description)
                    rss_articles_list.append((rss_article_body, date))

    rss_articles_list.sort(
        key=lambda article: time.strptime(article[1], "%d-%m-%Y"))

    reversed_list = reversed(rss_articles_list)

    articles_texts = map(lambda article: article[0], reversed_list)
    full_body_string = "\n".join(articles_texts)
    full_xml_string = rss_body.replace("{{body}}", full_body_string)

    with open_with_error(rss_file, "w") as (f_object, err):
        if err is None and f_object is not None:
            f_object.write(full_xml_string)


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
    try:
        shutil.rmtree(rvgswg_dest_dir)
    except:
        Logger.info("Not removing output directory because it does not exist")

    try:
        os.mkdir(rvgswg_dest_dir)
    except FileExistsError as error:
        Logger.info(f"Output directory already exists: {error}")

    # copy directory to new directory called `website`
    if (shutil.copytree(rvgswg_source_dir, rvgswg_dest_dir, dirs_exist_ok=True)
            != rvgswg_dest_dir):
        Logger.critical(
            "Pasted directory does not correspond to the target directory, exiting..."
        )
        exit(1)

    # start executing features
    for feature, enabled in rvgswg_features.items():
        Logger.info(f"Featured {feature} is enabled: {enabled}")

        if feature == "articles":
            feature_articles(feature)

        if feature == "orgmode":
            feature_orgmode(feature)

        if feature == "rss":
            feature_rss(feature)


def clean():
    shutil.rmtree(rvgswg_dest_dir)


def json_get_value(fn, key: str):
    try:
        result = fn()
        if result == "":
            raise Exception
        else:
            return result
    except:
        Logger.critical(
            f"Required JSON key {key} has no value or does not exist.")
        exit(1)


def main():

    global rvgswg_source_dir
    global rvgswg_dest_dir
    global rvgswg_serve_dir
    global rvgswg_features

    if len(sys.argv) != 2:
        Logger.info("Incorrect number of arguments\n")
        help()
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

    # get all information needed, exit on error
    with open_with_error(DIR_ID, "r") as (f_object, err):
        if err is None and f_object is not None:
            project_data = json.load(f_object)

            rvgswg_source_dir = json_get_value(
                lambda: project_data["website_source"], "website_source")
            rvgswg_dest_dir = json_get_value(
                lambda: project_data["website_output"], "website_output")
            rvgswg_serve_dir = json_get_value(
                lambda: project_data["website_serve"], "website_serve")

            features_data = json_get_value(lambda: project_data["features"],
                                           "features")

            rvgswg_features["orgmode"] = json_get_value(
                lambda: features_data["orgmode"], "orgmode")
            rvgswg_features["articles"] = json_get_value(
                lambda: features_data["articles"], "articles")
            rvgswg_features["rss"] = json_get_value(
                lambda: features_data["rss"], "rss")

    # check if website source directory exists
    if not os.path.isdir(rvgswg_source_dir):
        Logger.info("Website source directory does not exist!")
        exit(1)
    else:
        Logger.info("Website source directory detected!")

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
