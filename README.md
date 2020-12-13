# Pocket-Newsletter

Assortment of scripts to make it easier to publish a collection of links as a newsletter.

I gather a list of links from Pocket and then use the Hacker News API to get more discussion points.
Pocket provides a word count that is used to estimate the reading time.

The script can replace Hacker News links with the main article.

## Getting started

You will need:

 * Python 3.8

```
pip install -r requirements.txt

# Convert hacker news bookmarks to the main article
./newsletter-cli.py resolve-hacker-news

# Create the newsletter
./newsletter-cli.py > newsletter.md
```
