# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import io
import os
import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from nose.tools import *

from tgre import praat_reader, praat_string, tier_from_reader
from tgre import TextGrid, IntervalTier, TextTier, Interval, Point
from tgre.tgre import Tier


class TestPraatReader(object):
    empty_expected = ['ooTextFile', 'TextGrid', 0, 1, 3, 'IntervalTier',
                      'Mary', 0, 1, 1, 0, 1, 'def', 'IntervalTier', 'John', 0,
                      1, 2, 0, 0.5, 'abc', 0.5, 1, '', 'IntervalTier', 'Pat',
                      0, 1, 1, 0, 1, '']

    intervals_expected = ['ooTextFile', 'TextGrid', 0, 2.5, 2, 'IntervalTier',
                          'Pat', 0, 2.5, 2, 0, 0.65, 'hello', 0.65, 2.5, '',
                          'IntervalTier', 'Sam', 0, 2.5, 3, 0, 1.125, '',
                          1.125, 1.45, 'ciao', 1.45, 2.5, '']

    one_point_expected = ['ooTextFile', 'TextGrid', 0, 1, 1, 'TextTier',
                           'bell', 0, 1, 1, 0.5, 'asdf']

    quotes_expected = ['ooTextFile', 'TextGrid', 0.25, 1.5, 2, 'IntervalTier',
                        'words', 0.1, 1, 2, 0.1, 0.5, '"Is anyone home?"',
                        0.5, 1, 'asked "Pat"', 'TextTier', 'points', 0.1, 1,
                        2, 0.25, '"event"', 0.75, '"event" with quotes again']

    whitespace_sep_expected = ['ooTextFile', 'TextGrid', 0, 2.3, 3,
                               'IntervalTier', 'Mary', 0, 2.3, 1, 0, 2.3,
                               'abc', 'IntervalTier', 'John', 0, 2.3, 1, 0,
                               2.3, '', 'TextTier', 'bell', 0, 2.3, 0]

    def read(self, path):
        with io.open(path) as textgrid:
            textgrid_string = textgrid.read()

        return list(praat_reader(textgrid_string))

    def test_interval_tiers(self):
        tg_file = 'tests/files/intervals.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.intervals_expected)

    def test_empty_tier_and_text(self):
        tg_file = 'tests/files/interval-tiers-with-empty-tier-and-empty-text.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.empty_expected)

    def test_one_point(self):
        tg_file = 'tests/files/one-point.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.one_point_expected)

    def test_one_point_comments(self):
        tg_file = 'tests/files/one-point-with-comments.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.one_point_expected)

    def test_one_point_comments_inline(self):
        tg_file = 'tests/files/one-point-inline-comment-after-whitespace.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.one_point_expected)

    def test_one_point_comments_inline_no_sep(self):
        tg_file = 'tests/files/one-point-inline-comment-no-whitespace.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.one_point_expected)

    def test_doubled_quotes(self):
        tg_file = 'tests/files/doubled-quotes-in-text-and-mark.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.quotes_expected)

    def test_doubled_quotes_short_format(self):
        tg_file = 'tests/files/short-doubled-quotes.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.quotes_expected)

    def test_various_whitespace_sep_custom_format(self):
        tg_file = 'tests/files/custom-intervals-points-various-whitespace.TextGrid'
        elements = self.read(tg_file)

        assert_equal(elements, self.whitespace_sep_expected)


class TestPraatString(object):
    def test_praat_string(self):
        assert_equal(praat_string('abc'), '"abc"')

    def test_praat_string_quotes(self):
        assert_equal(praat_string('a"b"c'), '"a""b""c"')


class TestTierFromReader(object):
    @mock.patch('tgre.tgre.IntervalTier')
    def test_interval_tier(self, IntervalTierMock):
        stream = iter(['IntervalTier'])
        tier = tier_from_reader(stream)

        assert_in(mock.call.from_reader(stream),
                  IntervalTierMock.method_calls)

    @mock.patch('tgre.tgre.TextTier')
    def test_text_tier(self, TextTierMock):
        stream = iter(['TextTier'])
        tier = tier_from_reader(stream)

        assert_in(mock.call.from_reader(stream),
                  TextTierMock.method_calls)

    def test_bad_tier(self):
        stream = iter(['BadTierName'])

        with assert_raises(ValueError):
            tier_from_reader(stream)


class TestTextGrid(object):
    def test_init(self):
        tg = TextGrid(0, 1, [])

        assert_equal(tg.xmin, 0)
        assert_equal(tg.xmax, 1)
        assert_equal(tg.tiers, [])

    @mock.patch('tgre.tgre.tier_from_reader')
    def test_from_reader(self, TierFromReaderMock):
        TierFromReaderMock.return_value = 'tier'
        stream = iter([0, 1, 2])

        tg = TextGrid.from_reader(stream)

        assert_equal(tg.xmin, 0)
        assert_equal(tg.xmax, 1)
        assert_equal(tg.tiers, ['tier', 'tier'])

    @mock.patch('tgre.tgre.tier_from_reader')
    def test_from_reader_wrong_size(self, TierFromReaderMock):
        TierFromReaderMock.return_value = 'tier'
        stream = iter([0, 1, 2, 'extra_value'])

        with assert_raises(ValueError):
            TextGrid.from_reader(stream)

    def test_repr(self):
        tg = TextGrid(0, 1, [1, 2, 3])
        assert_equal(repr(tg), "TextGrid(0, 1, [1, 2, 3])")

    def test_str(self):
        tg = TextGrid(0, 1, [1, 2, 3])
        assert_equal(str(tg), '<TextGrid from 0 to 1 seconds with 3 tiers>')

    def test_to_dict(self):
        mock_tier = mock.Mock()
        mock_tier.to_dict.return_value = {'a tier': 'data'}

        tg = TextGrid(0, 1, [mock_tier])
        res = tg.to_dict()

        assert_equal(res, {'xmin': 0,
                           'xmax': 1,
                           'tiers': [{'a tier': 'data'}]})

    def test_to_praat(self):
        mock_tier = mock.Mock()
        mock_tier.xmin = 0
        mock_tier.xmax = 1
        mock_tier.to_praat.return_value = 'a tier'

        tg = TextGrid(0, 1, [mock_tier, mock_tier])
        res = tg.to_praat()

        assert_equal(res, ('"ooTextFile"\n"TextGrid"\n'
                           '0 to 1 seconds <exists>\n'
                           '2 tiers\n\na tier\n\na tier'))

    def test_to_praat_starts_before(self):
        mock_tier = mock.Mock()
        mock_tier.xmin = 0
        mock_tier.xmax = 1

        tg = TextGrid(0.5, 1, [mock_tier])

        with assert_raises(ValueError):
            tg.to_praat()

    def test_to_praat_starts_after(self):
        mock_tier = mock.Mock()
        mock_tier.xmin = 0.5
        mock_tier.xmax = 1

        tg = TextGrid(0, 1, [mock_tier])

        with assert_raises(ValueError):
            tg.to_praat()

    def test_to_praat_ends_before(self):
        mock_tier = mock.Mock()
        mock_tier.xmin = 0
        mock_tier.xmax = 1

        tg = TextGrid(0, 1.5, [mock_tier])

        with assert_raises(ValueError):
            tg.to_praat()

    def test_to_praat_ends_after(self):
        mock_tier = mock.Mock()
        mock_tier.xmin = 0
        mock_tier.xmax = 1

        tg = TextGrid(0, 0.5, [mock_tier])

        with assert_raises(ValueError):
            tg.to_praat()

    def test_get(self):
        tg = TextGrid(0, 1, ['tier 0', 'tier 1'])
        assert_equal(tg[1], 'tier 1')

    def test_set(self):
        tg = TextGrid(0, 1, ['tier 0', 'tier 1'])
        tg[1] = 'new tier'
        assert_equal(tg[1], 'new tier')

    def test_del(self):
        tg = TextGrid(0, 1, ['tier 0', 'tier 1'])
        del tg[0]
        assert_equal(tg[0], 'tier 1')

    def test_len(self):
        tg = TextGrid(0, 1, ['tier 0', 'tier 1'])
        assert_equal(len(tg), 2)

    def test_reversed(self):
        tg = TextGrid(0, 1, ['tier 0', 'tier 1'])
        assert_equal(list(reversed(tg)), ['tier 1', 'tier 0'])

    def test_iter(self):
        tg = TextGrid(0, 1, ['tier 0', 'tier 1'])
        assert_equal(list(iter(tg)), ['tier 0', 'tier 1'])


class TestTextGridIO(object):
    def test_from_file(self):
        tg_file = 'tests/files/doubled-quotes-in-text-and-mark.TextGrid'
        tg = TextGrid.from_file(tg_file)

        assert_equal(tg.xmin, 0.25)
        assert_equal(tg.xmax, 1.5)
        assert_equal(len(tg.tiers), 2)

        assert_is(tg.tiers[0].__class__, IntervalTier)
        assert_equal(tg.tiers[0].name, 'words')
        assert_equal(tg.tiers[0].xmin, 0.1)
        assert_equal(tg.tiers[0].xmax, 1)
        assert_equal(len(tg.tiers[0]._items), 2)

        assert_equal(tg.tiers[0]._items[0].xmin, 0.1)
        assert_equal(tg.tiers[0]._items[0].xmax, 0.5)
        assert_equal(tg.tiers[0]._items[0].text, '"Is anyone home?"')
        assert_equal(tg.tiers[0]._items[1].xmin, 0.5)
        assert_equal(tg.tiers[0]._items[1].xmax, 1)
        assert_equal(tg.tiers[0]._items[1].text, 'asked "Pat"')

        assert_is(tg.tiers[1].__class__, TextTier)
        assert_equal(tg.tiers[1].name, 'points')
        assert_equal(tg.tiers[1].xmin, 0.1)
        assert_equal(tg.tiers[1].xmax, 1)
        assert_equal(len(tg.tiers[1]._items), 2)

        assert_equal(tg.tiers[1]._items[0].number, 0.25)
        assert_equal(tg.tiers[1]._items[0].mark, '"event"')
        assert_equal(tg.tiers[1]._items[1].number, 0.75)
        assert_equal(tg.tiers[1]._items[1].mark, '"event" with quotes again')

    def test_from_file_armenian(self):
        tg = TextGrid.from_file('tests/files/numbers.TextGrid', encoding='utf_16')

        assert_equal(tg.tiers[0][0].text, u'մեկ')
        assert_equal(tg.tiers[0][1].text, u'երկու')
        assert_equal(tg.tiers[0][2].text, u'երեք')
        assert_equal(tg.tiers[0][3].text, u'չորս')

    def test_utf8_bom(self):
        # BOM should be skipped by regex
        tg = TextGrid.from_file('tests/files/intervals-utf8-bom.TextGrid')
        assert_equal(tg.tiers[1][1].text, 'ciao')

    def test_from_file_missing_header(self):
        with assert_raises(ValueError):
            TextGrid.from_file('tests/files/intervals-no-filetype.TextGrid')

        with assert_raises(ValueError):
            TextGrid.from_file('tests/files/intervals-no-object-class.TextGrid')

    def test_to_praat_with_path(self):
        mock_tier = mock.Mock()
        mock_tier.xmin = 0
        mock_tier.xmax = 1
        mock_tier.to_praat.return_value = 'a tier'

        tg = TextGrid(0, 1, [mock_tier, mock_tier])
        tg.to_praat('tests/files/output.TextGrid')

        with open('tests/files/output.TextGrid') as output_file:
            res = output_file.read()

        assert_equal(res, ('"ooTextFile"\n"TextGrid"\n'
                           '0 to 1 seconds <exists>\n'
                           '2 tiers\n\na tier\n\na tier'))

    @classmethod
    def teardown_class(cls):
        os.remove('tests/files/output.TextGrid')


class TestInterval(object):
    @classmethod
    def setup_class(cls):
        cls.int1 = Interval(0.5, 2.5, 'abc')
        cls.int2 = Interval(0.65, 2.5, 'abc')

    def test_init(self):
        assert_equal(self.int1.xmin, 0.5)
        assert_equal(self.int1.xmax, 2.5)
        assert_equal(self.int1.text, 'abc')

    def test_from_reader(self):
        stream = iter([0.5, 2.5, 'abc'])
        interval = Interval.from_reader(stream)

        assert_equal(interval.xmin, 0.5)
        assert_equal(interval.xmax, 2.5)
        assert_equal(interval.text, 'abc')

    def test_lt(self):
        assert_less(self.int1, self.int2)

    def test_gt(self):
        assert_greater(self.int2, self.int1)

    def test_intervals_are_not_equal(self):
        interval = Interval(0.5, 2.5, 'abc')
        assert_not_equal(self.int1, interval)

    def test_repr(self):
        assert_equal(repr(self.int1), "Interval(0.5, 2.5, 'abc')")

    def test_str(self):
        assert_equal(str(self.int1), '<Interval "abc" from 0.5 to 2.5>')

    def test_to_praat(self):
        res = self.int1.to_praat()
        expected = '                     0.5                     2.5    "abc" '

        assert_equal(res, expected)


class TestPoint(object):
    @classmethod
    def setup_class(cls):
        cls.point1 = Point(0.5, 'abc')
        cls.point2 = Point(0.65, 'abc')

    def test_init(self):
        assert_equal(self.point1.number, 0.5)
        assert_equal(self.point1.mark, 'abc')

    def test_from_reader(self):
        stream = iter([0.5, 'abc'])
        point = Point.from_reader(stream)

        assert_equal(point.number, 0.5)
        assert_equal(point.mark, 'abc')

    def test_lt(self):
        assert_less(self.point1, self.point2)

    def test_gt(self):
        assert_greater(self.point2, self.point1)

    def test_points_are_not_equal(self):
        point = Point(0.5, 'abc')
        assert_not_equal(self.point1, point)

    def test_repr(self):
        assert_equal(repr(self.point1), "Point(0.5, 'abc')")

    def test_str(self):
        assert_equal(str(self.point1), '<Point "abc" at 0.5>')

    def test_to_praat(self):
        res = self.point1.to_praat()
        expected = '                     0.5    "abc" '

        assert_equal(res, expected)


class TestTier(object):
    def test_init(self):
        tier = Tier('abc', 0, 1, [4, 2, 3])

        assert_equal(tier.name, 'abc')
        assert_equal(tier.xmin, 0)
        assert_equal(tier.xmax, 1)
        assert_equal(tier._items, [2, 3, 4])

    def test_init_no_items(self):
        tier = Tier('abc', 0, 1)

        assert_equal(tier.name, 'abc')
        assert_equal(tier.xmin, 0)
        assert_equal(tier.xmax, 1)
        assert_equal(tier._items, [])

    def test_init_unsortable(self):
        with assert_raises(TypeError):
            Tier('abc', 0, 1, [Interval(0, 1, 'abc'), Point(0.5, 'abc')])

    def test_get(self):
        tier = Tier('abc', 0, 1, ['a', 'b', 'c'])
        assert_equal(tier[1], 'b')

    def test_slice(self):
        tier = Tier('abc', 0, 1, ['a', 'b', 'c', 'd'])
        assert_equal(tier[1:3], ['b', 'c'])

    def test_del(self):
        tier = Tier('abc', 0, 1, ['a', 'b', 'c'])
        del tier[1]
        assert_equal(tier[1], 'c')

    def test_reversed(self):
        tier = Tier('abc', 0, 1, ['a', 'b', 'c'])
        assert_equal(list(reversed(tier)), ['c', 'b', 'a'])

    def test_iter(self):
        tier = Tier('abc', 0, 1, ['a', 'b', 'c'])
        assert_equal(list(iter(tier)), ['a', 'b', 'c'])

    def test_len(self):
        tier = Tier('abc', 0, 1, ['a', 'b', 'c'])
        assert_equal(len(tier), 3)


class TestIntervalTier(object):
    def test_insert(self):
        int1 = Interval(0, 0.5, 'a')
        int2 = Interval(0.75, 1, 'c')
        tier = IntervalTier('abc', 0, 1, [int1, int2])

        tier.insert(0.5, 0.75, 'b')

        assert_is(tier[0], int1)
        assert_is(tier[2], int2)

        assert_equal(tier[1].xmin, 0.5)
        assert_equal(tier[1].xmax, 0.75)
        assert_equal(tier[1].text, 'b')

    @mock.patch('tgre.tgre.IntervalTier.item')
    def test_from_reader(self, IntervalMock):
        IntervalMock.from_reader.return_value = 'an interval'

        stream = iter(['abc', 0, 1, 2])

        tier = IntervalTier.from_reader(stream)

        assert_equal(tier.name, 'abc')
        assert_equal(tier.xmin, 0)
        assert_equal(tier.xmax, 1)
        assert_equal(tier._items, ['an interval', 'an interval'])

    def test_repr(self):
        int1 = Interval(0, 0.5, 'a')
        int2 = Interval(0.75, 1, 'c')
        tier = IntervalTier('abc', 0, 1, [int1, int2])

        assert_equal(repr(tier), "IntervalTier('abc', 0, 1, "
                                 "[Interval(0, 0.5, 'a'), "
                                 "Interval(0.75, 1, 'c')])")

    def test_str(self):
        int1 = Interval(0, 0.5, 'a')
        int2 = Interval(0.75, 1, 'c')
        tier = IntervalTier('abc', 0, 1, [int1, int2])

        assert_equal(str(tier), '<IntervalTier "abc" from 0 to 1 seconds '
                                'with 2 intervals>')

    def test_where(self):
        int1 = Interval(0, 0.5, 'a')
        int2 = Interval(0.5, 0.6, 'b')
        int3 = Interval(0.75, 1, 'c')
        tier = IntervalTier('abc', 0, 1, [int1, int2, int3])

        assert_is(tier.where(0), int1)
        assert_is(tier.where(0.25), int1)

        assert_is(tier.where(0.5), int2)
        assert_is(tier.where(0.55), int2)

        assert_is_none(tier.where(0.6))
        assert_is_none(tier.where(0.65))

        assert_is(tier.where(0.75), int3)
        assert_is(tier.where(0.8), int3)

        assert_is_none(tier.where(1))

    def test_where_out_of_bounds(self):
        interval = Interval(0.35, 0.5, 'a')
        tier = IntervalTier('abc', 0.25, 1, [interval])

        assert_is_none(tier.where(0.1))
        assert_is_none(tier.where(1.5))

    def test_to_dict(self):
        interval = Interval(0.35, 0.5, 'a')
        tier = IntervalTier('abc', 0.25, 1, [interval])

        assert_equal(tier.to_dict(), {'xmin': 0.25,
                                      'xmax': 1,
                                      'name': 'abc',
                                      'class': 'IntervalTier',
                                      'intervals': [{'xmin': 0.35,
                                                     'xmax': 0.5,
                                                     'text': 'a'}]})

    def test_to_praat(self):
        interval = Interval(0.35, 0.5, 'a')
        tier = IntervalTier('abc', 0.25, 1, [interval])

        expected = ('"IntervalTier" named "abc" \n'
                    'From 0.25 to 1 seconds with 3 intervals\n'
                    '                    0.25                    0.35    '
                    '"" \n'
                    '                    0.35                     0.5    '
                    '"a" \n'
                    '                     0.5                       1    '
                    '"" ')

        assert_equal(tier.to_praat(), expected)

    def test_to_praat_reversed_interval(self):
        interval = Interval(0.5, 0.35, 'a')
        tier = IntervalTier('abc', 0.25, 1, [interval])

        with assert_raises(ValueError):
            tier.to_praat()

    def test_to_praat_early_interval(self):
        interval = Interval(0.1, 0.35, 'a')
        tier = IntervalTier('abc', 0.25, 1, [interval])

        with assert_raises(ValueError):
            tier.to_praat()

    def test_to_praat_overlapping_intervals(self):
        int1 = Interval(0.25, 0.35, 'a')
        int2 = Interval(0.3, 0.4, 'a')
        tier = IntervalTier('abc', 0.25, 1, [int1, int2])

        with assert_raises(ValueError):
            tier.to_praat()

    def test_to_praat_late_interval(self):
        interval = Interval(0.25, 1.5, 'a')
        tier = IntervalTier('abc', 0.25, 1, [interval])

        with assert_raises(ValueError):
            tier.to_praat()


class TestTextTier(object):
    def test_insert(self):
        point1 = Point(0.5, 'a')
        point2 = Point(0.75, 'c')
        tier = TextTier('abc', 0, 1, [point1, point2])

        tier.insert(0.6, 'b')

        assert_is(tier[0], point1)
        assert_is(tier[2], point2)

        assert_equal(tier[1].number, 0.6)
        assert_equal(tier[1].mark, 'b')

    @mock.patch('tgre.tgre.TextTier.item')
    def test_from_reader(self, PointMock):
        PointMock.from_reader.return_value = 'a point'

        stream = iter(['abc', 0, 1, 2])

        tier = TextTier.from_reader(stream)

        assert_equal(tier.name, 'abc')
        assert_equal(tier.xmin, 0)
        assert_equal(tier.xmax, 1)
        assert_equal(tier._items, ['a point', 'a point'])

    def test_repr(self):
        point1 = Point(0.5, 'a')
        point2 = Point(0.75, 'c')
        tier = TextTier('abc', 0, 1, [point1, point2])

        assert_equal(repr(tier), "TextTier('abc', 0, 1, "
                                 "[Point(0.5, 'a'), Point(0.75, 'c')])")

    def test_str(self):
        point1 = Point(0.5, 'a')
        point2 = Point(0.75, 'c')
        tier = TextTier('abc', 0, 1, [point1, point2])

        expected = '<TextTier "abc" from 0 to 1 seconds with 2 points>'

        assert_equal(str(tier), expected)

    def test_where_left(self):
        point = Point(0.5, 'a')
        tier = TextTier('abc', 0, 1, [point])

        assert_is_none(tier.where(0.25))
        assert_is(tier.where(0.5), point)
        assert_is_none(tier.where(0.75))

    def test_where_left_out_of_bounds(self):
        point = Point(0.5, 'a')
        tier = TextTier('abc', 0.25, 1, [point])

        assert_is_none(tier.where(0.1))
        assert_is_none(tier.where(1.5))

    def test_where_range(self):
        point1 = Point(0.5, 'a')
        point2 = Point(0.75, 'c')
        tier = TextTier('abc', 0, 1, [point1, point2])

        assert_equal(tier.where(0, 0.25), [])
        assert_equal(tier.where(0.25, 0.5), [point1])
        assert_equal(tier.where(0.4, 0.6), [point1])
        assert_equal(tier.where(0.5, 0.6), [point1])

        assert_equal(tier.where(0.6, 0.7), [])
        assert_equal(tier.where(0.6, 0.75), [point2])
        assert_equal(tier.where(0.7, 1), [point2])

        assert_equal(tier.where(0, 1), [point1, point2])
        assert_equal(tier.where(0.25, 1), [point1, point2])
        assert_equal(tier.where(0.5, 0.75), [point1, point2])

    def test_where_range_out_of_bounds(self):
        point1 = Point(0.5, 'a')
        point2 = Point(0.75, 'c')
        tier = TextTier('abc', 0.25, 1, [point1, point2])

        assert_equal(tier.where(0.1, 0.2), [])
        assert_equal(tier.where(0.1, 0.25), [])
        assert_equal(tier.where(0.1, 0.5), [point1])
        assert_equal(tier.where(0.1, 0.6), [point1])

        assert_equal(tier.where(0.6, 1.5), [point2])
        assert_equal(tier.where(0.75, 1.5), [point2])
        assert_equal(tier.where(0.8, 1.5), [])
        assert_equal(tier.where(1.1, 1.5), [])

    def test_to_dict(self):
        point = Point(0.35, 'a')
        tier = TextTier('abc', 0.25, 1, [point])

        assert_equal(tier.to_dict(), {'xmin': 0.25,
                                      'xmax': 1,
                                      'name': 'abc',
                                      'class': 'TextTier',
                                      'points': [{'number': 0.35,
                                                  'mark': 'a'}]})

    def test_to_praat(self):
        point = Point(0.35, 'a')
        tier = TextTier('abc', 0.25, 1, [point])

        expected = ('"TextTier" named "abc" \n'
                    'From 0.25 to 1 seconds with 1 points\n'
                    '                    0.35    "a" ')

        assert_equal(tier.to_praat(), expected)

    def test_to_praat_early_point(self):
        point = Point(0.1, 'a')
        tier = TextTier('abc', 0.25, 1, [point])

        with assert_raises(ValueError):
            tier.to_praat()

    def test_to_praat_late_point(self):
        point = Point(1.5, 'a')
        tier = TextTier('abc', 0.25, 1, [point])

        with assert_raises(ValueError):
            tier.to_praat()

    def test_to_praat_overlapping_points(self):
        point1 = Point(1.5, 'a')
        point2 = Point(1.5, 'b')
        tier = TextTier('abc', 1, 2, [point1, point2])

        with assert_raises(ValueError):
            tier.to_praat()
