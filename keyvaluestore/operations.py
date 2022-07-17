class SetKey:
    def __init__(self, key, old_value, new_value):
        self._key = key
        self._old_value = old_value
        self._new_value = new_value

    def apply_on(self, system):
        system.set_key(self._key, self._old_value, self._new_value)


class Unset:
    def __init__(self, key, old_value):
        self._key = key
        self._old_value = old_value

    def apply_on(self, system):
        system.unset_key(self._key, self._old_value)
