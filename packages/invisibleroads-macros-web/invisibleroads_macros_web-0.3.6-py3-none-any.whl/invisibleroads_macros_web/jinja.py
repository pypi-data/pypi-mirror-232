from os.path import dirname, getmtime, join, normpath, realpath
from string import Template as StringTemplate

from invisibleroads_macros_disk import get_asset_path
from jinja2 import (
    BaseLoader,
    Environment,
    Template as JinjaTemplate,
    TemplateNotFound,
    pass_context)


class AssetStorage():

    def __init__(self, folder):
        self.folder = folder

    def load_raw_text(self, file_name):
        return (self.folder / file_name).read_text().strip()

    def load_string_text(self, file_name):
        return StringTemplate(self.load_raw_text(file_name))

    def load_jinja_text(self, file_name):
        return JinjaTemplate(self.load_raw_text(file_name), trim_blocks=True)


class PathTemplateLoader(BaseLoader):

    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def get_source(self, environment, template):
        'Support absolute template paths'
        try:
            modification_time = getmtime(template)
        except (OSError, TypeError):
            raise TemplateNotFound(template)

        def is_latest():
            try:
                return modification_time == getmtime(template)
            except OSError:
                return False

        with open(template, mode='rt', encoding=self.encoding) as f:
            text = f.read()
        return text, realpath(template), is_latest


class RelativeTemplateEnvironment(Environment):

    def join_path(self, template, parent):
        'Support relative template paths via extends, import, include'
        template = get_asset_path(template)
        return normpath(join(dirname(
            parent), template)) if template else template


@pass_context
def url_for(context, name, **d):
    return context['request'].url_for(name, **d)
