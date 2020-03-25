import yaml
from translation import Translate
from cachetools import cached, TTLCache
cache = TTLCache(maxsize=10, ttl=86400)


class Config:
    values = {}

    @cached(cache)
    def __init__(self):
        with open("config.yml", 'r') as yml_conf_file:
            self.values = yaml.safe_load(yml_conf_file)

    def get_sources_list(self):
        return [*self.sources.keys()]

    def get_opt_sources_list(self, t: Translate):
        return [t.get(f'opt_source_{s}')
                for s in self.get_sources_list()]

    def get_opt_sources_mapping(self, t: Translate):
        return {t.get(f'opt_source_{s}'): s
                for s in self.get_sources_list()}

    def __getattr__(self, string: str):
        return self.values.get(string, f"{string}")

    def get(self, string: str):
        return self.values.get(string, f"{string}")
