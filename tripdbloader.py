import tripdb
import sixfeet
import logging

def update_trip_db(config, db):
    """
    Ensures the data in the trip DB is up to date.  Right now this is just a hack to
    put all the pre-downloaded info in, but in the future you could imagine querying
    for all newly-uploaded hikes and incrementally adding them.

    :param config:
    :param db:
    :return:
    """
    trips = _download_tons_of_trips(config, range(500, 2451))

    logging.info("Begin insert {0} rows into MongoDB...".format(len(trips)))
    result = db.insert_many(trips, ignore_duplicates=True)
    logging.info("Insert {0} rows complete.".format(len(result.inserted_ids)))


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

    cached_downloader = cacheddownloader.CachedDownloader(config['download_cache_folder'], True)
    sfclient = sixfeet.SixFeetDownloader(cached_downloader, cached_downloader)

    trips = sfclient.get_beijing_trip_info(page_range)

    for t in trips:
        t.track, dled_from_cache = sfclient.get_track_json(t)

        if not dled_from_cache:
            # foooooot.com returns HTTP 599 if you query trip json too quickly.  Introduce a random delay.
            time.sleep(random.randrange(2, 6))

    return trips

