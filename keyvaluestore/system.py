from typing import Any


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
        self._operations = []

    def set(self, key, value):
        previous_operation = self._get_last_operation()
        old_value = self.get(key, KeyValueStoreSystem.NEW_KEY)
        self._operations.append(
            SetKey(key, old_value=old_value, new_value=value, previous_operation=previous_operation)
        )

    def get(self, key, default_if_key_does_not_exist: Any = KeyError):
        last_operation = self._get_last_operation()
        return last_operation.get(key, default_if_key_does_not_exist)

    def _get_last_operation(self):
        return self._operations[-1] if self._operations else self._system

    def commit(self):
        self._system.commit(self._operations)
        self._operations = []

    def rollback(self):
        self._operations = []

    def unset(self, key):
        previous_operation = self._get_last_operation()
        old_value = self.get(key, KeyValueStoreSystem.NEW_KEY)
        self._operations.append(Unset(key, old_value=old_value, previous_operation=previous_operation))

    def number_of_keys_with_value(self, a_value):
        last_operation = self._get_last_operation()
        return last_operation.number_of_keys_with_value(a_value)


class SetKey:
    def __init__(self, key, old_value, new_value, previous_operation):
        self._key = key
        self._old_value = old_value
        self._new_value = new_value
        self._previous_operatation = previous_operation

    def apply_on(self, system):
        system.set_key(self._key, self._old_value, self._new_value)

    def get(self, key, default_if_key_does_not_exist):
        if key == self._key:
            return self._new_value
        return self._previous_operatation.get(key, default_if_key_does_not_exist)

    def number_of_keys_with_value(self, a_value):
        if a_value == self._new_value:
            return 1 + self._previous_operatation.number_of_keys_with_value(a_value)
        return self._previous_operatation.number_of_keys_with_value(a_value)


class Unset:
    def __init__(self, key, old_value, previous_operation):
        self._key = key
        self._old_value = old_value
        self._previous_operatation = previous_operation

    def apply_on(self, system):
        system.unset_key(self._key, self._old_value)

    def get(self, key, default_if_key_does_not_exist):
        if key == self._key:
            if default_if_key_does_not_exist is KeyError:
                raise KeyError(key)
            return default_if_key_does_not_exist
        return self._previous_operatation.get(key, default_if_key_does_not_exist)

    def number_of_keys_with_value(self, a_value):
        if a_value == self._old_value:
            return -1 + self._previous_operatation.number_of_keys_with_value(a_value)
        return self._previous_operatation.number_of_keys_with_value(a_value)
