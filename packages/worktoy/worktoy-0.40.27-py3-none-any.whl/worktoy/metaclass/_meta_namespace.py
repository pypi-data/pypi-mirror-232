"""WorkToy - MetaClasses - MetaNameSpace
Provides a metaclass for creation of namespaces. """
#  MIT Licence
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from icecream import ic

from worktoy.core import Bases
from worktoy.metaclass import AbstractMetaClass

ic.configureOutput(includeContext=True)


class MetaNameSpace(AbstractMetaClass):
  """WorkToy - MetaClasses - MetaNameSpace
  Provides a metaclass for creation of namespaces. """

  @classmethod
  def __prepare__(mcls, name: str, bases: Bases) -> dict:
    return {}

  def __new__(mcls,
              name: str,
              bases: Bases,
              nameSpace: dict,
              **kwargs) -> type:
    return AbstractMetaClass.__new__(mcls, name, bases, nameSpace, **kwargs)

  def __init__(cls, name: str, bases: Bases, nameSpace: dict, **kw) -> None:
    AbstractMetaClass.__init__(cls, name, bases, nameSpace, **kw)
    setattr(cls, '__meta_name__', name)

  def __call__(cls, *args, **kwargs) -> object:
    return AbstractMetaClass.__call__(cls, *args, **kwargs)
