import base
import sys
import os
import logging
import sixfeet
import cacheddownloader

def _prepare_config(config):
    """
    Loads the program configuration from the given json file.
    """

    def expand_config_path(key): config[key] = os.path.expanduser(config[key])

    expand_config_path('download_cache_folder')


if __name__ == "__main__":

    config = base.Init(sys.argv)
    _prepare_config(config)

    logging.info("Done, cache is at %s" % config['download_cache_folder'])

    cached_downloader = cacheddownloader.CachedDownloader(config['download_cache_folder'], True)

    sfclient = sixfeet.SixFeetDownloader(cached_downloader, cached_downloader)

    trips = sfclient.get_beijing_trip_info(range(1, 2))
    for t in trips:
        track = sfclient.get_track_json(t)

    logging.info("Downloaded tracks for %s trips" % len(trips))
