#!/usr/bin/env python

import os
from datetime import datetime, timedelta
from math import ceil
from functools import cached_property

import click
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


class PocketClient:
    @cached_property
    def _client(self):
        auth = Authenticator({})
        if not os.path.isfile(auth._config_path):
            auth.setup()

        auth.load()

        return Pocket(
            auth.credentials["consumer_key"], auth.credentials["access_token"]
        )

    def articles(self, **query):
        delta = query.get("since")
        if delta:
            since = datetime.utcnow() - timedelta(**delta)
            query["since"] = since.timestamp()
        resp, _headers = self._client.get(**query)

        articles = [article for article in resp.get("list", {}).values()]
        for article in resp.get("list", {}).values():
            word_count = article.get("word_count")
            if word_count:
                article["estimated_reading_time"] = estimate_reading_time(
                    int(word_count)
                )

            yield article

    def add(self, url):
        resp, _headers = self._client.add(url)
        return resp

    def archive(self, article):
        resp, _headers = self._client.archive(article["item_id"], wait=False)
        return resp


from urllib.parse import urlparse, parse_qs
import requests


class HackerNewsClient:
    def from_url(self, url):
        o = urlparse(url)
        qs = parse_qs(o.query)
        item_id = qs.get("id")
        return self.from_id(item_id[0])

    def from_id(self, item_id):
        resp = requests.get(f"https://hn.algolia.com/api/v1/items/{item_id}")
        if resp.status_code == requests.codes.not_found:
            return None

        resp.raise_for_status()
        return resp.json()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(newsletter)


@cli.command()
def resolve_hacker_news():
    pocket = PocketClient()
    hn = HackerNewsClient()

    for article in pocket.articles(since={"days": 7}, domain="news.ycombinator.com"):
        item = hn.from_url(article["resolved_url"])
        click.echo(
            f"{article['item_id']}: replacing {article['resolved_url']} with {item['url']}"
        )
        pocket.add(url=item["url"])
        click.secho(f"\tadded {item['url']}", fg="green")
        pocket.archive(article)
        click.secho(f"\tarchived {article['resolved_url']}", fg="green")


@cli.command()
@click.option("--number", "issue_number", default=4)
def newsletter(issue_number):
    pocket = PocketClient()
    articles = [a for a in pocket.articles(since={"days": 7})]

    now = datetime.today()

    issue = {
        "number": issue_number,
        "title": "Tech Whimsies",
        "subtitle": "CentOS commits suicide?",
        "date": now.isoformat(),
        "human_date": now.strftime("%A, %B %d, %Y"),
        "articles": articles,
    }

    print(render_template("newsletter.md.j2", issue=issue))


if __name__ == "__main__":
    cli()
