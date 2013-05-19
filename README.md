# py-data-schema #

`py-data-schema` is a little library to create schemas which are able to validate complex python data structurs, with capability to provide defaults, validate flexible key-value-pairs, converting input. Furthermore it
provides a few additional validators, for example Length, Regex-Matching.


Below a few examples, the README is still a bit empty, but i plan to expand it...



Simple schema, which validates a dictionary:
```
schema = Schema({
	"some_key": int, # automatic conversion from basic types to validated types
	"some_other_key": Bool(default=True) # Provide defaults
	"x": String(required=False) # Mark entries as not required
})

res = schema.validate({
	"some_key": 1
})

res is now {
	"some_key": 1,
	"some_other_key": True
}
```

Using flexible keys in dictionarys:
```
schema = Schema({
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


## Basics ##


## Merging two schemas ##



# Tokens #

## ValueTokens ##

## ContainerTokens ##

## DecoratorTokens ##


