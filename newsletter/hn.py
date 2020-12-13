from urllib.parse import urlparse, parse_qs, urlencode
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

    def story_for(self, url):
        query = "https://hn.algolia.com/api/v1/search_by_date?" + urlencode(
            {"query": url, "restrictSearchableAttributes": "url", "tags": "story"}
        )
        resp = requests.get(query)
        results = resp.json()
        for hit in results.get("hits", []):
            story = {
                "item_id": hit["objectID"],
                "num_comments": hit["num_comments"],
                "url": f"https://news.ycombinator.com/item?id={hit['objectID']}",
            }
            return story
