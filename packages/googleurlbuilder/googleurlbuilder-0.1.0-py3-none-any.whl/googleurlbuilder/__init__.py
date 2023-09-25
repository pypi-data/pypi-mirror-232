"""
..

Google URL Builder.
===================

"""

from enum import Enum
from urllib.parse import urlencode
from dataclasses import dataclass, fields
from typing import Optional, Type, get_args
from googleurlbuilder import filters as ft, parameters, tld as tldutils


class DefaultSearchFilterValues:
    """Default values for search filters."""

    @classmethod
    @property
    def language(cls) -> ft.Languages:
        return ft.Languages.Any

    @classmethod
    @property
    def region(cls) -> ft.Regions:
        return ft.Regions.Any

    @classmethod
    @property
    def last_update(cls) -> ft.LastUpdate:
        return ft.LastUpdate.Anytime

    @classmethod
    @property
    def domain(cls) -> str:
        return ""

    @classmethod
    @property
    def terms_appearing(cls) -> ft.TermsAppearing:
        return ft.TermsAppearing.Anywhere

    @classmethod
    @property
    def file_type(cls) -> ft.FileTypes:
        return ft.FileTypes.Any

    @classmethod
    @property
    def usage_rights(cls) -> ft.FileTypes:
        return ft.UsageRights.NotFilteredByLicence


FILTERS_MAPPING = {
    ("lr", "language", None),
    ("cr", "region", None),
    ("as_qdr", "last_update", None),
    ("as_sitesearch", "domain", None),
    ("as_occt", "terms_appearing", None),
    ("as_filetype", "file_type", None),
    ("tbs", "usage_rights", "sur:"),
}
"""A mapping between ``SearchFilters``\ 's attributes and expected google URL 
parameters.

A set of tuples : (``url parameter``\ , ``attribute``\ , 
``url parameter value prefix``\ ).
"""


@dataclass
class SearchFilters:
    """Narrow your results by..."""

    language: Optional[ft.Languages] = None
    """Find pages in the language that you select."""

    region: Optional[ft.Regions] = None
    """ Find pages published in a particular region."""

    last_update: Optional[ft.LastUpdate] = None
    """Find pages updated within the time that you specify."""

    domain: Optional[str] = None
    """Search one site (like wikipedia.org) or limit your results to a domain like 
    .edu, .org or .gov"""

    terms_appearing: Optional[ft.TermsAppearing] = None
    """Search for terms in the whole page, page title or web address, or links to the 
    page you're looking for."""

    file_type: Optional[ft.FileTypes] = None
    """Find pages in the format that you prefer."""

    usage_rights: Optional[ft.UsageRights] = None
    """Find pages that you are free to use yourself."""

    def __post_init__(self) -> None:
        """Validate fields and set default values to None fields.

        Raises
        ------
        TypeError
            if field type is incorrect.
        """
        for field in fields(self):
            field_name = field.name
            field_value = getattr(self, field_name)

            if field_value is None:
                default = self.__get_default_value(field_name)
                setattr(self, field_name, default)
                # Set default value is value is None.
                field_value = default

            field_type = get_args(field.type)[0]
            # Remove None option as field cannot be None now.

            if not isinstance(field_value, field_type):
                raise TypeError(f"{field_name} must be of type {field_type.__name__}.")
            # Make sure typing is good.

    @staticmethod
    def __get_default_value(field_name: str) -> any:
        """
        Parameters
        ----------
        field_name : str
            the name of the field.

        Returns
        -------
        any
            Its default value.
        """
        assert isinstance(field_name, str)
        return getattr(DefaultSearchFilterValues, field_name)

    def compute_filters(self) -> dict[str, str]:
        """
        Returns
        -------
        dict[str, str]
            a dict corresponding to { URL parameter : value }
        """
        computed_filters: dict[str, str] = {}

        for key, attr, prefix in FILTERS_MAPPING:
            value: Enum = getattr(self, attr)

            if value != self.__get_default_value(attr):
                computed_filters.update(
                    {key: (value.value if prefix is None else f"{prefix}{value.value}")}
                )

        return computed_filters


class GoogleURL:
    """A Google URL."""

    @property
    def query(self) -> type[parameters.BaseParameter]:
        """
        Returns
        -------
        type[parameters.BaseParameter]
            The query.
        """
        return self._query

    @query.setter
    def query(self, query: Type[parameters.BaseParameter]) -> None:
        """
        Parameters
        ----------
        query : Type[parameters.BaseParameter]
            the query parameter to set.

        Raises
        ------
        TypeError
            if is not a valid parameter.
        """
        if not isinstance(query, parameters.BaseParameter):
            raise TypeError
        self._query = query

    @property
    def filters(self) -> SearchFilters:
        """
        Returns
        -------
        SearchFilters
            The search filters.
        """
        return self._filters

    @filters.setter
    def filters(self, filters: SearchFilters) -> None:
        """
        Parameters
        ----------
        filters : SearchFilters
            the ``SearchFilters`` to set.

        Raises
        ------
        TypeError
            if ``filters``\ 's type is not ``SearchFilter``\ .
        """
        if not isinstance(filters, SearchFilters):
            raise TypeError
        self._filters = filters

    base_url: str
    """The base URL."""

    def __init__(
        self,
        query: Optional[Type[parameters.BaseParameter]] = None,
        filters: SearchFilters = SearchFilters(),
        tld: tldutils.TLDType = "com",
        https: bool = True,
    ):
        """
        A Google URL.

        Parameters
        ----------
        query : Optional[Type[BaseParameter]], optional
            the Google query, by default None
        filters : SearchFilters, optional
            the search filters, by default SearchFilters()
        tld : tldType, optional
            the TLD of the URL, by default "com"
        https : bool, optional
            If true, returns a http**s** URL, by default True
        """
        if query is not None:
            self.query = query

        self.filters = filters

        self.set_base_url(tld, https)

    def set_base_url(self, tld: tldutils.TLDType = "com", https: bool = True) -> None:
        """Compute the base URL.

        Parameters
        ----------
        tld : tldutils.TLDType
            the TLD of the URL, by default "com"
        https : bool, optional
            If true, returns a http**s** URL, by default True

        Raises
        ------
        ValueError
            if provided TLD is not a valid Google TLD.
        """

        if not tld in set(get_args(tldutils.TLDType)):
            raise ValueError("Not a valid Google TLD.")
        self.base_url = f"http{'s' if https else ''}://google.{tld}"

    def compute_url(self) -> str:
        """
        Returns
        -------
        str
            the Google URL dependending on object attributes.
        """
        parameters: dict[str, str] = self.filters.compute_filters()
        if self.query is not None:
            parameters.update({"q": str(self.query)})

        return f"{self.base_url}/search?{urlencode(parameters)}"

    def __str__(self) -> str:
        """Alias for ``compute_url``\ .

        Returns
        -------
        str
            the Google URL dependending on object attributes.
        """
        self.compute_url()
