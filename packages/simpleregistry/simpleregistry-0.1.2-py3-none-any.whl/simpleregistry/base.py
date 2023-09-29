from typing import Set, Dict, List, Iterable, Optional, Any, Type

from simpleregistry import exceptions


class Index:
    pk: str
    fields: List[str]
    index_values: Dict

    def __init__(self, fields: Iterable[str]):
        self.fields = self.normalize_fields(fields)
        self.pk = self.fields_to_index_pk(self.fields)
        self.index_values = {}

    def __str__(self):
        return f"Index: {self.pk}"

    def __repr__(self):
        return f"<{self}>"

    def __hash__(self):
        return hash(self.pk)

    def __eq__(self, other):
        return isinstance(other, Index) and self.pk == other.pk

    def populate(self, member):
        current_level = self.index_values
        for field in self.fields:
            value = getattr(member, field)
            current_level.setdefault(value, [])
            current_level[value].append(member)
            current_level = current_level[value]

    @staticmethod
    def normalize_fields(field_names: Iterable[str]) -> List[str]:
        return sorted(field_names)

    @staticmethod
    def fields_to_index_pk(field_names: Iterable[str]) -> str:
        return ":".join(Index.normalize_fields(field_names))


class Registry:
    members: Set
    indexes: Dict[str, Index]

    def __init__(self, name: str, indexes: Optional[Set[Index]] = None):
        self.name = name
        self.members = set()
        self.indexes = {}
        if indexes is None:
            return
        for index in indexes:
            self.indexes[index.pk] = index

    def _can_use_index(self, fields_and_values: Dict[str, Any]) -> bool:
        return Index.fields_to_index_pk(fields_and_values.keys()) in self.indexes

    def _filter_from_index(self, fields_and_values: Dict[str, Any]) -> Set:
        index = self.indexes[Index.fields_to_index_pk(fields_and_values.keys())]
        current_level = index.index_values
        for field in Index.normalize_fields(fields_and_values.keys()):
            value = fields_and_values[field]
            try:
                current_level = current_level[value]
            except KeyError:
                return set()
        return current_level

    def clear(self):
        self.members = set()

    def register(self, member):
        self.members.add(member)
        for index in self.indexes.values():
            index.populate(member)

    def all(self) -> Set:
        return set(self.members)

    def filter(self, **fields_and_values) -> Set:
        if self._can_use_index(fields_and_values):
            return self._filter_from_index(fields_and_values)

        matches = set()
        for member in self:
            if all(
                [
                    getattr(member, field) == value
                    for field, value in fields_and_values.items()
                ]
            ):
                matches.add(member)
        return matches

    def get(self, **fields_and_values):
        matches = self.filter(**fields_and_values)
        if not matches:
            raise exceptions.NoMatch(f"No matches for {fields_and_values}")
        if len(matches) > 1:
            raise exceptions.MultipleMatches(
                f"Too many matches for {fields_and_values}: {matches}"
            )
        return next(iter(matches))

    def __contains__(self, item: Any) -> bool:
        return item in self.members

    def __len__(self) -> int:
        return len(self.members)

    def __iter__(self):
        return iter(self.members)


def register(registry: Registry):
    client_registry = registry

    def decorator(cls: Type):
        class Decorated(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                client_registry.register(self)

        return Decorated

    return decorator
