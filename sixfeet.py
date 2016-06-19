# Downloads tracks from foooooot.com.  "Six Feet" is the Chinese name of the site

import cacheddownloader

class SixFeetDownloader:

    _FOOT_BASE_URL = "http://foooooot.com

    # The '2' means Beijing
    _TRACK_LISTING_URL = "/search/trip/all/2/all/occurtime/descent/?page={0}&keyword="

    def __init__(self, downloader):
        self.downloader = downloader
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


    def get_beijing_track_info(self, word):
        """Downloads basic track summary info"""
        from lxml import html

        # TODO: urllib.parse.urlencode seems to order its parameters however it feels like it,
        # TODO: which messes with the caching logic. So, yeah
        #query_string = urllib.parse.urlencode({ "q": word })
        url = SixFeetDownloader._FOOT_BASE_URL + SixFeetDownloader._TRACK_LISTING_URL.Format("1")

        dom = html.fromstring(self.downloader.download_with_cache(url))

        return self._parse_sentences_bing(dom)


#     def get_sentences_iciba(self, word):
#         """Downloads example sentences for a given word from Bing"""
#         from lxml import html
#
#         url = SentenceDownloader._ICIBA_BASE_URL + "/" + word + "-1.html"
#         dom = html.fromstring(self.downloader.download_with_cache(url))
#
#         return self._parse_sentences_iciba(dom)
#
#
#


class UnitTests(unittest.TestCase):
    _TEMP_SENTENCE_CACHE_FOLDER = os.path.expandvars("$Temp\\sentences_py_unittest_cache")

    def setUp(self):
        osutils.clear_dir(UnitTests._TEMP_SENTENCE_CACHE_FOLDER)

    def tearDown(self):
        pass

    def test_track_list(self):
        downloader =

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
