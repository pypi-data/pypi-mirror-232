from math import isnan

import src.adash as _


class TestReplaceAll:
    def test_01(self):
        s = "3円00銭"
        obj = {"円": ".", "銭": ""}
        assert _.replace_all(s, obj) == "3.00"

    def test_02(self):
        s = "abcabc"
        obj = {"a": "!", "b": "", "c": "?"}
        assert _.replace_all(s, obj) == "!?!?"

    def test_03(self):
        obj = {"[△▲]": "-", "[,、]": ""}
        assert _.replace_all("▲12,345", obj) == _.replace_all("△12、345", obj)


class TestHalfString:
    def test_01(self):
        assert _.to_half_string("１２３４５ａｂｃ") == "12345abc"


class TestToNumber:
    def test_01(self):
        assert _.to_number("123,456") == 123456
        assert _.to_number("-123,456") == -123456
        assert _.to_number("▲123,456") == -123456
        assert _.to_number("△123,456") == -123456
        assert isnan(_.to_number("▼123,456"))
        assert isnan(_.to_number("abc"))
        assert _.to_number("abc", True) is True
        assert _.to_number("abc", False) is False
        assert _.to_number("18円32銭") == 18.32
        assert _.to_number("18円00銭") == 18
        assert _.to_number("18円") == 18
        assert _.to_number("18%") == 18
        assert _.to_number("18％") == 18
        assert _.to_number("１２３，４５６，７８９") == 123456789


class TestToDate:
    def test_01(self):
        td = _.to_date
        assert td("２０１８年５月２７日") == "2018-05-27"
        assert td("2018年1月1日") == "2018-01-01"
        assert td("平成30年 5月11日") == "2018-05-11"
        assert td("令和元年 5月11日") == "2019-05-11"
        assert td("令和 元年 5月12日") == "2019-05-12"
        assert td("令和2年 5月11日") == "2020-05-11"
        assert td("平成３０年５月２７日") == "2018-05-27"
        assert td("昭和３０年５月２７日") == "1955-05-27"
        assert td("大正３年５月２７日") == "1914-05-27"
        assert td("大３年５月２７日") == "1914-05-27"
        assert td("明３年５月２７日") == "1870-05-27"
        assert td("2018-5-27") == "2018-05-27"
        assert td("2018/5/27") == "2018-05-27"
        assert td("20180527") == "2018-05-27"
        assert td("Unknown") is None


class TestSplitUpperCase:
    def test_01(self):
        assert _.split_uppercase("IsJSON") == ["Is", "JSON"]
        assert _.split_uppercase("ILoveYou") == ["ILove", "You"]
        assert _.split_uppercase("NextAccumulatedQ2Duration") == [
            "Next",
            "Accumulated",
            "Q2",
            "Duration",
        ]


class TestHash:
    def test_md5(self):
        assert _.to_md5("test") == "098f6bcd4621d373cade4e832627b4f6"
        assert _.to_md5("test1") == "5a105e8b9d40e1329780d62ea2265d8a"

    def test_sha256(self):
        assert (
            _.to_sha256("test")
            == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )
        assert (
            _.to_sha256("test1")
            == "1b4f0e9851971998e732078544c96b36c3d01cedf7caa332359d6f1d83567014"
        )


class TestTextNormalize:
    def test_01(self):
        assert _.text_normalize("ﾊﾝｶｸｶﾀｶﾅｚｅｎｋａｋｕ１２３") == "ハンカクカタカナzenkaku123"
        assert _.text_normalize("①②③１２３") == "①②③123"
        assert _.text_normalize("①②③１２３", exclude_chars="①１") == "①23１23"
