import os

import unittest

from envargs import EnvParser
from envargs.errors import RequiredError, ParseError


class EnvParserTest(unittest.TestCase):

    def setUp(self) -> None:
        os.environ = dict()

    def test_description(self):
        ep = EnvParser()
        ep.add_variable("BOOL", type=bool, default=False)
        ep.add_variable("INT", type=int)
        ep.add_variable("STR", required=False)
        self.assertTrue(len(ep.description) > 0)

    def test_raises_required_error(self):
        ep = EnvParser()
        ep.add_variable("DUNT_EXIST")
        self.assertRaises(RequiredError, ep.parse_env)

    def test_bool_parse_error(self):
        os.environ["BOOLT"] = "yes"
        os.environ["BOOLF"] = "no"

        ep = EnvParser()
        ep.add_variable("BOOLT", type=bool)
        ep.add_variable("BOOLF", type=bool)
        self.assertRaises(ParseError, ep.parse_env)

    def test_primitives(self):
        os.environ["STR"] = "STR-val"
        os.environ["INT"] = "123"
        os.environ["FLOAT"] = "123.123"
        os.environ["BOOLF1"] = "false"
        os.environ["BOOLF2"] = "False"
        os.environ["BOOLF3"] = "0"
        os.environ["BOOLT1"] = "true"
        os.environ["BOOLT2"] = "True"
        os.environ["BOOLT3"] = "1"

        ep = EnvParser()
        ep.add_variable("STR")
        ep.add_variable("INT", type=int)
        ep.add_variable("FLOAT", type=float)
        ep.add_variable("BOOLF1", type=bool)
        ep.add_variable("BOOLF2", type=bool)
        ep.add_variable("BOOLF3", type=bool)
        ep.add_variable("BOOLT1", type=bool)
        ep.add_variable("BOOLT2", type=bool)
        ep.add_variable("BOOLT3", type=bool)
        ns = ep.parse_env()

        self.assertEqual(ns.str, "STR-val")
        self.assertEqual(ns.int, 123)
        self.assertEqual(ns.float, 123.123)
        self.assertEqual(ns.boolf1, False)
        self.assertEqual(ns.boolf2, False)
        self.assertEqual(ns.boolf3, False)
        self.assertEqual(ns.boolt1, True)
        self.assertEqual(ns.boolt2, True)
        self.assertEqual(ns.boolt3, True)

    def test_default(self):
        ep = EnvParser()
        ep.add_variable("STR", default="default-str")
        ep.add_variable("INT", type=int, default=12345)
        ep.add_variable("FLOAT", type=float, default=12345.12345)
        ep.add_variable("BOOL", type=bool, default=True)

        ns = ep.parse_env()

        self.assertEqual(ns.str, "default-str")
        self.assertEqual(ns.int, 12345)
        self.assertEqual(ns.float, 12345.12345)
        self.assertEqual(ns.bool, True)

    def test_dest(self):
        os.environ["STR"] = "STR-val"

        ep = EnvParser()
        ep.add_variable("STR", dest="sTr")
        ns = ep.parse_env()

        self.assertEqual(ns.sTr, "STR-val")
        self.assertRaises(AttributeError, lambda: ns.__getattribute__("str"))

    def test_raises_type_error(self):
        ep = EnvParser()
        self.assertRaises(TypeError,
                          lambda:
                          ep.add_variable("STR", type=str, default=123))

    def test_optional_without_default(self):
        ep = EnvParser()
        ep.add_variable("STR", required=False)

        ns = ep.parse_env()
        self.assertIsNone(ns.str)

    def test_raises_parse_error(self):
        os.environ["INT"] = "abc"

        ep = EnvParser()
        ep.add_variable("INT", type=int)

        self.assertRaises(ParseError, lambda: ep.parse_env())
