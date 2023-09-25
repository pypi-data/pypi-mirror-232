"""WorkToy - Wait A Minute! - MissingKeyHandleError
When implementing a custom metaclass, a particularly powerful tool is to
implement custom namespace objects by reimplementing the __prepare__
method. The object returned by the __prepare__ method is expected to
behave like a builtin dictionary instance in a number of situations. The
custom exception defined here concerns how the object handles missing keys.
The namespace objected is expected to raise a KeyError with the name of
the given key. If the object fails to raise such a KeyError, highly
undefined behaviour will result. The system will not raise any informative
error message.

Consider the following example:

  class SusNameSpace(dict):
    #A custom namespace class.#

    def __init__(self, name, bases, *args, **kwargs) -> None:
      dict.__init__(self)
      self._className = name
      self._classBases = bases

    def __getitem__(self, key: str, ) -> object:
      if key in self.keys():
        return dict.__getitem__(self, key)


  class MyMetaClass(type):
    #A Typical metaclass.#

    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
      return SusNameSpace(name, bases)


  class MyClass(metaclass=MyMetaClass):
    #A class derived from the metaclass#

    @staticmethod
    def myMethod():
      #A static method. #
      pass

The above results in the following error message:

  Traceback (most recent call last):
    File "...", line 14, in <module>
      from ... import MyClass
    File "...", line 28, in <module>

      class MyClass(metaclass=MyMetaClass):
    File "...", line 31, in MyClass
      @staticmethod
       ^^^^^^^^^^^^
  TypeError: 'NoneType' object is not callable

  Process finished with exit code 1

The error encountered is because the SusNameSpace instance did not raise:
KeyError('staticmethod'). Changing the __getitem__ method to default
dictionary behaviour, but including a print statement, reveals what is
happening:

  ...
  def __getitem__(self, key: str, ) -> object:
    try:
      return dict.__getitem__(self, key)
    except Exception as e:
      print(key)
      raise e
  ...

Now, the console outputs the following:
'''
  __name__
  staticmethod

  Process finished with exit code 0
'''

The metaclass system implemented in the WorkToy package includes
validation of the namespace objects returned by the __prepare__ method.
The MissingKeyHandleError is raised when a namespace 'objects' fails to
raise KeyError against missing keys in the __getitem__.

Custom metaclasses are powerful, but have such odd quirks. """
#  MIT Licence
#  Copyright (c) 2023 Asger Jon Vistisen
from __future__ import annotations

from worktoy.worktoyclass import WorkToyClass
from worktoy.core import Function
from worktoy.waitaminute import MetaXcept


class MissingKeyHandleError(MetaXcept):
  """...namespace objects fails to raise KeyError against missing keys in
  the __getitem__"""

  monoSpace = WorkToyClass().monoSpace

  def __init__(self, prepare: Function, **kwargs) -> None:
    mcls = kwargs.get('metaclass')
    MetaXcept.__init__(self, prepare, mcls)
    self._prepare = prepare
    self._metaClass = mcls

  def __str__(self) -> str:
    title = ('<br>CRITICAL!<br>%s<br>FATAL!<br>' %
             self.__class__.__qualname__)
    header = """The namespace produced by the given function %s during the 
    class creation implemented by metaclass %s, """
    header = header % (str(self._prepare), str(self._metaClass))
    body = """returned unexpected behaviour against missing keys in the 
    __getitem__ method!<br>Custom classes used as namespaces must raise: 
    "KeyError('key')" where 'key' is the string representing a missing 
    'key'."""
    out = ''.join([title, header, body])
    return self.monoSpace(out)
