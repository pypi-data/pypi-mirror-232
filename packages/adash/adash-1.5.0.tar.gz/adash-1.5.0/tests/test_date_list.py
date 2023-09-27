import src.adash as _


def test_date_list_1():
    dl = _.date_list(40)
    assert len(dl) == 40


def test_date_list_2():
    dl = _.date_list(3, "2020-12-1")
    assert dl == ["2020-11-29", "2020-11-30", "2020-12-01"]
    assert dl == _.date_list(3, "2020-12-01")


def test_date_list_3():
    dl = _.date_list(3, "20201201", "%Y%m%d")
    assert dl == ["20201129", "20201130", "20201201"]


def test_date_list_4():
    dl = _.date_list(3, "2020-12-01", rev=True)
    assert dl == ["2020-12-01", "2020-11-30", "2020-11-29"]
