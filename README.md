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
CONFIG_ORG2HTML_EXEC - Executable file for `org2html` conversion.
CONFIG_HEADER_ORG_MODE - Header to be added to the top of every org-mode file.
CONFIG_FOOTER_ORG_MODE - Footer to be added to the end of every org-mode file.
```

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
