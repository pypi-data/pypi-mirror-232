import re
import markdown
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import requests


def validate_urls(url):
    broken_link_status_codes = [404, 410, 408, 504, 502, 503, 500, 403, 401, 400]
    try:
        res = requests.head(url, timeout=2.5)
        if res.status_code in broken_link_status_codes:
            return False
    except Exception:
        return False

    return True


class UrlValidate:
    def validate_markup_urls(self, content):
        pattern = re.compile(r'<a[\s]+([^>]+)>((?:.(?!\<\/a\>))*.)</a>')
        content = markdown.markdown(content)
        tag_matches = re.findall(pattern, content)
        urls = []
        for tag_data in tag_matches:
            tag = tag_data[0]
            tag = tag.replace('href=\"', "")
            tag = tag[:tag.index('"')]
            if not tag[0].isalpha():
                continue
            urls.append(tag)

        invalid_urls = []
        for url in urls:
            if not validate_urls(url):
                invalid_urls.append(url)
        return invalid_urls

    def get_active_urls_list(self, content):
        pattern = re.compile(r'<a[\s]+([^>]+)>((?:.(?!\<\/a\>))*.)</a>')
        content = markdown.markdown(content)
        tag_matches = re.findall(pattern, content)
        urls = []
        for tag_data in tag_matches:
            tag = tag_data[0]
            tag = tag.replace('href=\"', "")
            tag = tag[:tag.index('"')]
            if not tag[0].isalpha():
                continue
            urls.append(tag)
