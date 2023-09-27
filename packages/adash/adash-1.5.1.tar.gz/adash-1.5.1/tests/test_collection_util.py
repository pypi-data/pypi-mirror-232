import src.adash as _


class TestAllkeys:
    def test_01(self):
        d = {"name": {"first": "John", "last": "Smith"}, "age": 36}
        res = _.allkeys(d)
        assert res == ["name.first", "name.last", "age"]

    def test_02(self):
        # https://json.org/example.html
        d = {
            "glossary": {
                "title": "example glossary",
                "GlossDiv": {
                    "title": "S",
                    "GlossList": {
                        "GlossEntry": {
                            "ID": "SGML",
                            "SortAs": "SGML",
                            "GlossTerm": "Standard Generalized Markup Language",
                            "Acronym": "SGML",
                            "Abbrev": "ISO 8879:1986",
                            "GlossDef": {
                                "para": "A meta-markup language, used to create markup languages such as DocBook.",
                                "GlossSeeAlso": ["GML", "XML"],
                            },
                            "GlossSee": "markup",
                        }
                    },
                },
            }
        }
        assert _.allkeys(d) == [
            "glossary.title",
            "glossary.GlossDiv.title",
            "glossary.GlossDiv.GlossList.GlossEntry.ID",
            "glossary.GlossDiv.GlossList.GlossEntry.SortAs",
            "glossary.GlossDiv.GlossList.GlossEntry.GlossTerm",
            "glossary.GlossDiv.GlossList.GlossEntry.Acronym",
            "glossary.GlossDiv.GlossList.GlossEntry.Abbrev",
            "glossary.GlossDiv.GlossList.GlossEntry.GlossDef.para",
            "glossary.GlossDiv.GlossList.GlossEntry.GlossDef.GlossSeeAlso",
            "glossary.GlossDiv.GlossList.GlossEntry.GlossSee",
        ]

    def test_03(self):
        assert _.allkeys({"a": 1, "b": 1}) == ["a", "b"]


class TestFind:
    def test_01(self):
        users = [
            {"user": "barney", "age": 36, "active": True},
            {"user": "fred", "age": 40, "active": False},
            {"user": "pebbles", "age": 1, "active": True},
        ]
        assert _.find(users, {"age": 1, "active": True}) == {
            "user": "pebbles",
            "age": 1,
            "active": True,
        }

    def test_02(self):
        users = [
            {"user": "barney", "age": 36, "active": True},
            {"user": "fred", "age": 40, "active": False},
            {"user": "pebbles", "age": 1, "active": True},
        ]
        assert _.find(users, "active") == {"user": "barney", "age": 36, "active": True}

    def test_03(self):
        users = [
            {"user": "barney", "age": 36, "active": True},
            {"user": "fred", "age": 40, "active": False},
            {"user": "pebbles", "age": 1, "active": True},
        ]
        assert _.find(users, lambda x: x["age"] < 40 or not x["active"]) == {
            "user": "barney",
            "age": 36,
            "active": True,
        }

    def test_04(self):
        items = ["apple", "banana", "cherry", "date"]
        assert _.find(items, lambda x: x.startswith("b")) == "banana"

    def test_05(self):
        items = ["apple", "banana", "cherry", "date"]
        assert _.find(items, "grape") is None

    def test_06(self):
        users = [
            {"user": "barney", "age": 36, "active": True},
            {"user": "fred", "age": 40, "active": False},
            {"user": "pebbles", "age": 1, "active": True},
        ]
        assert _.find(users, {"age": 100, "active": False}) is None
