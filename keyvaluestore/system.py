from typing import Any

from keyvaluestore.operations import SetKey, Unset


class KeyValueStoreSystem:
    class TransactionConflict(RuntimeError):
        """Raised when a transaction tries to modify old data"""

    NEW_KEY = object()

    def __init__(self):
        self._storage = {}

    def begin(self):
        return Transaction(self)

    def end(self):
        pass

    def commit(self, operations):
        for operation in operations:
            operation.apply_on(self)

    def get(self, key, default_if_key_does_not_exist: Any = KeyError):
        if default_if_key_does_not_exist is KeyError:
            return self._storage[key]
        return self._storage.get(key, default_if_key_does_not_exist)

    def set_key(self, key, old_value, new_value):
        self._assert_there_are_not_conflict(key, old_value)
        self._storage[key] = new_value

    def unset_key(self, key, old_value):
        self._assert_there_are_not_conflict(key, old_value)
        del self._storage[key]

    def _assert_there_are_not_conflict(self, key, old_value):
        current_value = self.get(key, KeyValueStoreSystem.NEW_KEY)
        if current_value != old_value:
            raise KeyValueStoreSystem.TransactionConflict()

    def number_of_keys_with_value(self, a_value):
        return sum(value == a_value for value in self._storage.values())



class Transaction:
    def __init__(self, system: KeyValueStoreSystem):
        self._system = system
        self._init()

    def set(self, key, value):
        old_value = self.get(key, KeyValueStoreSystem.NEW_KEY)
        self._operations.append(SetKey(key, old_value=old_value, new_value=value))
        self._local_storage[key] = value

    def get(self, key, default_if_key_does_not_exist: Any = KeyError):
        if key in self._unset_keys:
            if default_if_key_does_not_exist is KeyError:
                raise KeyError(key)
            return default_if_key_does_not_exist
        if key in self._local_storage:
            return self._local_storage[key]
        return self._system.get(key, default_if_key_does_not_exist)

    def commit(self):
        self._system.commit(self._operations)
        self._init()

    def rollback(self):
        self._init()

    def _init(self):
        self._local_storage = {}
        self._operations = []
        self._unset_keys = set()

    def unset(self, key):
        old_value = self.get(key, KeyValueStoreSystem.NEW_KEY)
        if key in self._local_storage:
            del self._local_storage[key]
        self._operations.append(Unset(key, old_value=old_value))
        self._unset_keys.add(key)

    def number_of_keys_with_value(self, a_value):
        return sum(
            value == a_value for value in self._local_storage.values()
        ) + self._system.number_of_keys_with_value(a_value)
