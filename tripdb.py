import pymongo
import unittest
from test import testdata
import base
import sixfeet

class TripDB():
    def __init__(self, mongo_config):
        self.client = pymongo.MongoClient(
            mongo_config['host'],
            serverSelectionTimeoutMS=mongo_config['timeoutMS'],
            connectTimeoutMS=mongo_config['timeoutMS']
        )
        self.client.server_info() # Force connection

        self.db = self.client.tripsDB




#
# Representation in code of the trip objects.
#

class TripInfo:
    def __init__(self, id, title, type, hike_date, upload_date):
        self.id = id
        self.title = title
        self.type = type
        self.hike_date = hike_date
        self.upload_date = upload_date
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
    def setUp(self):
        self.dl = testdata.setUp()
        self.config = base.InitTest()

    def tearDown(self):
        pass

    def test_insert(self):
        me = sixfeet.SixFeetDownloader(self.dl, self.dl)
        trips = me.get_beijing_trip_info(range(1, 2))
        self.assertEqual(10, len(trips))

        db = TripDB(self.config['mongodb'])

        db.insert_many(trips)

        trip = db.find_one({'_id': '672456'})
        self.assertEqual("672456", trip.id)
        self.assertEqual("22公里测试", trip.title)
        self.assertEqual("徒步", trip.type)

        trip = db.find_one({'_id': '748475'})
        self.assertEqual("748475", trip.id)
        self.assertEqual("大觉寺 萝卜地 妙峰山 阳台山 凤凰岭 白虎涧", trip.title)

        trip = db.find_one({'_id': '748477'})
        self.assertEqual("748477", trip.id)

        self.assertEqual(datetime.datetime(2106, 2, 7, 14, 28), trip.hike_date)
        self.assertEqual(datetime.datetime(2015, 7, 21), trip.upload_date)