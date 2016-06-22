import tripdb
import sixfeet


def update_trip_db(config, tripdb):
    """
    Ensures the data in the trip DB is up to date.  Right now this is just a hack to
    put all the pre-downloaded info in, but in the future you could imagine querying
    for all newly-uploaded hikes and incrementally adding them.

    :param config:
    :param tripdb:
    :return:
    """
    trips = _download_tons_of_trips(config, range(1, 3))

    tripdb.insert_many(trips)


def _download_tons_of_trips(config, page_range):
    """
    Hack of a utility function to load trip and track data from foooooot.com.

    page_range is simply the range of pages to download, so page 1, once it's downloaded and
    stored in the cache, will never be updated.  This is obviously incorrect, but it worked
    well enough for me to download a few hundred tracks for analysis.
    """
    import time
    import random
    import cacheddownloader
    import json
    import codecs
    import jsonpickle

    cached_downloader = cacheddownloader.CachedDownloader(config['download_cache_folder'], True)
    sfclient = sixfeet.SixFeetDownloader(cached_downloader, cached_downloader)

    # Optimization to avoid loading and parsing html files on each run
    # trips_cache_file = os.path.join(config['download_cache_folder'], "trips.json")
    # if not os.path.exists(trips_cache_file):
    #     trips = sfclient.get_beijing_trip_info(page_range)
    #
    #     with codecs.open(trips_cache_file, 'w', 'utf-8') as file:
    #         file.write(jsonpickle.encode(trips))
    #     logging.info("Parsed {0} trips from html files; saved to '{1}'".format(len(trips), trips_cache_file))
    #
    # else:
    #     with codecs.open(trips_cache_file, 'r', 'utf-8') as file:
    #         trips = jsonpickle.decode(file.read())
    #     logging.info("Loaded {0} trips from cache".format(len(trips)))

    trips = sfclient.get_beijing_trip_info(page_range)

    for t in trips:
        t.track, dled_from_cache = sfclient.get_track_json(t)

        if not dled_from_cache:
            # foooooot.com returns HTTP 599 if you query it too quickly.  Introduce a random delay.
            time.sleep(random.randrange(2, 6))

    return trips

