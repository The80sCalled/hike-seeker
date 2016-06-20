import base
import sys
import os
import logging
import sixfeet
import tripvis


def _prepare_config(config):
    """
    Loads the program configuration from the given json file.
    """

    def expand_config_path(key): config[key] = os.path.expanduser(config[key])

    expand_config_path('download_cache_folder')
    expand_config_path('kml_output_folder')


def _download_tons_of_trips(config, page_range, use_delay):
    import time
    import random
    import cacheddownloader

    cached_downloader = cacheddownloader.CachedDownloader(config['download_cache_folder'], True)
    sfclient = sixfeet.SixFeetDownloader(cached_downloader, cached_downloader)

    trips = sfclient.get_beijing_trip_info(page_range)
    for t in trips:
        # foooooot.com returns HTTP 599 if you query it too quickly.  This introduces a random delay.
        if use_delay:
            time.sleep(random.randrange(2, 6))

        t.track = sfclient.get_track_json(t)

    return trips


if __name__ == "__main__":
    config = base.Init(sys.argv)
    _prepare_config(config)

    logging.info("Done, cache is at %s" % config['download_cache_folder'])

    INCLUDE_PAGE_RANGE = range(1, 2)

    trips = _download_tons_of_trips(config, INCLUDE_PAGE_RANGE, use_delay=False)
    original_trips_len = len(trips)

    skip = {"748475"}
    activity_types = {"登山", "徒步"}
    trips = [t for t in trips if t.id not in skip and t.type in activity_types]
    logging.info("Loaded {0} trips, {1} meet filter criteria".format(original_trips_len, len(trips)))

    os.makedirs(config['kml_output_folder'], exist_ok=True)
    tripvis.visualize_trips(trips, os.path.join(config['kml_output_folder'], "BeijingHikes.kml"))
