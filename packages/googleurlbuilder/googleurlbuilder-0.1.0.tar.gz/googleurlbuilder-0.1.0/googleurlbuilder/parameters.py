"""
..

Search parameters.
==================

"""

from __future__ import annotations


from enum import Enum
from dataclasses import dataclass, fields
from abc import ABC, abstractmethod
from typing import Optional, Type, Union


NumberType = Optional[Union[int, float, str]]
"""Numbers can contain a unit of measurement."""

class Operators(Enum):
    """Operators used in Google queries."""

    ADD = " "
    """Concatenation."""

    OR = " OR "
    """Union."""

    AND = " AND "
    """Intersection."""


class BaseParameter(ABC):
    """Base search parameter."""

    @staticmethod
    def operate_binary(
        operation: Operators, args: list[Type[BaseParameter]]
    ) -> StrParameter:
        """Binary operation over *x* parameters.

        Parameters
        ----------
        operation : Operators
            the operation to process.
        args : list[Type[BaseParameter]]
            the parameters on which we operate.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return StrParameter(
            f"({f'{operation.value}'.join([str(arg) for arg in args])})"
        )

    @staticmethod
    def operate_not(query_parameter: Type[BaseParameter]) -> StrParameter:
        """Operate a negation over a parameter.

        Parameters
        ----------
        query_parameter : Type[BaseParameter]
            the parameter to process.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return StrParameter(f"-{str(query_parameter)}")

    @classmethod
    def operate_or(cls, *args: list[Type[BaseParameter]]) -> StrParameter:
        """Operate an union.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return cls.operate_binary(operation=Operators.OR, args=args)

    @classmethod
    def operate_and(cls, *args: list[Type[BaseParameter]]) -> StrParameter:
        """Operate an iteresection.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return cls.operate_binary(operation=Operators.AND, args=args)

    @classmethod
    def concat(cls, *args: list[Type[BaseParameter]]) -> StrParameter:
        """Operate a concatenation.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return cls.operate_binary(operation=Operators.ADD, args=args)

    def __or__(self, other: Type[BaseParameter]) -> StrParameter:
        """Operate an union between this object and another.

        Parameters
        ----------
        other : Type[BaseParameter]
            the other parameter to process.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return self.operate_or(self, other)

    def __and__(self, other: Type[BaseParameter]) -> StrParameter:
        """Operate a concatenation between this object and another.

        Parameters
        ----------
        other : Type[BaseParameter]
            the other parameter to process.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return self.operate_and(self, other)

    def __add__(self, other : Type[BaseParameter]) -> StrParameter:
        """Operate an intersection between this object and another.

        Parameters
        ----------
        other : Type[BaseParameter]
            the other parameter to process.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return self.concat(self, other)

    def __invert__(self) -> StrParameter:
        """Operate a negation over this object.

        Returns
        -------
        StrParameter
            A parameter.
        """
        return self.operate_not(self)

    @abstractmethod
    def __str__(self):
        """Query parameters (subclasses of this) must contain a ``__str__`` method which
        returns a str value corresponding to the **query pararmeter** used in google 
        queries depending on attributes of that field.

        Must be overriden.

        Returns
        -------
        str
            the computed str used in google queries.
        """
        pass


@dataclass
class StrParameter(BaseParameter):
    """A str parameter."""

    str_value: str
    """The str value of this parameter."""

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            the computed str used in google queries.
        """
        return self.str_value
    
    def __post_init__(self) -> None:
        """Validate fields.

        Raises
        ------
        TypeError
            if field type is incorrect.
        """
        if not isinstance(self.str_value, str):
            raise TypeError("str_value must be of type be str.")


@dataclass
class NumbersParameter(BaseParameter):
    """A number parameter."""

    number_from: NumberType
    """Number ranging from"""

    number_to: NumberType
    """Number ranging to"""
    
    def __str__(self) -> str:
        """
        Returns
        -------
        str
            the computed str used in google queries.
        """
        if self.number_from is None and self.number_to is None:
            return ""

        query: str = ""

        if self.number_from is not None:
            query += str(self.number_from)
        query += ".."
        if self.number_to is not None:
            query += str(self.number_to)

        return query
    
    def __post_init__(self) -> None:
        """Validate fields.

        Raises
        ------
        TypeError
            if field type is incorrect.
        """
        for field in fields(self):
            if not isinstance(field.type, NumberType):
                raise TypeError(f"{field.name} must be of type NumberType.") 


@dataclass
class BaseWordParameter(BaseParameter):
    """Base class for parameters based on a list of words."""

    words: list[str]
    """A list of words."""

    @abstractmethod
    def __str__(self) -> str:
        """Must be overriden.

        Returns
        -------
        str
            the computed str used in google queries.
        """
        pass

    def __len__(self) -> int:
        """
        Returns
        -------
        int
            the len of this.
        """
        return len(self.words) # The length of this object corresponds to the length of 
        # the ``words`` attribute.

    def __post_init__(self) -> None:
        """Validate fields.

        Raises
        ------
        TypeError
            if field type is incorrect.
        """
        try : 
            assert(isinstance(self.words, list))
            for word in self.words :
                assert(isinstance(word, str))
        except AssertionError :
            raise TypeError("words must be a list of str.")


class Words(BaseWordParameter):
    """A list of words."""

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            the computed str used in google queries.
        """
        string = " ".join(self.words)
        return f"({string})" if len(self) > 1 else string # add paranthesis if there is 
        # several words


class ExactPhrases(BaseWordParameter):
    """A list of exact words or exact phrases."""

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            the computed str used in google queries.
        """
        string = " ".join([f'"{phrase}"' for phrase in self.words])
        return f"({string})" if len(self) > 1 else string # add paranthesis if there is 
        # several words
