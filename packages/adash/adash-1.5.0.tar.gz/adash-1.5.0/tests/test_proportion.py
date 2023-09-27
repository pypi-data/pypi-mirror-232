from math import isnan
import src.adash as _


class TestProportion:
    def test_01(self):
        _p = _.proportion
        assert _p(100, 99) == -1
        assert _p(203, 7) == -96.55
        assert _p(203, 7, "0.001") == -96.552
        assert _p(0.25, 0.51) == 104
        assert _p(100, 25) == -75
        assert _p(10, 0) == -100
        assert _p(1, 9) == 800
        assert isnan(_p(0, 25))
        assert isnan(_p(None, 0))


class TestProgressRate:
    def test_01(self):
        _p = _.progress_rate
        assert _p(-50, -50) == 100
        assert _p(-50, -45) == 110
        assert _p(-50, -70) == 60
        assert _p(-50, 0) == 200
        assert _p(-50, 50) == 300
        assert _p(50, -50) == -100
        assert _p(50, -45) == -90
        assert _p(50, -70) == -140
        assert _p(50, 0) == 0
        assert _p(50, 50) == 100
        assert _p(50, 12.031454) == 24.06
        assert _p(50, 12.031454, "0.00001") == 24.06291
        assert isnan(_p(0, -50))
        assert isnan(_p(None, -50))
