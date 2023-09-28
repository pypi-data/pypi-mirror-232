"""Load config from json file."""
import collections.abc
import dataclasses
import json
import sys
import typing


class ServerCheckException(Exception):
	"""Custom server check exception"""


class ConfigurationException(ServerCheckException):
	"""Configuration Exception"""


class EnhancedJSONEncoder(json.JSONEncoder):
	"""Enhanced json encoder which is able to encode more objects."""

	def __encode_iterable(self, obj: typing.Any) -> dict[str, typing.Any] | list[typing.Any] | tuple[typing.Any, ...] | set[typing.Any]:
		"""Encode iterables.

		:param obj: object to encode
		:return: encoded object
		"""
		if isinstance(obj, dict):  # dicts
			return collections.OrderedDict(zip(obj.keys(), tuple(self.__encode_iterable(item) for item in obj.values())))
		if isinstance(obj, (list, tuple, set)):  # list and subclasses of tuple and set
			return type(obj)((self.__encode_iterable(item) for item in obj))
		if dataclasses.is_dataclass(obj):  # dataclass
			encoded_object: dict[str, typing.Any] = {"dataclass_module": type(obj).__module__, "dataclass_type": type(obj).__name__}
			for f in dataclasses.fields(obj):
				encoded_object[f.name] = self.__encode_iterable(getattr(obj, f.name))
			return encoded_object
		return obj  # non-iterables

	def iterencode(self, o: object, _one_shot: bool = False) -> collections.abc.Iterator[str]:
		"""Overwrite iterative encoding to replace iterables with dicts.

		:param o: object to be encoded
		:return: generator that yields each string representation as available
		"""
		return json.JSONEncoder.iterencode(self, self.__encode_iterable(o), _one_shot)


class EnhancedJSONDecoder(json.JSONDecoder):
	"""Enhanced JSON decoder which is able to decode more objects."""

	def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
		"""Initialize EnhancedJsonDecoder with custom object hook.

		:param \\*args: passed positional arguments
		:param \\**kwargs: additional keyword args
		"""
		json.JSONDecoder.__init__(self, object_hook=self.__object_hook, *args, **kwargs)

	@staticmethod
	def __object_hook(obj: object) -> object:
		"""JSON decoder function which is able to decode more objects.

		:param obj: object in JSON encoding format
		:return: the object decoded as its original class
		"""
		if "dataclass_module" in obj:
			cls = getattr(sys.modules[obj["dataclass_module"]], obj["dataclass_type"])
			fields = {}
			for name, data in obj.items():
				if name in {"dataclass_module", "dataclass_type"}:
					continue
				fields[name] = data
			return cls(**fields)
		return obj
