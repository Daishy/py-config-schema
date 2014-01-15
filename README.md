# py-data-schema #

`py-data-schema` is a little library to create schemas which are able to validate complex python data structurs, with capability to provide [defaults](#defaults), [validate flexible key-value-pairs in dicts](#flexible-keys), [converting input](#call). Furthermore it
provides a few additional validators, for example Length or Regex-Matching.

This library was primarily created, to validate configuration-files and provide defaults for config-values, but on the way it
got some additional features and i'm currently planning on using it for user-input validation too, so there may be some more `Token`s comming

This library is influenced/inspired by [Voluptuous](https://github.com/alecthomas/voluptuous)

Below a few examples, the README is still a bit empty, but i plan to expand it...
**This is currently growing as i need tokens, so if anything is missing please just leave an issue, chances are, i'll need it anyway :D ***



Simple schema, which validates a dictionary:
```
schema = Dict({
	"some_key": int, # automatic conversion from basic types to validated types
	"some_other_key": Bool(default=True) # Provide defaults
	"x": String(required=False) # Mark entries as not required
})

schema.validate({
	"some_key": 1
})

Results in:
{
	"some_key": 1,
	"some_other_key": True
}
```

Using flexible keys in dictionaries:
```
schema = Dict({
	int: Bool(desc="This is a short description of what we are storing here"),
	str: object,
	"main": String()
})
schema.validate({
	1: True,
	2: False
	3: True
	"some_string": 12,
	"some_other_string": True,
	"main": "This string is mandatory in the input!"
})
```


## Basics ##
The main class is `Schema`. This class should be the entry-point for creating a schema. The constructor takes any valid
schema as described later on. If the schema is not valid and can not be compiled, a `SchemaError` is raised.

Each call to `validate` is idempotent, after the initial internal compiling of the schema, no data is altered. Furthermore, the values passed to `validate` wont be changed.



## Merging two schemas ##
TODO



# Tokens #
Tokens are the main parts of the validation. Specific tokens ares described below, but they all have some features in common, in one way or another.
All tokens will validate the input and return the validated input as a new variable. No input is changed! 

#### defaults ####
Most tokens can be initialised with a default-value, which is used if the value passed to it is `None`.

```
>>>Schema(Int(default=1)).validate(None)
1

>>>Schema(String(default="test")).validate(None)
"Test"

>>> Schema({
>>>		Dict.default = {"a": 1}
>>> }).validate(None)
{"a": 1}
```

#### required ####
If this is true, `None` is not accepted as a possible value and a `ValidationError` will be raised.

Note, that if there is a default `None` and required is `true`, this will also raise an error!

The default is `True`


```
>>>Schema(Int(required=False)).validate(None)
None

>>>Schema(Int(required=True)).validate(None)
raises ValidationError
```

#### desc ####
A description for the entry. This is mainly for future features and in configuration-checking-applications, so you could generate a documentation from the config itself.

## ValueTokens ##
ValueTokens cover the use of the basic python types. These are actuall classes, but linked to the basic python types for easier access. For example `Schema(int)` is the same as `Schema(Int())` which is the same
as `Schema(Int(default=None, required=True))`

The current types are:
- `Int()` with binding `int`: Validates the input is an int
- `Object()` with binding `object`: Validates the input is any type of object
- `Bool()` with binding `bool`: Validates the input is a boolean
- `String()` with binding `basestring`: Validates the input is a basestring (Currently this is not very Python2.X/Python3.3 friendly i think...)

## ContainerTokens ##
Containertokens are tokens, which contain other tokens.

### And-Token ###
The And-Token takes a list of other tokens. Upon validation, each of the child-tokens will be applied in order and all must validate. If one child-token changes the input, beware of the order in which the child-tokens are listed.

```
>>>Schema(And(int, Range(min=0))).validate(0)
0
>>>Schema(And(int, Range(min=0))).validate("1")
raises ValidationError because of int
>>>Schema(And(int, Range(min=0))).validate(-1)
raises ValidationError because of range
```


### Or-Token ###
The Or-Token takes a list of other tokens. Upon validation, the first token to not raise a ValidationError 
will be used. 

```
>>>Schema(Or(int, bool)).validate(True)
True
>>>Schema(Or(int, Bool(default=True))).validate(None)
True
>>>Schema(Or(int, Bool(default=True))).validate(1)
1
```

### Dict-Token ###
Dict-Tokens are the more commonly used tokens. They are created implicitly, when a python-dict is found in the schema:

```
Schema({
	"a": int,
	"b": bool
})
```

#### Dict.required ####
The dict can also be marked as beeing required or not. If the dict is not required, the passed value may be `None`. 
```
>>> Schema({
>>>		"a": int
>>>		Dict.required: False
>>> }).validate(None)
None
```

This is different from passing an empty dict however! The following will fail:
```
>>> Schema({
>>>		"a": int,
>>>		Dict.required: False
>>> }).validate({})
raises ValidationError because empty dict is not the same as None!
```

#### Dict.default ####
Similar to `Dict.required`, the default will be used if the entire dict is missing, not if a dict is empty.
```
>>> Schema({
>>>		"a": int,
>>>		Dict.default = {"a": 1}
>>> }).validate(None)
{"a": 1}
```


#### Dict.fixed ####
Fixed is unique to `Dict`. If true (default), this will prevent a dict from taking any none specified 
values and raise an error.

```
>>> Schema({
>>> 	"a": int
>>> }).validate({"a": 1, "b": 2})
raises ValidationError, because 'b' is not accounted for
```

The following will raise no error, but still `b` wont be added to the result. For that, you can check out the flexibel dict-keys below.
```
>>> Schema({
>>> 	"a": int,
>>> 	Dict.fixed: False
>>> }).validate({"a": 1, "b": 2})
{"a": 1}
```

#### Dict.desc ####
`Dict.desc` can be used to set a description


#### Flexible keys ####
Most examples above worked with fixed keys in a dict, but the schema is also able to use type-keys:

```
>>> Schema({
>>>		int: bool
>>> }).validate({1: True, 2: False})
{1: True, 2: False}
```

Specific keys take precedence over flexible ones and more specific types take precedence over more general ones:

```
>>> Schema({
>>>		1: int,
>>>		int: String()
>>> }).validate({1: "t", 2: "c"})
raises ValidationError because key '1' must be of int

>>> Schema({
>>>		int: int
>>> 	object: str
>>>	}).validate({1: "test"})
raises ValidationError because 1 is int and should have a value of int
```

Beware, that `bool` inherits from `int`, so the following will go through because the handler for int will 
also cover a boolean value!
```
>>> Schema({
>>>		bool: bool,
>>>		int: int
>>> }).validate({True: 1})
{True: 1}
```




## DecoratorTokens ##
Decorator-tokens are tokens that check a value with special methods or convert the value to another type.

### Call ###
Apply a function to the value and return it

### Check ###
Apply a function and check the result evaluates to true. return the original value

### Range ###
Check the value is within range

### Regex ###
Check the value matches a regex



