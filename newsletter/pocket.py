import os
from datetime import datetime, timedelta
from math import ceil
from functools import cached_property
from urllib.parse import urlparse

from pockyt.auth import Authenticator
from pocket import Pocket


def estimate_reading_time(n_words):
    words_per_minute = 200
    return ceil(n_words / words_per_minute)


def extract_domain(url):
    u = urlparse(url)
    return u.netloc


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
            article["domain"] = extract_domain(article["resolved_url"])

            yield article

    def add(self, url):
        resp, _headers = self._client.add(url)
        return resp

    def archive(self, article):
        resp, _headers = self._client.archive(article["item_id"], wait=False)
        return resp
