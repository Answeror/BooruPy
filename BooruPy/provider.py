# Copyright (C) 2012 Christopher Kaster
# This file is part of BooruPy
#
# You should have received a copy of the GNU General Public License
# along with BooruPy. If not, see <http://www.gnu.org/licenses/>
import json
from urlparse import urljoin
from image import Image
from xml.etree import ElementTree
import logging


LIMIT_MIN = 128


class BaseProvider:

    def __init__(self, base_url, name, shortname, filter_nsfw):
        self._base_url = base_url
        self.name = name
        self.shortname = shortname
        self._filter_nsfw = filter_nsfw

        import urllib3
        self._http = urllib3.PoolManager()

    def _fetch(self, request_url):
        return self._http.request('GET', request_url).data

    def _get_json(self, request_url):
        raw_json = self._fetch(request_url)
        return json.loads(raw_json)

    def _get_xml(self, request_url):
        raw_xml = self._fetch(request_url)
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
        limit = LIMIT_MIN
        page = self.start_page
        end = False
        fetched = 0
        while not end:
            logging.debug('limit %d' % limit)
            page_link = self._img_url % ('+'.join(tags), limit, page)
            images = list(self._get(page_link))
            if len(images) < limit:
                end = True
            for im in images[fetched:]:
                yield im
            fetched = len(images)
            # doubling next fetch
            limit += limit

    def _request_paged_images(self, tags, page, per):
        page = self.start_page + page
        page_link = self._img_url % ('+'.join(tags), per, page)
        for im in self._get(page_link):
            yield im

    def get_images(self, tags, page=None, per=None):
        if self._filter_nsfw:
            tags.append(self.nsfw_tag)

        if page is None or per is None:
            images = self._request_images(tags)
        else:
            images = self._request_paged_images(tags, page, per)

        for im in images:
            yield self._make_image(im)

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
