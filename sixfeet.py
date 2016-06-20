# Downloads tracks from foooooot.com.  "Six Feet" is the Chinese name of the site

import cacheddownloader
import os
import osutils
import shutil
import unittest

class SixFeetDownloader:

    _FOOT_BASE_URL = "http://foooooot.com"

    # The '2' means Beijing
    _TRIP_LISTING_URL = "/search/trip/all/2/all/occurtime/descent/?page={0}&keyword="

    def __init__(self, trip_downloader, track_downloader):
        self.trip_downloader = trip_downloader
        self.track_downloader = track_downloader

    #
    # def _parse_sentences_bing(self, dom):
    #     dom_sentences = dom.xpath('//*[@class="se_li"]')
    #     sentences = []
    #
    #     for s in list(dom_sentences):
    #         english = "".join(s.xpath('.//*[@class="sen_en"]//text()'))
    #         chinese = "".join(s.xpath('.//*[@class="sen_cn"]//text()'))
    #
    #         sentences.append({ "english": english, "chinese": chinese})
    #
    #     return sentences
    #
    # def _parse_sentences_iciba(self, dom):
    #     import re
    #
    #     dom_sentences = dom.xpath('//*[@class="dj_li"]')
    #     sentences = []
    #
    #     for s in list(dom_sentences):
    #         # Can't use tokenize a la http://stackoverflow.com/questions/20692303/xslt-select-elements-that-have-multiple-class-values-based-off-of-1-of-those-v
    #         # Get an unregistered function exception
    #         raw_english = "".join(s.xpath('.//*[@class="stc_en_txt font_arial"]//text()'))
    #         matches = re.search("^\d{1,2}\.\s(.*)$", raw_english.strip())
    #         english = matches.group(1)
    #         chinese = "".join(s.xpath('.//*[@class="stc_cn_txt"]//text()'))
    #         chinese = chinese.strip()
    #
    #         sentences.append({ "english": english, "chinese": chinese})
    #
    #     return sentences
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

            start_time_text = s.xpath('./dd[2]/text()')[0].strip()
            start_time_text = re.search("([-:\d\s]{8,20})", start_time_text).group(1).strip()
            trip_start_time = datetime.datetime.strptime(start_time_text, "%Y-%m-%d %H:%M")

            infos.append(TripInfo(trip_id, trip_title, trip_start_time))

        return infos


    def get_beijing_trip_info(self, num_pages):
        """Downloads basic track summary info"""
        from lxml import html

        trip_info = []

        for i in range(1, num_pages + 1):
            url = SixFeetDownloader._FOOT_BASE_URL + SixFeetDownloader._TRIP_LISTING_URL.format("1")
            dom = html.fromstring(self.trip_downloader.download(url))
            trip_info.extend(self._parse_track_info_dom(dom))

        return trip_info


class TripInfo:
    def __init__(self, id, title, hike_date):
        self.id = id
        self.title = title
        self.hike_date = hike_date


class UnitTests(unittest.TestCase):
    _TEMP_SENTENCE_CACHE_FOLDER = os.path.expandvars("$Temp\\sixfeet_py_unittest_cache")

    def setUp(self):
        osutils.clear_dir(UnitTests._TEMP_SENTENCE_CACHE_FOLDER)
        shutil.copytree("unittest\\test-data", UnitTests._TEMP_SENTENCE_CACHE_FOLDER, True)

    def tearDown(self):
        pass

    def test_track_list(self):
        import datetime

        me = SixFeetDownloader(cacheddownloader.CachedDownloader(UnitTests._TEMP_SENTENCE_CACHE_FOLDER, True),
                               cacheddownloader.CachedDownloader(UnitTests._TEMP_SENTENCE_CACHE_FOLDER, True))

        trips = me.get_beijing_trip_info(1)
        self.assertEqual(10, len(trips))

        self.assertEqual("672456", trips[0].id)
        self.assertEqual("22公里测试", trips[0].title)

        self.assertEqual("748475", trips[1].id)
        self.assertEqual("大觉寺 萝卜地 妙峰山 阳台山 凤凰岭 白虎涧", trips[1].title)

        self.assertEqual(datetime.datetime(2106, 2, 7, 14, 28), trips[2].hike_date)

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
