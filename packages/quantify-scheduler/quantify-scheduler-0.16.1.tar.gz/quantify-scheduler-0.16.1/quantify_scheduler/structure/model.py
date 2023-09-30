# Repository: https://gitlab.com/quantify-os/quantify-scheduler
# Licensed according to the LICENCE file on the main branch
"""Root models for data structures used within the package."""

import types
from typing import Any, Callable

import orjson
from pydantic import BaseModel, Extra

from quantify_scheduler.structure import types as qs_types
from quantify_scheduler.helpers.importers import (
    import_python_object_from_string,
    export_python_object_to_path_string,
)


def orjson_dumps(obj: Any, *, default: Callable[[Any], Any]) -> str:
    """Dump an object to a JSON string using :mod:`orjson` library.

    Parameters
    ----------
    obj
        Object to dump
    default
        A function that is called if an object can't be serialized otherwise.
        It should return a JSON-encodable version of an object or raise a
        :class:`TypeError`.

    Returns
    -------
    str
        JSON-encoded string representation of an object

    Raises
    ------
    TypeError
        If value can't be serialized.
    """
    # Use orjson.OPT_NON_STR_KEYS to allow for non-string keys in datastructures.
    # For example: a module/channel index in the HardwareDescription.
    return orjson.dumps(obj, default=default, option=orjson.OPT_NON_STR_KEYS).decode()


class DataStructure(BaseModel):  # pylint: disable=too-few-public-methods
    """A parent for all data structures.

    Data attributes are generated from the class' type annotations, similarly to
    `dataclasses <https://docs.python.org/3/library/dataclasses.html>`_. If data
    attributes are JSON-serializable, data structure can be serialized using
    ``json()`` method. This string can be deserialized using ``parse_raw()`` classmethod
    of a correspondent child class.

    If required, data fields can be validated, see examples for more information.
    It is also possible to define custom field types with advanced validation.

    This class is a pre-configured `pydantic <https://docs.pydantic.dev/>`_
    model. See its documentation for details of usage information.

    .. admonition:: Examples
        :class: dropdown

        .. include:: ../../../../examples/structure.DataStructure.rst
    """

    class Config:  # pylint: disable=too-few-public-methods,missing-class-docstring
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        # Support serialization of function and class pointers, turning them
        # into dotted import strings:
        json_encoders = {
            types.FunctionType: export_python_object_to_path_string,
            type: export_python_object_to_path_string,
            qs_types.NDArray: qs_types.NDArray.to_dict,
        }

        # ensures exceptions are raised when passing extra argument that are not
        # part of a model when initializing.
        extra = Extra.forbid

        # run validation when assigning attributes
        validate_assignment = True


def deserialize_function(fun: str) -> Callable[..., Any]:
    """Import a python function from a dotted import string (e.g.,
    "quantify_scheduler.structure.model.deserialize_function").

    Parameters
    ----------
    fun : str
        A dotted import path to a function (e.g.,
        "quantify_scheduler.waveforms.square"), or a function pointer.

    Returns
    -------
    Callable[[Any], Any]


    Raises
    ------
    ValueError
        Raised if the function cannot be imported from path in the string.
    """
    try:
        return import_python_object_from_string(fun)
    except ImportError as exc:
        raise ValueError(f"{fun} is not a valid path to a known function.") from exc


def deserialize_class(cls: str) -> type:
    """Import a python class from a dotted import string (e.g.,
    "quantify_scheduler.structure.model.DataStructure").

    Parameters
    ----------
    cls : str

    Returns
    -------
    :
        The type you are trying to import.

    Raises
    ------
    ValueError
        Raised if the class cannot be imported from path in the string.
    """
    try:
        return import_python_object_from_string(cls)
    except ImportError as exc:
        raise ValueError(f"{cls} is not a valid path to a known class.") from exc
