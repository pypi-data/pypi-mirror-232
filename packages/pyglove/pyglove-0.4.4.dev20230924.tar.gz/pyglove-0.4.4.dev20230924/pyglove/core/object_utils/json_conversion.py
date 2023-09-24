# Copyright 2022 The PyGlove Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Interface and functions for JSON conversion."""

import abc
import base64
import collections
import importlib
import inspect
import marshal
import pickle
import types
import typing
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Type, TypeVar, Union

# Nestable[T] is a (maybe) nested structure of T, which could be T, a Dict
# a List or a Tuple of Nestable[T]. We use a Union to fool PyType checker to
# make Nestable[T] a valid type annotation without type check.
T = TypeVar('T')
Nestable = Union[Any, T]  # pytype: disable=not-supported-yet

# pylint: disable=invalid-name
JSONPrimitiveType = Union[int, float, bool, str]

# pytype doesn't support recursion. Use Any instead of 'JSONValueType'
# in List and Dict.
JSONListType = List[Any]
JSONDictType = Dict[str, Any]
JSONValueType = Union[JSONPrimitiveType, JSONListType, JSONDictType]

# pylint: enable=invalid-name


class _TypeRegistry:
  """A registry for mapping a string name to type definition.

  This class is used for looking up type definition by a string identifier for
  deserialization.
  """

  def __init__(self):
    """Constructor."""
    # NOTE(daiyip): the order of keys in the dict is preserved. As a result,
    # in `pg.wrapping.apply_wrappers`, the latest registered wrapper
    # class will always be picked up when there are multiple wrapper classes
    # registered for a user class.
    self._type_to_cls_map = dict()

  def register(
      self, type_name: str, cls: Type[Any], override_existing: bool = False
      ) -> None:
    """Register a ``symbolic.Object`` class with a type name.

    Args:
      type_name: String identifier for the class, which will be used as the
        value of `_type` property when deciding which class to construct object
        when converting a JSON value to object.
      cls: Class to register.
      override_existing: Whether allow to override existing value if type name
        is already registered.

    Raises:
      KeyError: If type_name is already registered and override_existing is set
        to False.
    """
    if type_name in self._type_to_cls_map and not override_existing:
      raise KeyError(
          f'Type {type_name!r} has already been registered with class '
          f'{self._type_to_cls_map[type_name].__name__}.')
    self._type_to_cls_map[type_name] = cls

  def is_registered(self, type_name: str) -> bool:
    """Returns whether a type name is registered."""
    return type_name in self._type_to_cls_map

  def class_from_typename(
      self, type_name: str) -> Optional[Type[Any]]:
    """Get class from type name."""
    return self._type_to_cls_map.get(type_name, None)

  def iteritems(self) -> Iterable[Tuple[str, Type[Any]]]:
    """Iterate type registry."""
    return self._type_to_cls_map.items()


class JSONConvertible(metaclass=abc.ABCMeta):
  """Interface for classes whose instances are convertible from/to JSON.

  A JSON convertible object is an object that can be converted into plain Python
  objects, hence can be serialized into or deserialized from JSON.

  Subclasses of ``JSONConvertible`` should implement:

    * ``to_json``: A method that returns a plain Python dict with a `_type`
      property whose value should identify the class.
    * ``from_json``: A class method that takes a plain Python dict and returns
      an instance of the class.

  Example::

    class MyObject(pg.JSONConvertible):

      def __init__(self, x: int):
        self.x = x

      def to_json(self, **kwargs):
        return {
          '_type': 'MyObject',
          'x': self.x
        }

      @classmethod
      def from_json(cls, json_value, **kwargs):
        return cls(json_value['x'])

  All symbolic types (see :class:`pyglove.Symbolic`) are JSON convertible.
  """

  # Registry for looking up the type definition for a string identifier during
  # deserialization. One key can be used for only one type, while the same type
  # can be registered with many different string identifiers, which can be
  # useful to allow backward compatibility of existing serialized strings.
  _TYPE_REGISTRY = _TypeRegistry()

  # Key in serialized dict that represents the class to restore.
  TYPE_NAME_KEY = '_type'

  # Marker (as the first element of a list) for serializing tuples.
  TUPLE_MARKER = '__tuple__'

  # Type converter that converts a complex type to basic JSON value type.
  # When this field is set by users, the converter will be invoked when a
  # complex value cannot be serialized by existing methods.
  TYPE_CONVERTER: Optional[
      Callable[[Type[Any]], Callable[[Any], JSONValueType]]] = None

  # Class property that indicates whether to automatically register class
  # for deserialization. Subclass can override.
  auto_register = True

  @classmethod
  def from_json(cls, json_value: JSONValueType, **kwargs) -> 'JSONConvertible':
    """Creates an instance of this class from a plain Python value.

    NOTE(daiyip): ``pg.Symbolic`` overrides ``from_json`` class method.

    Args:
      json_value: JSON value type.
      **kwargs: Keyword arguments as flags to control object creation.

    Returns:
      An instance of cls.
    """
    del kwargs
    assert isinstance(json_value, dict)
    init_args = {k: from_json(v) for k, v in json_value.items()
                 if k != JSONConvertible.TYPE_NAME_KEY}
    return cls(**init_args)

  @abc.abstractmethod
  def to_json(self, **kwargs) -> JSONValueType:
    """Returns a plain Python value as a representation for this object.

    A plain Python value are basic python types that can be serialized into
    JSON, e.g: ``bool``, ``int``, ``float``, ``str``, ``dict`` (with string
    keys), ``list``, ``tuple`` where the container types should have plain
    Python values as their values.

    Args:
      **kwargs: Keyword arguments as flags to control JSON conversion.

    Returns:
      A plain Python value.
    """

  @classmethod
  def register(
      cls,
      type_name: str,
      subclass: Type['JSONConvertible'],
      override_existing: bool = False
      ) -> None:
    """Registers a class with a type name.

    The type name will be used as the key for class lookup during
    deserialization. A class can be registered with multiple type names, but
    a type name should be uesd only for one class.

    Args:
      type_name: A global unique string identifier for subclass.
      subclass: A subclass of JSONConvertible.
      override_existing: If True, override the class if the type name is
        already present in the registry. Otherwise an error will be raised.
    """
    cls._TYPE_REGISTRY.register(type_name, subclass, override_existing)

  @classmethod
  def is_registered(cls, type_name: str) -> bool:
    """Returns True if a type name is registered. Otherwise False."""
    return cls._TYPE_REGISTRY.is_registered(type_name)

  @classmethod
  def class_from_typename(
      cls, type_name: str) -> Optional[Type['JSONConvertible']]:
    """Gets the class for a registered type name.

    Args:
      type_name: A string as the global unique type identifier for requested
        class.

    Returns:
      A type object if registered, otherwise None.
    """
    return cls._TYPE_REGISTRY.class_from_typename(type_name)

  @classmethod
  def registered_types(cls) -> Iterable[Tuple[str, Type['JSONConvertible']]]:
    """Returns an iterator of registered (serialization key, class) tuples."""
    return cls._TYPE_REGISTRY.iteritems()

  @classmethod
  def to_json_dict(
      cls,
      fields: Dict[str, Union[Tuple[Any, Any], Any]],
      *,
      exclude_default=False,
      exclude_keys: Optional[Set[str]] = None,
      **kwargs) -> Dict[str, JSONValueType]:
    """Helper method to create JSON dict from class and field."""
    json_dict = {JSONConvertible.TYPE_NAME_KEY: _serialization_key(cls)}
    exclude_keys = exclude_keys or set()
    if exclude_default:
      for k, (v, default) in fields.items():
        if k not in exclude_keys and v != default:
          json_dict[k] = to_json(v, **kwargs)
    else:
      json_dict.update(
          {k: to_json(v, **kwargs) for k, v in fields.items()
           if k not in exclude_keys})
    return json_dict

  def __init_subclass__(cls):
    super().__init_subclass__()
    if not inspect.isabstract(cls) and cls.auto_register:
      type_name = _serialization_key(cls)
      JSONConvertible.register(type_name, cls, override_existing=True)


def _serialization_key(
    type_or_function: Union[Type[Any], types.FunctionType]) -> str:
  """Returns the ID for a type or function."""
  serializaton_key = getattr(type_or_function, '__serialization_key__', None)
  if serializaton_key is not None:
    return serializaton_key
  return _type_name(type_or_function)


def _type_name(
    type_or_function: Union[Type[Any], types.FunctionType]) -> str:
  return f'{type_or_function.__module__}.{type_or_function.__qualname__}'


class _OpaqueObject(JSONConvertible):
  """An JSON converter for opaque Python objects."""

  def __init__(self, value: Any, encoded: bool = False):
    if encoded:
      value = self.decode(value)
    self._value = value

  @property
  def value(self) -> Any:
    """Returns the decoded value."""
    return self._value

  def encode(self, value: Any) -> JSONValueType:
    try:
      return base64.encodebytes(pickle.dumps(value)).decode('utf-8')
    except Exception as e:
      raise ValueError(
          f'Cannot encode opaque object {value!r} with pickle.') from e

  def decode(self, json_value: JSONValueType) -> Any:
    assert isinstance(json_value, str), json_value
    try:
      return pickle.loads(base64.decodebytes(json_value.encode('utf-8')))
    except Exception as e:
      raise ValueError('Cannot decode opaque object with pickle.') from e

  def to_json(self, **kwargs) -> JSONValueType:
    return self.to_json_dict({
        'value': self.encode(self._value)
    }, **kwargs)

  @classmethod
  def from_json(cls, json_value: JSONValueType, *args, **kwargs) -> Any:
    del args, kwargs
    assert isinstance(json_value, dict) and 'value' in json_value, json_value
    encoder = cls(json_value['value'], encoded=True)
    return encoder.value


def registered_types() -> Iterable[Tuple[str, Type[JSONConvertible]]]:
  """Returns an iterator of registered (serialization key, class) tuples."""
  return JSONConvertible.registered_types()


def to_json(value: Any, **kwargs) -> Any:
  """Serializes a (maybe) JSONConvertible value into a plain Python object.

  Args:
    value: value to serialize. Applicable value types are:

      * Builtin python types: None, bool, int, float, string;
      * JSONConvertible types;
      * List types;
      * Tuple types;
      * Dict types.

    **kwargs: Keyword arguments to pass to value.to_json if value is
      JSONConvertible.

  Returns:
    JSON value.
  """
  if isinstance(value, (type(None), bool, int, float, str)):
    return value
  elif isinstance(value, JSONConvertible):
    return value.to_json(**kwargs)
  elif isinstance(value, tuple):
    return [JSONConvertible.TUPLE_MARKER] + to_json(list(value), **kwargs)
  elif isinstance(value, list):
    return [to_json(item, **kwargs) for item in value]
  elif isinstance(value, dict):
    return {k: to_json(v, **kwargs) for k, v in value.items()}
  elif isinstance(value, (type, typing.GenericAlias)):  # pytype: disable=module-attr
    return _type_to_json(value)
  elif inspect.isbuiltin(value):
    return _builtin_function_to_json(value)
  elif inspect.isfunction(value):
    return _function_to_json(value)
  elif inspect.ismethod(value):
    return _method_to_json(value)
  # pytype: disable=module-attr
  elif isinstance(value, typing._Final):  # pylint: disable=protected-access
    # pytype: enable=module-attr
    return _annotation_to_json(value)
  elif value is ...:
    return {JSONConvertible.TYPE_NAME_KEY: 'type', 'name': 'builtins.Ellipsis'}
  else:
    if JSONConvertible.TYPE_CONVERTER is not None:
      converter = JSONConvertible.TYPE_CONVERTER(type(value))   # pylint: disable=not-callable
      if converter:
        return to_json(converter(value))
    return _OpaqueObject(value).to_json(**kwargs)


def from_json(json_value: JSONValueType) -> Any:
  """Deserializes a (maybe) JSONConvertible value from JSON value.

  Args:
    json_value: Input JSON value.

  Returns:
    Deserialized value.
  """
  if isinstance(json_value, list):
    if json_value and json_value[0] == JSONConvertible.TUPLE_MARKER:
      if len(json_value) < 2:
        raise ValueError(
            f'Tuple should have at least one element '
            f'besides \'{JSONConvertible.TUPLE_MARKER}\'. '
            f'Encountered: {json_value}.')
      return tuple([from_json(v) for v in json_value[1:]])
    return [from_json(v) for v in json_value]
  elif isinstance(json_value, dict):
    if JSONConvertible.TYPE_NAME_KEY not in json_value:
      return {k: from_json(v) for k, v in json_value.items()}
    type_name = json_value[JSONConvertible.TYPE_NAME_KEY]
    if type_name == 'type':
      return _type_from_json(json_value)
    elif type_name == 'function':
      return _function_from_json(json_value)
    elif type_name == 'method':
      return _method_from_json(json_value)
    else:
      cls = JSONConvertible.class_from_typename(type_name)
      if cls is None:
        raise TypeError(
            f'Type name \'{type_name}\' is not registered '
            f'with a `pg.JSONConvertible` subclass.')
      return cls.from_json(json_value)
  return json_value


#
# Helper methods for loading/saving Python types and functions.
#


def _type_to_json(t: Type[Any]) -> Dict[str, str]:
  """Converts a type to a JSON dict."""
  type_name = _type_name(t)
  origin = typing.get_origin(t) or t
  if '<locals>' not in type_name and origin is _load_symbol(type_name):
    result = {
        JSONConvertible.TYPE_NAME_KEY: 'type',
        'name': type_name,
    }
    args = typing.get_args(t)
    if args:
      result['args'] = to_json(args)
    return result
  else:
    raise ValueError(f'Cannot convert local class {type_name!r} to JSON.')


def _builtin_function_to_json(f: Any) -> Dict[str, str]:
  return {
      JSONConvertible.TYPE_NAME_KEY: 'function',
      'name': f'builtins.{f.__name__}'
  }


def _function_to_json(f: types.FunctionType) -> Dict[str, str]:
  """Converts a function to a JSON dict."""
  if ('<lambda>' == f.__name__                       # lambda functions.
      or (f.__code__.co_flags & inspect.CO_NESTED)   # local functions.
      ):
    return {
        JSONConvertible.TYPE_NAME_KEY: 'function',
        'name': _type_name(f),
        'code': base64.encodebytes(marshal.dumps(f.__code__)).decode('utf-8'),
        'defaults': to_json(f.__defaults__),
    }

  return {
      JSONConvertible.TYPE_NAME_KEY: 'function',
      'name': _type_name(f)
  }


def _method_to_json(f: types.MethodType) -> Dict[str, str]:
  """Converts a method to a JSON dict."""
  type_name = _type_name(f)
  if isinstance(f.__self__, type):
    return {
        JSONConvertible.TYPE_NAME_KEY: 'method',
        'name': type_name
    }
  raise ValueError(f'Cannot convert instance method {type_name!r} to JSON.')


_SUPPORTED_ANNOTATIONS = {
    typing.Any: 'typing.Any',
    typing.Sequence: 'typing.Sequence',
    collections.abc.Sequence: 'typing.Sequence',
    typing.List: 'typing.List',
    list: 'typing.List',
    typing.Tuple: 'typing.Tuple',
    typing.Mapping: 'typing.Mapping',
    collections.abc.Mapping: 'typing.Mapping',
    typing.MutableMapping: 'typing.MutableMapping',
    collections.abc.MutableMapping: 'typing.MutableMapping',
    typing.Dict: 'typing.Dict',
    dict: 'typing.Dict',
    typing.Union: 'typing.Union',
    typing.Optional: 'typing.Optional',
    typing.Callable: 'typing.Callable',
    collections.abc.Callable: 'typing.Callable',
    typing.Set: 'typing.Set',
    set: 'typing.Set',
    typing.FrozenSet: 'typing.FrozenSet',
    frozenset: 'typing.FrozenSet',
}


def _annotation_to_json(annotation) -> Dict[str, str]:
  """Converts a typing annotation to a JSON dict."""
  origin = typing.get_origin(annotation) or annotation
  if origin in _SUPPORTED_ANNOTATIONS:
    name = _SUPPORTED_ANNOTATIONS[origin]
  elif isinstance(origin, type):
    name = _type_name(origin)
  else:
    raise ValueError(f'Annotation cannot be converted to JSON: {annotation}.')

  result = {JSONConvertible.TYPE_NAME_KEY: 'type', 'name': name}
  args = typing.get_args(annotation)
  if args:
    if len(args) > 4:
      raise NotImplementedError(
          'Cannot convert generic type with more than 4 type arguments '
          f'into JSON. Encountered: {annotation}.'
      )
    result['args'] = to_json(args)
  return result


# A symbol cache allows a symbol to be resolved just once upon multiple
# serializations/deserializations.

_LOADED_SYMBOLS = {}

# Special builtin symbols which cannot be accessed from the `builtins` module.

_SPECIAL_BUILTIN_SYMBOLS = {
    'builtins.NoneType': type(None),
    'builtins.Ellipsis': ...,
}


def _load_symbol(type_name: str) -> Any:
  """Loads a symbol from its type name."""
  symbol = _LOADED_SYMBOLS.get(type_name, None)
  if symbol is not None:
    return symbol

  symbol = _SPECIAL_BUILTIN_SYMBOLS.get(type_name, None)
  if symbol is not None:
    _LOADED_SYMBOLS[type_name] = symbol
    return symbol

  # Import symbol based on the module and symbol name.
  *maybe_modules, symbol_name = type_name.split('.')
  module_end_pos = None

  # NOTE(daiyip): symbols could be nested within classes, for example::
  #
  #  class A:
  #    class B:
  #      @classmethod
  #      def x(cls):
  #        pass
  #
  # In such case, class A will have type name `<module>.A`;
  # class B will have type name `module.A.B` and class method `x`
  # will have `module.A.B.x` as its type name.
  #
  # To support nesting, we need to infer the module names from type names
  # correctly. This is done by detecting the first token in the module path
  # whose first letter is capitalized, assuming class names always start
  # with capital letters.
  for i, name in enumerate(maybe_modules):
    if name[0].isupper():
      module_end_pos = i
      break

  # Figure out module path and parent symbol names.
  if module_end_pos is None:
    module_name = '.'.join(maybe_modules)
    parent_symbols = []
  else:
    module_name = '.'.join(maybe_modules[:module_end_pos])
    parent_symbols = maybe_modules[module_end_pos:]

  # Import module and lookup parent symbols.
  module = importlib.import_module(module_name)
  parent = module
  for name in parent_symbols:
    parent = getattr(parent, name)

  # Lookup the final symbol.
  symbol = getattr(parent, symbol_name)
  _LOADED_SYMBOLS[type_name] = symbol
  return symbol


def _type_from_json(json_value: Dict[str, str]) -> Type[Any]:
  """Loads a type from a JSON dict."""
  t = _load_symbol(json_value['name'])
  if 'args' in json_value:
    return _bind_type_args(t, from_json(json_value['args']))
  return t


def _function_from_json(json_value: Dict[str, str]) -> types.FunctionType:
  """Loads a function from a JSON dict."""
  function_name = json_value['name']
  if 'code' in json_value:
    code = marshal.loads(
        base64.decodebytes(json_value['code'].encode('utf-8')))
    defaults = from_json(json_value['defaults'])
    return types.FunctionType(
        code=code,
        globals=globals(),
        argdefs=defaults,
    )
  else:
    return _load_symbol(function_name)


def _method_from_json(json_value: Dict[str, str]) -> types.MethodType:
  """Loads a class method from a JSON dict."""
  return _load_symbol(json_value['name'])


def _bind_type_args(t, args):
  """Bind type args to a type."""
  # NOTE(daiyip): Haven't found an equivalence for expressing `t[**args]`,
  # thus we hard code the logic based on the number of type args. May change
  # if future when we find better ways of expressing this.
  assert args and len(args) <= 4, args
  if len(args) == 1:
    return t[args[0]]
  elif len(args) == 2:
    return t[args[0], args[1]]
  elif len(args) == 3:
    return t[args[0], args[1], args[2]]
  else:
    return t[args[0], args[1], args[2], args[3]]
