from typing import Any


def annotation_type(obj: Any) -> Any:
    """
    Use to forward declare an annotation type, i.e. a type that will be fully
    defined later but is not available at the annotation location in the source
    code. The following example shows a MyType class with a method that
    accepts a MyType instance; annotating this cannot be done in Python.

        class MyType:
            def copy_from(other: MyType):  # Raises exception
                ...

    The recommended approach is to use a string annotation, but this is rather
    unnatural in Python code

        class MyType:
            def copy_from(other: 'MyType'):
                ...

    The annotationType function allows a more pythonic syntax:

        @annotationType
        class MyType:
            pass

        class MyType:
            def copy_from(other: MyType):
                ...

    This decorator doesn't actually do anything to its argument.
    """
    return obj
