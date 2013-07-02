# Copyright (C) 2012 Christopher Kaster
# This file is part of pyDanbooru
#
# You should have received a copy of the GNU General Public License
# along with pyDanbooru. If not, see <http://www.gnu.org/licenses/>


from functools import partial
from operator import getitem


FIELDS = (
    'url',
    'width',
    'height',
    'rating',
    'score',
    'md5',
    'preview_url',
    'tags'
)


class Image:

    def __init__(self):
        pass

    @classmethod
    def from_dict(cls, image, root, mapping):
        if type(mapping) is dict:
            def map_fn(source):
                d = {}
                for key, value in image.items():
                    d[key] = value
                for lhs, rhs in mapping.items():
                    if type(rhs) is tuple:
                        rhs, fn = rhs
                    elif hasattr(rhs, '__call__'):
                        fn = rhs
                        rhs = lhs
                    else:
                        fn = lambda x: x
                    d[lhs] = fn(image[rhs])
                return d
        else:
            map_fn = mapping

        inst = cls()
        for key, value in map_fn(image).items():
            setattr(inst, key, value)

        for field in FIELDS:
            assert hasattr(inst, field), field

        from urlparse import urljoin
        for key, value in inst.__dict__.items():
            if key.endswith('url'):
                setattr(inst, key, urljoin(root, value))
        return inst

    @classmethod
    def from_etree(cls, image, root, mapping):
        return cls.from_dict(dict(image.attrib.iteritems()), mapping)
