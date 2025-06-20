# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class NoExtraAttributesMeta(type):
    """Metaclass restricting attribute creation."""

    def __new__(mcs, name, bases, namespace):
        """Create a new class with restricted attribute creation."""
        base = bases[0]  # Base class. We assume each class inherits from one class only.
        # Method Resolution Order (MRO) of the base class, that is, base + every other level of
        # inheritance.
        mro = base.__mro__
        # Store the list of the base class attribute names (in a variable called _allowed_attrs)
        # It is stored in the namespace so that it can be accessed anywhere in the class to create.
        _allowed_attrs = set()
        for cls in mro:
            _allowed_attrs.update(vars(cls).keys())
        namespace["_allowed_attrs"] = _allowed_attrs
        # print(f"Allowed attributes for {name}: {namespace['_allowed_attrs']}")

        def __setattr__(self, key, value):
            # Check if the created attribute is allowed, ie is in the list of attribute defined in
            # the base class.
            print(key)
            if key not in self._allowed_attrs:
                raise AttributeError(
                    f"Cannot create attribute {key}. Class {self.__class__.__name__} does not "
                    "allow creation of attributes that are not defined in "
                    f"{self.__class__.__bases__[0].__name__}."
                )
            else:
                super(cls, self).__setattr__(key, value)

        # Add the __setattr__ method to the namespace of the class to create.
        namespace["__setattr__"] = __setattr__

        # Create and return the new class.
        cls = super().__new__(mcs, name, bases, namespace)
        return cls
