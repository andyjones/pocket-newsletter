#!/usr/bin/env python

import os
from datetime import datetime, timedelta
from math import ceil

from jinja2 import Template
from pockyt.auth import Authenticator
from pocket import Pocket


def estimate_reading_time(n_words):
    words_per_minute = 200
    return ceil(n_words / words_per_minute)


def render_template(template, **context):
    with open(template) as fh:
        t = Template(fh.read())
        return t.render(**context)


def main():
    week_ago = datetime.utcnow() - timedelta(days=7)

    auth = Authenticator({})
    if not os.path.isfile(auth._config_path):
        auth.setup()

    auth.load()

    pocket = Pocket(auth.credentials["consumer_key"], auth.credentials["access_token"])
    resp, _headers = pocket.get(since=week_ago.timestamp())

    articles = [article for article in resp.get("list", {}).values()]
    for article in articles:
        if "word_count" in article:
            article["estimated_reading_time"] = estimate_reading_time(
                int(article["word_count"])
            )
    now = datetime.today()

    issue = {
        "number": 4,
        "title": "Tech Whimsies",
        "subtitle": "CentOS commits suicide?",
        "date": now.isoformat(),
        "human_date": now.strftime("%A, %B %d, %Y"),
        "articles": articles,
    }

    print(render_template("newsletter.md.j2", issue=issue))


if __name__ == "__main__":
    main()
