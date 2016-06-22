import pymongo
import unittest
from test import testdata
import base
import sixfeet
import datetime

class TripDB():
    def __init__(self, mongo_config):
        self.client = pymongo.MongoClient(
            mongo_config['host'],
            serverSelectionTimeoutMS=mongo_config['timeoutMS'],
            connectTimeoutMS=mongo_config['timeoutMS']
        )
        self.client.server_info() # Force connection

        self.db = self.client.get_database(mongo_config['tripsDBName'])

    def drop_db(self):
        self.client.drop_database(self.db.name)

    def insert_many(self, items, ignore_duplicates=False):
        """
        Inserts the given items into the database

        :param items: List of items to insert
        :param ignore_duplicates: Whether to swallow errors from duplicate inserted items
        :return:
        """
        insertable = [i.to_dictionary() for i in items]

        try:
            ret = self.db.trips.insert_many(insertable, ordered=False)
        except pymongo.errors.BulkWriteError as e:
            dupe_indices = set([err['index'] for err in e.details['writeErrors'] if err['code'] == 11000])
            if e.details['nInserted'] + len(dupe_indices) != len(items) or not ignore_duplicates:
                raise

            ret = pymongo.results.InsertManyResult([items[i].id for i in range(len(items)) if i not in dupe_indices], False)

        return ret

    def find_one(self, find_exp):
        return TripInfo.from_dictionary(self.db.trips.find_one(find_exp))


#
# Representation in code of the trip objects.
#

class TripInfo:
    def __init__(self, id, title, type, hike_date, upload_date):
        # These are all
        self.id = id
        self.title = title
        self.type = type
        self.hike_date = hike_date
        self.upload_date = upload_date
        self.track = []

    def to_dictionary(self):
        ret = dict(self.__dict__)
        # MongoDB uses _id for the built-in ID field, might as well use that.  Keep .id for the Python interface though.
        ret['_id'] = self.id
        ret.pop('id')
        # Built-in __dict__ contains 'track': [<tripdb.GpsTrackPoint object at 0x0xxxxx>], so fix that
        ret['track'] = [p.to_dictionary() for p in self.track]
        return ret

    @staticmethod
    def from_dictionary(dict):
        track = [GpsTrackPoint.from_dictionary(x) for x in dict['track']]
        trip_info = TripInfo(dict['_id'], dict['title'], dict['type'], dict['hike_date'], dict['upload_date'])
        trip_info.track = track
        return trip_info


class GpsTrackPoint:
    def __init__(self, latitude, longitude, altitude, timestamp, speed, cumulative_distance):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.timestamp = timestamp
        self.speed = speed
        self.cumulative_distance = cumulative_distance

    def to_dictionary(self):
        return [self.timestamp, self.latitude, self.longitude, self.altitude, self.speed, self.cumulative_distance]

    @staticmethod
    def from_dictionary(dict):
        return GpsTrackPoint(dict[1], dict[2], dict[3], dict[0], dict[4], dict[5])


class PocoTests(unittest.TestCase):
    def setUp(self):
        import datetime
        self.fake_trip = TripInfo("931702", "20160618八大处-植物园", "登山", datetime.datetime(2016, 6, 18, 8, 53),
                             datetime.datetime(2016, 5, 19))
        self.fake_trip.track.extend([
            GpsTrackPoint(1, 2, 3, 4, 5, 6),
            GpsTrackPoint(2, 3, 4, 5, 6, 7)
        ])

    def test_dictionary(self):
        import datetime

        fake_trip_as_dict = {
            '_id': "931702",
            'title': "20160618八大处-植物园",
            'type': "登山",
            'hike_date': datetime.datetime(2016, 6, 18, 8, 53),
            'upload_date': datetime.datetime(2016, 5, 19),
            'track': [[4, 1, 2, 3, 5, 6], [5, 2, 3, 4, 6, 7]]
        }

        self.assertEqual(
            fake_trip_as_dict,
            self.fake_trip.to_dictionary()
        )

        from_dict = TripInfo.from_dictionary(fake_trip_as_dict)
        to_dict_again = from_dict.to_dictionary()

        self.assertDictEqual(fake_trip_as_dict, to_dict_again)


class TripDBTests(unittest.TestCase):
    def setUp(self):
        self.dl = testdata.setUp()
        self.config = base.InitTest()
        self.db = TripDB(self.config['mongodb'])
        self.db.drop_db()

    def tearDown(self):
        pass

    def test_db_round_trip(self):
        me = sixfeet.SixFeetDownloader(self.dl, self.dl)
        trips = me.get_beijing_trip_info(range(1, 2))
        self.assertEqual(10, len(trips))

        trips[0].track, from_cache = me.get_track_json(trips[0])
        self.assertTrue(from_cache)
        self.assertEqual(200, len(trips[0].track))

        result = self.db.insert_many(trips)
        self.assertEqual(10, len(result.inserted_ids))

        trip = self.db.find_one({'_id': '672456'})
        self.assertEqual("672456", trip.id)
        self.assertEqual("22公里测试", trip.title)
        self.assertEqual("徒步", trip.type)
        self.assertEqual(200, len(trip.track))
        self.assertAlmostEqual(0.042071, trip.track[1].cumulative_distance, 6)

        trip = self.db.find_one({'_id': '748475'})
        self.assertEqual("748475", trip.id)
        self.assertEqual("大觉寺 萝卜地 妙峰山 阳台山 凤凰岭 白虎涧", trip.title)

        trip = self.db.find_one({'_id': '748477'})
        self.assertEqual("748477", trip.id)

        self.assertEqual(datetime.datetime(2106, 2, 7, 14, 28), trip.hike_date)
        self.assertEqual(datetime.datetime(2015, 7, 21), trip.upload_date)

    def test_insert_duplicate(self):
        me = sixfeet.SixFeetDownloader(self.dl, self.dl)
        trips = me.get_beijing_trip_info(range(1, 2))
        # put it at the beginning to ensure insert_many attempts all operations
        trips.insert(0, trips[0])

        result = self.db.insert_many(trips, ignore_duplicates=True)
        self.assertEqual(10, len(result.inserted_ids))

