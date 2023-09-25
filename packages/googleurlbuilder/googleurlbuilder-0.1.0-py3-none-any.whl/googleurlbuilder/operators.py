"""
..

Operators over query parameters.
================================

"""

from googleurlbuilder.parameters import BaseParameter, StrParameter


class Or:
    """Union operator."""

    def __new__(cls, *parameters: list[BaseParameter]) -> StrParameter:
        """
        Returns
        -------
        StrParameter
            the resulting parameter.
        """
        return BaseParameter.operate_or(*parameters)


class And:
    """Intersection operator."""

    def __new__(cls, *parameters: list[BaseParameter]) -> StrParameter:
        """
        Returns
        -------
        StrParameter
            the resulting parameter.
        """
        return BaseParameter.operate_and(*parameters)


class Not:
    """Negation operator."""

    def __new__(cls, parameter: BaseParameter) -> StrParameter:
        """
        Parameters
        ----------
        parameter : BaseParameter
            the parameter to process.

        Returns
        -------
        StrParameter
            the resulting parameter.
        """
        return BaseParameter.operate_not(parameter)
    
class Add:
    """Concatenation operator."""

    def __new__(cls, *parameters: list[BaseParameter]) -> StrParameter:
        """
        Returns
        -------
        StrParameter
            the resulting parameter.
        """
        return BaseParameter.concat(*parameters)
