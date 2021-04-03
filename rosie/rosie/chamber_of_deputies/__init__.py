from rosie.chamber_of_deputies import settings
from rosie.chamber_of_deputies.adapter import Adapter
from rosie.core import Core


def main(target_directory='/tmp/serenata-data', skip_loaded_files=False):
    adapter = Adapter(target_directory, skip_loaded_files)
    core = Core(settings, adapter)
    core()
