import os
from django.apps import AppConfig

default_app_config = 'index.IndexConfig'

def get_current_app_name(_file):
    return os.path.split(os.path.dirname(_file))[-1]


class IndexConfig(AppConfig):
    name = get_current_app_name(__file__)
    verbose_name=u'首页'
