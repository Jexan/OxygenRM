from . import *

import datetime

class DatetimeModel(O.Model):
    created = Datetime(create_date=True)
    updated = Datetime(update_date=True)

    random = Datetime()

class TestDateTimeFields(unittest.TestCase):
    def setUp(self):
        db.create_table('DatetimeModels', default_cols(created='datetime', updated='datetime', random="datetime"))

    def tearDown(self):
        db.drop_table('DatetimeModels')

    def test_model_initialization(self):
        t1 = DatetimeModel()

        self.assertIs(t1.created, None)
        self.assertIs(t1.updated, None)
        self.assertIs(t1.random, None)

    @unittest.skip('Incomplete')
    def test_new_model_saved_creates_updated_and_created(self):
        t1 = DatetimeModel()
        t1.save()

        self.assertIsInstance(t1.a, list)
        self.assertTrue(t1.a.conformable)

    def test_updated_model_changes_time(self):
        t1 = DatetimeModel()
        t1.save()

        first = DatetimeModel.first().save()

        self.assertLesserThan(t1.update, first.update)
        self.assertEqual(t1.created, first.created)

    def test_model_random_datetime_setting_with_timestamp(self):
        t1 = DatetimeModel()
        t1.random = datetime.datetime(2000, 1, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc).timestamp()

        self.assertEqual(t1.random.day, 1)
        self.assertEqual(t1.random.year, 2000)
        self.assertEqual(t1.random.microsecond, 1)

        t1.save()

        saved = DatetimeModel.first()
        self.assertEqual(saved.random.day, 1)
        self.assertEqual(saved.random.year, 2000)
        self.assertEqual(saved.random.microsecond, 1)    

    def test_model_random_datetime_setting_with_datetime_object(self):
        t1 = DatetimeModel()
        t1.random = datetime.datetime(2000, 1, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc)

        self.assertEqual(t1.random.day, 1)
        self.assertEqual(t1.random.year, 2000)
        self.assertEqual(t1.random.microsecond, 1)

        t1.save()

        saved = DatetimeModel.first()
        self.assertEqual(saved.random.day, 1)
        self.assertEqual(saved.random.year, 2000)
        self.assertEqual(saved.random.microsecond, 1)

class DateModel(O.Model):
    created = Date(create_date=True)
    updated = Date(update_date=True)

    random = Date()

class TestDateFields(unittest.TestCase):
    def setUp(self):
        db.create_table('DateModels', default_cols(created='datetime', updated='datetime', random="datetime"))

    def tearDown(self):
        db.drop_table('DateModels')

    def test_model_initialization(self):
        t1 = DateModel()

        self.assertIs(t1.created, None)
        self.assertIs(t1.updated, None)
        self.assertIs(t1.random, None)

    @unittest.skip('Incomplete')
    def test_new_model_saved_creates_updated_and_created(self):
        t1 = DateModel()
        t1.save()

        self.assertIsInstance(t1.a, list)
        self.assertTrue(t1.a.conformable)

    def test_updated_model_changes_time(self):
        t1 = DateModel()
        t1.save()

        first = DateModel.first().save()

        self.assertLesserThan(t1.update, first.update)
        self.assertEqual(t1.created, first.created)

    def test_model_random_datetime_setting_with_timestamp(self):
        t1 = DateModel()
        t1.random = datetime.date(2000, 1, 1).timestamp()

        self.assertEqual(t1.random.day, 1)
        self.assertEqual(t1.random.year, 2000)

        t1.save()

        saved = DateModel.first()
        self.assertEqual(saved.random.day, 1)
        self.assertEqual(saved.random.year, 2000)

    def test_model_random_datetime_setting_with_datetime_object(self):
        t1 = DateModel()
        t1.random = datetime.datetime(2000, 1, 1)

        self.assertEqual(t1.random.day, 1)
        self.assertEqual(t1.random.year, 2000)

        t1.save()

        saved = DateModel.first()
        self.assertEqual(saved.random.day, 1)
        self.assertEqual(saved.random.year, 2000)

class TimeModel(O.Model):
    created = Time(create_date=True)
    updated = Time(update_date=True)

    random = Time()

class TestTimeFields(unittest.TestCase):
    def setUp(self):
        db.create_table('TimeModels', default_cols(created='time', updated='time', random="time"))

    def tearDown(self):
        db.drop_table('TimeModels')

    def test_model_initialization(self):
        t1 = TimeModel()

        self.assertIs(t1.created, None)
        self.assertIs(t1.updated, None)
        self.assertIs(t1.random, None)

    @unittest.skip('Incomplete')
    def test_new_model_saved_creates_updated_and_created(self):
        t1 = TimeModel()
        t1.save()

        self.assertIsInstance(t1.a, list)
        self.assertTrue(t1.a.conformable)

    def test_updated_model_changes_time(self):
        t1 = TimeModel()
        t1.save()

        first = TimeModel.first().save()

        self.assertLesserThan(t1.update, first.update)
        self.assertEqual(t1.created, first.created)

    def test_model_random_date_setting_with_date_object(self):
        t1 = TimeModel()
        t1.random = datetime.date(2000, 1, 1)

        self.assertEqual(t1.random.hour, 12)
        self.assertEqual(t1.random.second, 1)

        t1.save()

        saved = TimeModel.first()
        self.assertEqual(saved.random.hour, 12)
        self.assertEqual(saved.random.second, 1)