import base
import sys
import os
import logging

def _prepare_config(config):
    """
    Loads the program configuration from the given json file.
    """

    def expand_config_path(key): config[key] = os.path.expanduser(config[key])

    expand_config_path('sentence_cache_folder')


if __name__ == "__main__":

    config = base.Init(sys.argv)
    _prepare_config(config)

    logging.info("Done, cache is at %s" % config['sentence_cache_folder'])


