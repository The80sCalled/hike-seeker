# Downloads tracks from foooooot.com.  "Six Feet" is the Chinese name of the site

import cacheddownloader
import os
import osutils
import shutil
import unittest
import logging

# Quick and fragile way to import eviltransform
import sys
sys.path.append('../lib/eviltransform/python')
import eviltransform

def download_tons_of_trips(config, page_range):
    """
    Hack of a utility function to load trip and track data from foooooot.com.

    page_range is simply the range of pages to download, so page 1, once it's downloaded and
    stored in the cahce, will never be updated.  This is obviously incorrect, but it worked
    well enough for me to download a few hundred tracks for analysis.
    """
    import time
    import random
    import cacheddownloader
    import json
    import codecs
    import jsonpickle

    cached_downloader = cacheddownloader.CachedDownloader(config['download_cache_folder'], True)
    sfclient = SixFeetDownloader(cached_downloader, cached_downloader)

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


class SixFeetDownloader:

    _FOOT_BASE_URL = "http://foooooot.com"

    # The '2' means Beijing
    _TRIP_LISTING_URL = "/search/trip/all/2/all/occurtime/descent/?page={0}&keyword="
    _TRACK_JSON_URL = "/trip/{0}/offsettrackjson/"

    def __init__(self, trip_downloader, track_downloader):
        self.trip_downloader = trip_downloader
        self.track_downloader = track_downloader

    def _parse_track_info_dom(self, dom):
        import re
        import datetime

        dom_trips = dom.xpath('//div[@class="listSection"]//li[not(@class)]//dl')
        infos = []

        for s in list(dom_trips):
            trip_url = s.xpath('.//p[@class="trip-title"]/a[1]/@href')[0]
            matches = re.search("^/trip/(\d*)/$", trip_url)
            trip_id = matches.group(1)

            trip_title = s.xpath('.//p[@class="trip-title"]/a[1]/text()')[0].strip()

            trip_type = s.xpath('./dd[1]/a[2]/text()')[0].strip()

            start_time_text = s.xpath('./dd[2]/text()')[0].strip()
            start_time_text = re.search("([-:\d\s]{8,20})", start_time_text).group(1).strip()
            trip_start_time = datetime.datetime.strptime(start_time_text, "%Y-%m-%d %H:%M")

            infos.append(TripInfo(trip_id, trip_title, trip_type, trip_start_time))

        return infos


    def get_beijing_trip_info(self, page_range):
        """Downloads basic track summary info"""
        from lxml import html

        trip_info = []

        for i in page_range:
            url = SixFeetDownloader._FOOT_BASE_URL + SixFeetDownloader._TRIP_LISTING_URL.format(i)
            doc, from_cache = self.trip_downloader.download(url)
            dom = html.fromstring(doc)
            new_trips = self._parse_track_info_dom(dom)
            trip_info.extend(new_trips)
            logging.info("Downloaded {0} new trips, first one's date is {1}".format(len(new_trips), new_trips[0].hike_date))

        return trip_info

    def get_track_json(self, trip_info):
        """Downloads the JSON for the GPS track"""
        import json

        url = SixFeetDownloader._FOOT_BASE_URL + SixFeetDownloader._TRACK_JSON_URL.format(trip_info.id)
        doc, from_cache = self.track_downloader.download(url)
        try:
            points_json = json.loads(doc)
        except:
            logging.warning("Couldn't parse json for trip {0}".format(trip_info.id))
            points_json = []

        points = []

        for p in points_json:
            p[1], p[2] = eviltransform.gcj2wgs(p[1], p[2])
            points.append(GpsTrackPoint(p[1], p[2], p[3], p[0], p[4], p[5]))

        return points, from_cache


class TripInfo:
    def __init__(self, id, title, type, hike_date):
        self.id = id
        self.title = title
        self.type = type
        self.hike_date = hike_date
        self.track = []


class GpsTrackPoint:
    def __init__(self, latitude, longitude, altitude, timestamp, speed, cumulative_distance):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.timestamp = timestamp
        self.speed = speed
        self.cumulative_distance = cumulative_distance


class UnitTests(unittest.TestCase):
    _TEMP_CACHE_FOLDER = os.path.expandvars("$Temp\\sixfeet_py_unittest_cache")

    def setUp(self):
        osutils.clear_dir(UnitTests._TEMP_CACHE_FOLDER)
        shutil.copytree("unittest\\test-data", UnitTests._TEMP_CACHE_FOLDER, True)
        self.dl = cacheddownloader.CachedDownloader(UnitTests._TEMP_CACHE_FOLDER, True)

    def tearDown(self):
        pass

    def test_track_list(self):
        import datetime

        me = SixFeetDownloader(self.dl, self.dl)

        trips = me.get_beijing_trip_info(range(1, 2))
        self.assertEqual(10, len(trips))

        self.assertEqual("672456", trips[0].id)
        self.assertEqual("22公里测试", trips[0].title)
        self.assertEqual("徒步", trips[0].type)

        self.assertEqual("748475", trips[1].id)
        self.assertEqual("大觉寺 萝卜地 妙峰山 阳台山 凤凰岭 白虎涧", trips[1].title)

        self.assertEqual(datetime.datetime(2106, 2, 7, 14, 28), trips[2].hike_date)

    def test_track_list_page_2(self):
        me = SixFeetDownloader(self.dl, self.dl)

        trips = me.get_beijing_trip_info(range(1, 3))
        self.assertEqual(20, len(trips))

        self.assertEqual("753443", trips[12].id)
        self.assertEqual("周六", trips[12].title)

    def test_track_points(self):
        import datetime

        me = SixFeetDownloader(self.dl, self.dl)

        fake_trip = TripInfo("931702", "20160618八大处-植物园", "登山", datetime.datetime(2016, 6, 18, 8, 53))

        track_points = me.get_track_json(fake_trip)

        self.assertEqual(835, len(track_points))
        self.assertEqual("1466211222", track_points[1].timestamp)
        self.assertAlmostEqual(39.946837, track_points[1].latitude, 6)
        self.assertAlmostEqual(116.1830357, track_points[1].longitude, 6)
        self.assertEqual(88.0, track_points[1].altitude)
        self.assertEqual(4.5, track_points[1].speed)
        self.assertEqual(0.02332, track_points[1].cumulative_distance)


# class UnitTests(unittest.TestCase):
#     _TEMP_SENTENCE_CACHE_FOLDER = os.path.expandvars("$Temp\\sentences_py_unittest_cache")
#
#     def setUp(self):
#         osutils.clear_dir(UnitTests._TEMP_SENTENCE_CACHE_FOLDER)
#
#     def tearDown(self):
#         pass
#
#     def test_bing_download(self):
#         """Should download sentences for a given word, and use cache"""
#         downloader = CachedDownloader(UnitTests._TEMP_SENTENCE_CACHE_FOLDER)
#         me = SentenceDownloader(downloader)
#
#         test_word = u"\u4fdd\u62a4"
#         sentences = me.get_sentences_bing(test_word) # bao3hu4, protect
#
#         self.assertEqual(len(sentences), 10, "sentence count")
#         self.assertTrue(sentences[0]['chinese'].find(test_word) >= 0, "downloaded sentence contains word")
#
#         sentences2 = me.get_sentences_bing(test_word) # same thing
#         self.assertEqual(1, downloader.download_count, "download count")
#         self.assertEqual(json.dumps(sentences), json.dumps(sentences2), "sentences downloaded should be identical")
#
#
#     def test_iciba_download(self):
#         """Should download sentences for a given word, and use cache"""
#         downloader = CachedDownloader(UnitTests._TEMP_SENTENCE_CACHE_FOLDER)
#         me = SentenceDownloader(downloader)
#
#         test_word = u"\u4fdd\u62a4"
#         sentences = me.get_sentences_iciba(test_word) # bao3hu4, protect
#
#         self.assertEqual(len(sentences), 10, "sentence count")
#         self.assertTrue(sentences[0]['chinese'].find(test_word) >= 0, "downloaded sentence contains word")
#         self.assertTrue(
#             sentences[0]['english'].find("protection") >= 0 or
#             sentences[0]['english'].find("cover") >= 0 or
#             sentences[0]['english'].find("protect") >= 0,
#             "downloaded sentence contains English word")
#
#         first_char = sentences[0]['chinese'][0]
#         self.assertTrue(first_char != '\t' and first_char != '\r')
#         self.assertTrue(first_char != "1")
#
#         sentences2 = me.get_sentences_iciba(test_word) # same thing
#         self.assertEqual(1, downloader.download_count, "download count")
#         self.assertEqual(json.dumps(sentences), json.dumps(sentences2), "sentences downloaded should be identical")
