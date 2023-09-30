from inspect import isclass
from keyword import iskeyword
from typing import Any, Callable, get_args, get_origin, ParamSpec, TypeVar
from warnings import warn

from .exceptions import *
from .utils import *


# Defining the generic types used by staticvar 
P = ParamSpec('P') # Represents the argument types of the function being decorated
R = TypeVar('R') # Represents any return type of the function being decorated


def staticvar(var_name: str, initial_value: Any, var_type: type = Any) -> Callable[[Callable[P, R]], Callable[P, R]]:
	'''
	
	Decorator to create a static variable for the target function.

	Args:
		var_name (str): static variable name.
		initial_value (Any): initial value for the variable.
		var_type (type): type of the variable. Leave empty to make it dynamic.

	Returns:
		Callable[[Callable[P, R]], Callable[P, R]]: the decorated function.

	Raises:
		TypeError:
			• if a type is specified and it does not match the initial value.

			• if the variable name is not a string.

		UnsupportedTypeError: if the specified variable is not a valid type or a generic type from the typing module.
		ValueError: if the variable name does not follow Python's syntax rules.
	
	'''
	def decorator(func: Callable[P, R]) -> Callable[P, R]:
		# Checking if the targetted function is a method or a nested function
		if (
			len(func.__qualname__.split('.')) > 1 and
			not Configure.suppressed()['UnpredictableBehaviourWarning']
		):
			warn(
				f"\033[91m{func.__name__}: "
				f"staticvar should not be used on methods or nested functions.\n"
				f"\033[93mTo suppress this warning, use Configure.suppress('UnpredictableBehaviourWarning')\033[0m",
				UnpredictableBehaviourWarning
			)

		
		# Checking if the variable name is not a string
		if type(var_name) != str:
			with StaticvarExceptionHandler():
				raise TypeError(
					f"{func.__name__}: Variable name must be a string. Current type: {(type(var_name))}"
				)
		
		# Getting the full name of the variable
		full_name: str = f"{func.__name__}.{var_name.encode('unicode_escape').decode()}"

		
		# Checking if the type specified is not a valid type or a generic type from the typing module
		var_origin = get_origin(var_type)
		var_args = get_args(var_type)

		if not (
			isclass(var_type) or
			(var_origin is not None and isinstance(var_origin, type)) or
			(var_args is not None and len(var_args) > 0)
		):
			with StaticvarExceptionHandler():
				raise UnsupportedTypeError(
					f"{full_name}: "
					f"variable type must be a valid type or a generic type from the typing module. "
					f"Type specified: {var_type}"
				)
		
		# Checking if the initial value does not match the type specified.
		matching: bool = True
		try:
			if var_type is not Any and not isinstance(initial_value, var_type):
				matching = False
		except TypeError:
			if not Configure.suppressed()['ComplicatedTypeWarning']:
				warn(
					f"\033[91m{func.__name__}: "
					f"@staticvar decorator cannot check if the type {var_type} matches the type of the initial value.\n"
					f"\033[93mTo suppress this warning, use Configure.suppress('ComplicatedTypeWarning')\033[0m",
					ComplicatedTypeWarning
				)
		else:
			if matching is False:
				with StaticvarExceptionHandler():
					raise TypeError(
						f"{full_name}: variable must be of specified type {var_type}. Current type: {type(initial_value)}"
					)
		

		# Checking if the variable name does not follow Python's syntax rules.
		if iskeyword(var_name):
			with StaticvarExceptionHandler():
				raise ValueError(f"{full_name}: variable name cannot be a reserved keyword")
		
		if var_name[0].isdecimal():
			with StaticvarExceptionHandler():
				raise ValueError(f"{full_name}: variable name cannot start with a number")
		
		for ch in var_name:
			if not (ch == "_" or ch.isalpha() or ch.isdecimal()):
				with StaticvarExceptionHandler():
					raise ValueError(f"{full_name}: variable name contains an invalid character: {repr(ch)}")
		
		
		setattr(func, var_name, initial_value)

		return func
	return decorator