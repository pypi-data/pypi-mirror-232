simpleregistry
==============

Simple registries in Python.

Right now supports only object registries, but class registries are coming in the future releases:

```python
import dataclasses

import simpleregistry


book_registry = simpleregistry.Registry('books')


@simpleregistry.register(book_registry)
@dataclasses.dataclass
class Book:
    isbn: int
    title: str
    author: str
    
    def __hash__(self) -> int:
        return hash(self.isbn)


lord_of_the_rings = Book(123, 'The Lord of the Rings', 'J. R. R. Tolkien')

assert lord_of_the_rings in book_registry
assert len(book_registry) == 1
assert book_registry.all() == {lord_of_the_rings}
assert book_registry.get(isbn=123) == lord_of_the_rings
assert book_registry.filter(author='J. R. R. Tolkien') == {lord_of_the_rings}

```

Works with custom types, standard-library dataclasses and Pydantic. See tests for examples.

This project is currently in Alpha status. You are welcome to use it. Code should be stable, but the API may change.
