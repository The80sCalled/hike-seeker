import requests
import osutils
import os
import codecs
import logging

class CachedDownloader:

    def __init__(self, cache_folder, use_cache):
        self.cache_folder = cache_folder
        self.download_count = 0
        self.use_cache = use_cache
        osutils.ensure_dir(self.cache_folder)

    def download(self, url):
        """
        Downloads example sentences for the given word from Bing's dictionary.
        Returns the content of the html page.
        :param word: hanzi of word to search for
        :return:
        """
        if not self.use_cache:
            response = requests.get(url)
            response_as_text = response.content.decode(encoding=response.encoding)
            return response_as_text

        cache_file = os.path.join(self.cache_folder, osutils.make_valid_filename(url) + ".txt")

        if not os.path.exists(cache_file):
            logging.info("Requesting content from '%s'", url)

            response = requests.get(url)
            self.download_count += 1
            response_as_text = response.content.decode(encoding = response.encoding)

            with codecs.open(cache_file, 'w', 'utf-8') as file:
                file.write(response_as_text)

            logging.info("Saved content to '%s'", cache_file)
            return response_as_text

        else:
            with codecs.open(cache_file, 'r', 'utf-8') as file:
                return file.read()
