# Copyright (C) 2012 Christopher Kaster
# This file is part of BooruPy
#
# You should have received a copy of the GNU General Public License
# along with BooruPy. If not, see <http://www.gnu.org/licenses/>
import json
from provider import DanbooruProvider, GelbooruProvider


class BooruManager:

    def __init__(self):
        pass

    @classmethod
    def from_yaml(cls, providerlist_path, filter_nsfw=True):
        inst = cls()
        providers = json.load(open(providerlist_path))
        inst.provider_list = []
        for p in providers["providers"]:
            if p["type"] == "danbooru":
                inst.provider_list.append(DanbooruProvider(p['url'], p['name'],
                    p['key'], filter_nsfw, p['mapping']))
            elif p["type"] == "gelbooru":
                inst.provider_list.append(GelbooruProvider(p['url'], p['name'],
                    p['key'], filter_nsfw, p['mapping']))
            else:
                print("Unknown provider type: {0}".format(p["type"]))
        return inst

    @classmethod
    def from_python_file(cls, path):
        inst = cls()
        inst.provider_list = []
        import configit
        conf = configit.from_file(path)
        for p in conf.providers:
            if p['type'] == 'danbooru':
                Type = DanbooruProvider
            elif p['type'] == 'gelbooru':
                Type = GelbooruProvider
            else:
                raise Exception("Unknown provider type: {0}".format(p["type"]))
            inst.provider_list.append(Type(
                p['url'],
                p['name'],
                p['key'],
                p.get('filter_nsfw', True),
                p['mapping']
            ))
        return inst

    @property
    def providers(self):
        return self.provider_list

    def set_filter_nsfw(self, filter_nsfw=True):
        for provider in self.provider_list:
            provider.set_filter_nsfw(filter_nsfw)

    def get_provider_by_id(self, provider_id):
        if isinstance(provider_id, int):
            return self.provider_list[provider_id]

    def get_provider_by_key(self, provider_key):
        for p in self.provider_list:
            if p.key is provider_key:
                return p
