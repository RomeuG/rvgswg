# Rvgswg

A static website generator for my website. This is a very specific setup, using my own
[Emacs Configuration](https://github.com/RomeuG/.emacs.d), my own Org-Mode configuration
and my own Emacs `org2html` script, therefore, **this won't probably suit your needs**.

# Usage

```
$ ./rvgswg.py help

Arguments:

run - Create HTTP server.
gen - Generate website.
clean - Clean output.
help - Prints this info.
```

## Configuration

Configuration is done through constants in the `rvgswg.py` file:

```
CONFIG_SOURCE_DIR - Source directory of the website.
CONFIG_DEST_DIR - Destination of the website files after generation.
CONFIG_SERVE_DIR - Serve directory for the `run` command.
```

The hidden file that identifies the directory (`.rvgswg`) is also home to the general
configuration of this static website generator. The following is a configuration example:

```json
{
    "website_source": "source",
    "website_output": "website",
    "website_serve": "website",
    "features": {
        "articles": true,
        "rss": true,
        "orgmode": true
    }
}
```

Its attributes are:

- `website_source` - Website source code directory.
- `website_output` - Website output directory.
- `website_serve` - Directory that will be used by the HTTP server.

The `features` key is another JSON object whose keys are the features (`articles`, `rss`, `orgmode`) and the values are
the current state: enabled or disabled.

# Features

## Article HTML Generation

To automatically generate an `articles` page (`index.html`), the file
`features/articles.json` needs to exist with this format:

```json
{
  "main_html": "<html>{{body}}</html>",
  "body_placeholder": "{{body}}",
  "dest_file": "website/articles/index.html",
  "articles": [
    {
      "directory": "website/articles/org-mode-mathjax/org-mode-mathjax.html",
      "url": "../articles/org-mode-mathjax/org-mode-mathjax.html",
      "title": "Org-Mode & MathJax",
      "date": "30-05-2021"
    }
  ]
}
```

Main object has four different keys:

- `main_html` - Result file HTML, with its placeholder included.
- `body_placeholder` - the format of the placeholder for the `replace` function.
- `dest_file` - Destination file path.
- `articles` - JSON Array of articles.

The article object has four different attributes:

- `directory` - File path of the article.
- `url` - The article URL for the `<a>` tag.
- `title` - Title for the paragraph tag.
- `date` - Date of the article.

## RSS Feed Generation

This feature depends on the article generation feature because it uses the article
references to build the RSS feed. To make this feature work, the file `features/rss.json`
should exist with a structure similar to the following example:

```json
{
  "rss_file": "website/rss.xml",
  "rss_body": "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<rss version=\"2.0\">\n<channel>\n{{body}}\n</channel>\n</rss>",
  "rss_item_body": "<item>\n\t<title>{{title}}</title>\n\t<link>{{url}}</link>\n\t<description>{{description}}</description>\n</item>\n"
}
```

The structure attributes are:

- `rss_file` - The XML file location.
- `rss_body` - RSS file main body.
- `rss_item_body` - Each items' structure.

## Org-Mode to HTML

This feature finds Org-Mode files and converts them to HTML using a script provided by the
user (or the script that is included in this repository in the `scripts` folder). The
configuration is done through the `features/orgmode.json` file, which has the following
structure:

```json
{
  "binary": "emacs_org2html",
  "header": "#+AUTHOR: Romeu Vieira\n\n#+OPTIONS: html-style:nil\n#+OPTIONS: html-scripts:nil\n\n#+OPTIONS: author:nil\n#+OPTIONS: email:nil\n#+OPTIONS: date:nil\n#+OPTIONS: toc:nil\n\n#+PROPERTY: header-args :eval no\n\n#+HTML_HEAD: <link rel=\"stylesheet\" type=\"text/css\" href=\"/style.css\"/>\n\n",
  "footer": "\n* FOOTER                                                                                              :ignore:\n:PROPERTIES:\n:clearpage: t\n:END:\n#+BEGIN_EXPORT html\n<hr>\n<footer>\n<div class=\"container\">\n<ul class=\"menu-list\">\n<li class=\"menu-list-item flex-basis-100-margin fit-content\">\n<a href=\"/index.html\" class=\"test\">Home</a>\n</li>\n<li class=\"menu-list-item flex-basis-100-margin fit-content\">\n<a href=\"/articles/articles.html\">Articles</a>\n</li>\n<li class=\"menu-list-item flex-basis-100-margin fit-content\">\n<a href=\"/writeups/htb/index.html\">Write-Ups</a>\n</li>\n<li class=\"menu-list-item flex-basis-100-margin fit-content\">\n<a class=\"inactive-link\">{{date}}</a>\n</li>\n</ul>\n</div>\n</footer>\n#+END_EXPORT"
}
```

The structure has the following attributes:

- `binary` - The executable file to be used that operates on each org-mode file to convert to HTML.
- `header` - Org-mode formatted contents to be inserted before the org-mode file contents.
- `footer` - Org-mode formatted contents to be inserted after the org-mode file contents.

# License

Copyright 2022 Romeu Gomes

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
