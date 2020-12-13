#!/usr/bin/env python

from datetime import datetime

import click
from jinja2 import Template
from newsletter.hn import HackerNewsClient
from newsletter.pocket import PocketClient


def render_template(template, **context):
    with open(template) as fh:
        t = Template(fh.read())
        return t.render(**context)


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
@click.argument("urls", nargs=-1)
def hn(urls):
    hn = HackerNewsClient()
    for url in urls:
        story = hn.story_for(url)
        click.echo(f"{url}: {story['url']}")


@cli.command()
@click.option("--number", "issue_number", default=4)
@click.option("--template", default="newsletter.md.j2")
def newsletter(issue_number, template):
    pocket = PocketClient()
    hn = HackerNewsClient()
    articles = []
    for article in pocket.articles(since={"days": 7}):
        story = hn.story_for(article["resolved_url"])
        if story:
            article["hn_url"] = story["url"]
            article["hn_comments"] = story["num_comments"]
        articles.append(article)

    now = datetime.today()

    issue = {
        "number": issue_number,
        "title": "Tech Whimsys",
        "subtitle": "CentOS commits suicide?",
        "date": now.isoformat(),
        "human_date": now.strftime("%A, %B %d, %Y"),
        "articles": articles,
    }

    print(render_template(template, issue=issue))


if __name__ == "__main__":
    cli()
