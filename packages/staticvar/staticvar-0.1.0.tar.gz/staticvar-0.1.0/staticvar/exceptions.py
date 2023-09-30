class StaticvarException(Exception):
	def __init__(self, message: str) -> None:
		'''
		Base class for staticvar exceptions.

		Args:
			message (str): error message.
		'''
		super().__init__(message)


class IllegalInstantiationError(StaticvarException):
	def __init__(self, message: str) -> None:
		'''
		Should be raised when the user tries to create an object out of a class they shouldn't (e.g. `Configure()`).

		Args:
			message (str): error message.
		'''
		super().__init__(message)


class UnsupportedTypeError(StaticvarException):
	def __init__(self, message: str) -> None:
		'''
		Should be raised when a non-standarad type or an unsupported type is specified.

		Args:
			message (str): error message.
		'''
		super().__init__(message)


class StaticvarWarning(Warning):
	def __init__(self, message: str) -> None:
		'''
		Base class for staticvar warnings.

		Args:
			message (str): error message.
		'''
		super().__init__(message)


class ComplicatedTypeWarning(StaticvarWarning):
	def __init__(self, message: str) -> None:
		'''
		Should be raised when a type that `isinstance()` cannot process (e.g. subscripted generics) is specified.

		Args:
			message (str): error message.
		'''
		super().__init__(message)


class UnpredictableBehaviourWarning(StaticvarWarning):
	def __init__(self, message: str) -> None:
		'''
		Should be raised when staticvar is used on a function that can make it behave incorrectly.

		Args:
			message (str): error message.
		'''
		super().__init__(message)