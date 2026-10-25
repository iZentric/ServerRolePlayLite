from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "community" / "index.html"


class PageFacts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.fragments = []
        self.text = []
        self.lang_ro = False
        self.title_open = False
        self.title_seen = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html" and attrs.get("lang") == "ro":
            self.lang_ro = True
        if "id" in attrs:
            self.ids.add(attrs["id"])
        href = attrs.get("href", "")
        if href.startswith("#") and len(href) > 1:
            self.fragments.append(href[1:])
        if tag == "title":
            self.title_open = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.title_open = False
            self.title_seen = True

    def handle_data(self, data):
        self.text.append(data)


class CommunityPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.parser = PageFacts()
        cls.parser.feed(cls.html)
        cls.visible = " ".join(cls.parser.text)

    def test_page_is_romanian_fun_city_and_has_valid_internal_navigation(self):
        self.assertTrue(self.parser.lang_ro)
        self.assertTrue(self.parser.title_seen)
        self.assertIn("FunCity", self.visible)
        self.assertIn("roleplay", self.visible.lower())
        self.assertTrue(self.parser.fragments)
        self.assertFalse(set(self.parser.fragments) - self.parser.ids)

    def test_no_unverified_invite_or_server_address_is_advertised(self):
        self.assertNotRegex(self.html, r"(?i)discord\.gg/|discord(?:app)?\.com/invite/")
        self.assertNotRegex(self.html, r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}")
        self.assertRegex(self.visible, r"(?i)nu există încă un link de invitație")
        self.assertRegex(self.visible, r"(?i)adresa serverului nu este publicată")

    def test_page_is_explicitly_paper_only_and_does_not_promise_hybrid_support(self):
        self.assertIn("Paper-only", self.visible)
        self.assertIn("Bukkit/Paper", self.visible)
        self.assertIn("fără Forge", self.visible)
        self.assertIn("client Java nemodat", self.visible)
        self.assertNotRegex(self.visible, r"(?i)server hibrid|client Forge")
        self.assertNotRegex(self.visible, r"(?i)compatibil(?:itate)? universal(?:ă|a)")

    def test_page_is_self_contained_and_uses_no_remote_assets(self):
        self.assertNotRegex(self.html, r"(?i)<(?:script|img|iframe)\b")
        self.assertNotRegex(self.html, r"(?i)(?:src|href)=['\"]https?://")


if __name__ == "__main__":
    unittest.main()
