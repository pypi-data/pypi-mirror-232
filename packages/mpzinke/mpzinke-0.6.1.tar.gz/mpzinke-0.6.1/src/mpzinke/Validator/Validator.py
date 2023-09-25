

import mpzinke
import types
import typing
from typing import Any, Dict, Optional


class Validator:
	def __init__(self, locals: Dict[str, Any], descendent_class: Optional[type]=None):
		"""
		
		"""
		assert(type(self) is not Validator), "'Validator' must be inheritted"
		assert(issubclass(type(self), Validator)), f"'{type(self).__name__}' must be of type 'Validator'"

		descendent_class = Validator.class_with_Validator_parent(descendent_class or type(self))
		annotations = descendent_class.__init__.__annotations__

		# Check if any parameter is not supplied in the `locals` values.
		missing_params: Dict[str, type] = {name: type for name, type in annotations.items() if(name not in locals)}
		if(len(missing_params) != 0):
			missing_keys_string = ", ".join([f"{name} of type '{type}'" for name, type in missing_params.items()])
			raise KeyError(f"Missing key(s) for {missing_keys_string}")

		# Check if any parameter is not of proper type.
		failed_params: list[Dict[str, Any]] = []  # [{"name": "<name>", "required_type": <type>, "value_type": <value>}]
		for name, required_type in annotations.items():
			if(not Validator.check_type(locals[name], required_type)):
				failed_params.append({"name": name, "required_type": required_type, "value_type": type(locals[name])})

		if(len(failed_params) == 0):
			return

		failed_param_string = "{name} must be of type '{required_type}' not '{value_type}'"
		failed_param_message = ", ".join([failed_param_string.format(**failed_param) for failed_param in failed_params])
		raise ValueError(failed_param_message)


	@staticmethod
	def check_type(value: Any, needed_type: type) -> bool:
		"""
		https://stackoverflow.com/questions/49171189/whats-the-correct-way-to-check-if-an-object-is-a-typing-generic
		"""
		if((origin := typing.get_origin(needed_type)) is types.UnionType or origin is typing.Union):
			return Validator.check_union_type(value, needed_type)

		elif(isinstance(needed_type, (mpzinke.Generic, types.GenericAlias, typing._GenericAlias))):
			return Validator.check_generic_type(value, needed_type)

		# EG. `int`
		return isinstance(value, needed_type)


	@staticmethod
	def check_union_type(value: Any, needed_type: type) -> bool:
		"""
		EG. `int|str`
		"""
		return any(Validator.check_type(value, unioned_type) for unioned_type in needed_type.__args__)


	@staticmethod
	def check_generic_type(value: Any, needed_type: type) -> bool:
		"""
		EG. `list[<__args__[0]>] or Dict[<__args__[0]>, <__args__[1]]`
		"""
		if(not isinstance(value, typing.get_origin(needed_type))):  # if(not isinstance({1: ['1', '1'], ...}, dict))
			return False

		# If the number of types for the generic is one, iterate through those types
		if(len((generics_args := needed_type.__args__)) == 1):
			return all(Validator.check_type(subvalue, generics_args[0]) for subvalue in value)

		# {1: ['1', '1'], 2: ['2', '2'], 3: ['3', '3']}
		for value_children in (value.items() if(isinstance(value, dict)) else value):
			# (1, int), (['1', '1'], list[str])
			if(any(not Validator.check_type(grandchild, type) for grandchild, type in zip(value_children, generics_args))):
				return False

		return True


	@staticmethod
	def class_with_Validator_parent(class_type: type) -> type:
		for base in class_type.__bases__:
			if(base is not None):
				if(base == Validator):
					return class_type

				return Validator.class_with_Validator_parent(base)
