import base
import sys
import os
import logging
import sixfeet
import tripvis
import tripdb
import tripdbloader

def _prepare_config(config):
    """
    Loads the program configuration from the given json file.
    """

    def expand_config_path(key): config[key] = os.path.expanduser(config[key])

    expand_config_path('download_cache_folder')
    expand_config_path('kml_output_folder')


def _update_trip_db(config):
    db = tripdb.TripDB(config['mongodb'])
    tripdbloader.update_trip_db(config, db)


if __name__ == "__main__":
    config = base.Init(sys.argv)
    _prepare_config(config)

    logging.info("Done, cache is at %s" % config['download_cache_folder'])

    _update_trip_db(config)

    # original_trips_len = len(trips)
    # skip_ids = {"748475"}
    # activity_types = {"登山", "徒步", "观光旅游"}
    # trips = [t for t in trips if t.id not in skip_ids and t.type in activity_types]
    # logging.info("Loaded {0} trips, {1} meet filter criteria".format(original_trips_len, len(trips)))

    # os.makedirs(config['kml_output_folder'], exist_ok=True)
    # tripvis.visualize_trips(trips, os.path.join(config['kml_output_folder'], "BeijingHikes.kml"))
