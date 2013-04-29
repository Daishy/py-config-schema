"""
Tests for the *configguard*-system
"""


import unittest
from exceptions import ConfigValidationError, ConfigValidatorError
from core import ConfigValidator
from tokens import Int, String, Bool, Dict
from decorator import Range, Length, NotEmpty


class ConfigValidatorTests(unittest.TestCase):
    """ Class for testing the Configguard """
    
    def assertValidates(self, config_definition, struct, expected_result=None):
        cv = ConfigValidator(config_definition)
        res = cv.validate(struct)
        if expected_result:
            self.assertEqual(res, expected_result)
        return res
    
    def assertFails(self, config_definition, struct):
        cv = ConfigValidator(config_definition)
        with self.assertRaises(ConfigValidationError):
            cv.validate(struct)
            
            
    def test_fill_in_from_defaults(self):
        self.assertValidates({"a": Int(default=2)}, {}, expected_result={"a":2})
    
    
    def test_basic_types_int(self):
        # Check basic values
        self.assertValidates(int, 1)
        self.assertValidates(int, 0)
        self.assertValidates(Int(), 1)
        
        # check it fails without anything else
        self.assertFails(int, None)
        
        # check with required=false this is ok
        self.assertValidates(Int(required=False), None)
        
        # Check default is used
        self.assertValidates(Int(default=0), None, 0)
        
        # Check type-check is correct
        self.assertFails(int, "1")
        
    def test_basic_types_string(self):
        # Check Basic values
        self.assertValidates(str, "test")
        self.assertValidates(str, u"unicode")
        self.assertValidates(String(), "test")
        
        # Empty values should validate
        self.assertValidates(str, "")
        self.assertValidates(String(required=False), None)
        
    def test_basic_types_bool(self):
        self.assertValidates(bool, True)
        self.assertValidates(bool, False)
        self.assertValidates(Bool(), True)
        
        self.assertFails(bool, "true")
        self.assertFails(bool, 1)
        
        self.assertFails(bool, None)
        self.assertValidates(Bool(required=False), None)
        
    def test_basic_types_dict(self):
        self.assertValidates({"a": int}, {"a": 1})
        
        
    def test_basic_types_dict_allow_extra_keys(self):
        self.assertFails({"a": int}, {"a":1, "b":2})
        self.assertValidates(
            {"a": int, "__allow_extra_keys__": True},
            {"a": 1, "b": 2})
            
    def test_basic_types_dict_required_keyword(self):
        self.assertValidates(
            {"a": {"a1":int}, "b":{"b1":int, "__required__": False}},
            {"a": {"a1": 1}})
        self.assertFails(
            {"a": {"a1":int}, "b":{"b1":int, "__required__": True}},
            {"a": {"a1": 1}})            
        self.assertFails(
            {"a": {"a1":int}, "b":{"b1":int}},
            {"a": {"a1": 1}, "b":{}})
        
        
    def test_decorators_range(self):
        """ """
        # Check with int
        self.assertValidates(Range(int, min=0, max=5), 4)
        self.assertValidates(Range(int, max=0), -1)
        self.assertValidates(Range(int, max=0), 0)
        self.assertValidates(Range(int, min=0), 4)
        self.assertValidates(Range(Int(), min=0), 4)
        
        # Check range fails
        self.assertFails(Range(int, min=0), -4)
        self.assertFails(Range(int, max=0), 4)
        
        # Check with required=false
        self.assertValidates(Range(Int(required=False), min=0), None)
        self.assertValidates(Range(Int(required=False), max=0), None)
        
        # Check with default-value
        self.assertValidates(Range(Int(default=1), min=0), None)
        self.assertValidates(Range(Int(default=1), max=10), None)
        
        # Check with floats
        # TODO
        
    def test_decorators_length(self):
        # With strings
        self.assertValidates(Length(str, min=3), "123")
        self.assertFails(Length(str, min=3), "12")
        
        self.assertValidates(Length(str, max=5), "1234")
        self.assertFails(Length(str, max=3), "1234")
        
        self.assertValidates(Length(str, length=3), "123")
        self.assertFails(Length(str, length=4), "123")
        
        self.assertFails(Length(str, length=3, min=4), "123")
        
        # With Ints
        self.assertValidates(Length(int, min=3), 123)
        self.assertFails(Length(int, min=3), 12)
    
    
    def test_decorators_notempty(self):
        self.assertValidates(NotEmpty(str), "123")
        self.assertFails(NotEmpty(str), "")
 
 
    def test_complex_configs(self):
        """ Test some more complex Configs """
        config = {
            "name": str,
            "version": Range(int, min=1),
            "debug": Bool(default=False),
            "sub": {
                "sub1": String(required=False)
            },
            
        }
        
        self.assertValidates(config, {"name": "a", "version": 1, "debug": True, "sub":{"sub1": "test"}})
        
        self.assertValidates(config, {"name": "a", "version": 1, "sub": {"sub1": "Test"}})
        self.assertValidates(config, {"name": "a", "version": 2, "sub": {}})
        
        
        

unittest.main()