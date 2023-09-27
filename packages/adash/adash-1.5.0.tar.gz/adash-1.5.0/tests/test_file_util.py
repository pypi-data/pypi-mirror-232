import pytest
import pathlib
import src.adash as _


class TestDownload:
    @pytest.fixture()
    def path(self):
        _p = "tmp/hello.js"
        yield _p
        _p = pathlib.Path(_p)
        if _p.exists():
            pathlib.Path(_p).unlink()

    def test_download(self, path):
        url = "https://cdn.jsdelivr.net/npm/js-hello-world@1.0.0/helloWorld.js"
        p = pathlib.Path(path)
        assert not p.exists()
        assert _.download(url, p) == 1
        assert _.download(url, path) == 0
        text = p.read_text()
        assert 'console.log("Hello World");' in text

    def test_download_unknown(self, path):
        url = "https://www.google.com/example"
        with pytest.warns(UserWarning) as record:
            assert _.download(url, "down_test.html") == 0
            assert record[0].message.args[0] == "404: Not Found"
            assert record[1].message.args[0] == "url: https://www.google.com/example"


class TestJson:
    @pytest.fixture()
    def path(self):
        _p = "tmp/sample.json"
        yield _p
        pathlib.Path(_p).unlink()

    @pytest.fixture()
    def ppath(self):
        _p = pathlib.Path("sample.json")
        yield _p
        pathlib.Path(_p).unlink()

    def test_json(self, path):
        assert _.json_write({"a": 1}, path) == 1
        assert _.json_write({"a": 1}, path, overwrite=True) == 1
        assert _.json_read(path) == {"a": 1}
        assert _.json_write({"a": 1}, path) == 0

    def test_json_pathlib(self, ppath):
        assert _.json_write({"a": 1}, ppath) == 1
        assert _.json_write({"a": 1}, ppath, overwrite=True) == 1
        assert _.json_read(ppath) == {"a": 1}
        assert _.json_write({"a": 1}, ppath) == 0


class TestCat:
    @pytest.fixture()
    def path(self):
        _p = "tmp/hello.js"
        _.json_write({"a": 1}, _p)
        yield _p
        _p = pathlib.Path(_p)
        if _p.exists():
            pathlib.Path(_p).unlink()

    def test_cat(self, path):
        s = _.cat("tmp/hello.js")
        assert s == '{"a": 1}'

    def test_cat_is_none(self, path):
        s = _.cat("tmp/unknown.js")
        assert s is None
