# Copyright (C) 2012 Christopher Kaster
# This file is part of BooruPy
#
# You should have received a copy of the GNU General Public License
# along with BooruPy. If not, see <http://www.gnu.org/licenses/>
import json
import urllib
from urlparse import urljoin
from image import Image
from xml.etree import ElementTree


class BaseProvider:

    def __init__(self, base_url, name, shortname, filter_nsfw):
        self._base_url = base_url
        self.name = name
        self.shortname = shortname
        self._filter_nsfw = filter_nsfw

    def _get_URLopener(self):
        return urllib.FancyURLopener({})  # TODO: add proxy support

    def _get_json(self, request_url):
        opener = self._get_URLopener()
        raw_json = opener.open(request_url)
        return json.load(raw_json)

    def _get_xml(self, request_url):
        opener = self._get_URLopener()
        raw_xml = opener.open(request_url).read()
        return ElementTree.XML(raw_xml)

    def set_filter_nsfw(self, filter_nsfw=True):
        self._filter_nsfw = filter_nsfw

    @property
    def start_page(self):
        assert False

    @property
    def method(self):
        assert False

    @property
    def nsfw_tag(self):
        assert False

    def _check_method(self):
        assert self.method in ('xml', 'json'), self.method

    def _get(self, request_url):
        self._check_method()
        return {
            'xml': self._get_xml,
            'json': self._get_json
        }[self.method](request_url)

    def _make_image(self, node):
        self._check_method()
        return {
            'xml': Image.from_etree,
            'json': Image.from_dict
        }[self.method](node)

    def _request_images(self, tags):
        limit = 100
        page = self.start_page
        end = False
        while not end:
            page_link = self._img_url % ('+'.join(tags), limit, page)
            images = self._get(page_link)
            if len(images) < limit:
                end = True
            yield images
            page += 1

    def get_images(self, tags):
        if self._filter_nsfw:
            tags.append(self.nsfw_tag)

        for images in self._request_images(tags):
            for i in images:
                yield self._make_image(i)

    def get_tags(self):
        for tags in self._request_tag():
            for tag in tags:
                yield tag.count, tag.name

    def _request_tag(self):
        limit = 100
        page = self.start_page
        end = False
        while not end:
            page_link = self._tag_url % (limit, page)
            tags = self._get(page_link)
            if len(tags) < limit:
                end = True
            yield tags
            page += 1


class DanbooruProvider(BaseProvider):

    def __init__(self, base_url, name, shortname, filter_nsfw):
        BaseProvider.__init__(self, base_url, name, shortname, filter_nsfw)
        self._img_url = urljoin(
            self._base_url,
            "/post/index.json?tags=%s&limit=%s&page=%s"
        )
        self._tag_url = urljoin(
            self._base_url,
            "/tags/index.json?limit=%s&page=%s"
        )

    @property
    def start_page(self):
        return 1

    @property
    def method(self):
        return 'json'

    @property
    def nsfw_tag(self):
        return "rating:s"


class GelbooruProvider(BaseProvider):

    def __init__(self, base_url, name, shortname, filter_nsfw):
        BaseProvider.__init__(self, base_url, name, shortname, filter_nsfw)
        self._img_url = urljoin(
            self._base_url,
            "/index.php?page=dapi&s=post&q=index&tags=%s&limit=%s&pid=%s"
        )
        self._tag_url = urljoin(
            self._base_url,
            "/index.php?page=dapi&s=tag&q=index&limit=%s&pid=%s"
        )

    @property
    def start_page(self):
        return 0

    @property
    def method(self):
        return 'xml'

    @property
    def nsfw_tag(self):
        return "rating:safe"
