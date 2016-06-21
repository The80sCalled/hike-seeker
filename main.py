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
    import json
    import codecs
    import jsonpickle

    cached_downloader = cacheddownloader.CachedDownloader(config['download_cache_folder'], True)
    sfclient = sixfeet.SixFeetDownloader(cached_downloader, cached_downloader)

    trips_cache_file = os.path.join(config['download_cache_folder'], "trips.json")
    if not os.path.exists(trips_cache_file):
        trips = sfclient.get_beijing_trip_info(page_range)

        with codecs.open(trips_cache_file, 'w', 'utf-8') as file:
            file.write(jsonpickle.encode(trips))
        logging.info("Parsed {0} trips from html files; saved to '{1}'".format(len(trips), trips_cache_file))

    else:
        with codecs.open(trips_cache_file, 'r', 'utf-8') as file:
            trips = jsonpickle.decode(file.read())
        logging.info("Loaded {0} trips from cache".format(len(trips)))

    # DEBUG: only load some trips
    trips = trips[0:1000]

    for t in trips: # [4000:]
        # foooooot.com returns HTTP 599 if you query it too quickly.  Introduce a random delay.
        if use_delay:
            time.sleep(random.randrange(2, 6))

        t.track = sfclient.get_track_json(t)

    return trips


if __name__ == "__main__":
    config = base.Init(sys.argv)
    _prepare_config(config)

    logging.info("Done, cache is at %s" % config['download_cache_folder'])

    INCLUDE_PAGE_RANGE = range(1, 2451)

    trips = _download_tons_of_trips(config, INCLUDE_PAGE_RANGE, use_delay=False)
    original_trips_len = len(trips)

    skip_ids = {"748475"}
    activity_types = {"登山", "徒步"}
    trips = [t for t in trips if t.id not in skip_ids and t.type in activity_types]
    logging.info("Loaded {0} trips, {1} meet filter criteria".format(original_trips_len, len(trips)))

    os.makedirs(config['kml_output_folder'], exist_ok=True)
    tripvis.visualize_trips(trips, os.path.join(config['kml_output_folder'], "BeijingHikes.kml"))
