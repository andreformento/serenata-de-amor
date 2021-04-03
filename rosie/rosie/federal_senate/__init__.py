from rosie.federal_senate import settings
from rosie.federal_senate.adapter import Adapter
from rosie.core import Core


def main(target_directory='/tmp/serenata-data', skip_loaded_files=False):
    adapter = Adapter(target_directory, skip_loaded_files)
    core = Core(settings, adapter)
    core()