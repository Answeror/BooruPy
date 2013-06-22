# Copyright (C) 2012 Christopher Kaster
# This file is part of pyDanbooru
#
# You should have received a copy of the GNU General Public License
# along with pyDanbooru. If not, see <http://www.gnu.org/licenses/>


FIELDS = (
    'url',
    'width',
    'height',
    'rating',
    'score',
    'md5',
    'preview_url',
    'preview_width',
    'preview_height',
    'sample_url',
    'sample_width',
    'sample_height',
    'tags'
)


class Image:

    def __init__(self):
        pass

    @classmethod
    def from_dict(cls, image, mapping):
        inst = cls()
        if type(mapping) is dict:
            mapping = mapping.items()
        mapping = {rhs: lhs for lhs, rhs in mapping}
        for rhs, value in image.items():
            lhs = mapping.get(rhs, rhs)
            setattr(inst, lhs, image[rhs])
        for field in FIELDS:
            assert hasattr(inst, field), field
        return inst

    @classmethod
    def from_etree(cls, image, mapping):
        return cls.from_dict(dict(image.attrib.iteritems()), mapping)
