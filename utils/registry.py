import json
import os


class Registry:
    """
    Registry to manage multiple named PersistentDict and PersistentList instances.
    Allows access and manipulation of data across the application via registered names.
    """

    def __init__(self, base_dir):
        """
        Initialize the registry.

        Args:
            base_dir (str): Directory where JSON files are stored.
        """
        self.base_dir = base_dir
        self._objects = {}

    def register(self, name, filepath=None):
        """
        Register a new PersistentDict under a given name.

        Args:
            name (str): Unique identifier for this object.
            filepath (str, optional): Full path to the JSON file. If not provided,
                                      defaults to <base_dir>/<name>.json.

        Returns:
            PersistentDict or PersistentList: The registered persistent object.

        Raises:
            ValueError: If the name is already registered or invalid data_type.
        """
        if name in self._objects:
            raise ValueError(f"An object named '{name}' is already registered.")

        if filepath is None:
            filepath = os.path.join(self.base_dir, f"{name}.json")

        obj = PersistentDict(filepath=filepath)
        self._objects[name] = obj
        return obj

    def unregister(self, name):
        """
        Unregister a previously registered object.

        Args:
            name (str): Name of the object to unregister.

        Raises:
            KeyError: If the name is not registered.
        """
        if name not in self._objects:
            raise KeyError(f"No object registered under the name '{name}'.")
        del self._objects[name]

    def get_object(self, name):
        """
        Get the PersistentDict or PersistentList instance registered under the given name.

        Args:
            name (str): Name of the registered object.

        Returns:
            PersistentDict or PersistentList: The registered object.

        Raises:
            KeyError: If the name is not registered.
        """
        if name not in self._objects:
            raise KeyError(f"No object registered under the name '{name}'.")
        return self._objects[name]


class PersistentBase:
    def __init__(self, root=None, save_callback=None):
        self._root = root or self
        self._is_root = root is None
        self._save_callback = save_callback or self._root._save

    def _wrap(self, value):
        if isinstance(value, dict) and not isinstance(value, PersistentDict):
            return PersistentDict(value, root=self._root, save_callback=self._save_callback)
        elif isinstance(value, list) and not isinstance(value, PersistentList):
            return PersistentList(value, root=self._root, save_callback=self._save_callback)
        return value

    def _unwrap(self, value):
        if isinstance(value, (PersistentDict, PersistentList)):
            return value._raw()
        return value


class PersistentDict(dict, PersistentBase):
    def __init__(self, initial=None, filepath=None, root=None, save_callback=None):
        dict.__init__(self)
        PersistentBase.__init__(self, root=root, save_callback=save_callback)

        self._filepath = filepath if self._is_root else None

        initial_data = {}
        if self._is_root and filepath and os.path.exists(filepath):
            with open(filepath, 'r') as f:
                try:
                    initial_data = json.load(f)
                except json.JSONDecodeError:
                    pass

        if initial:
            initial_data.update(initial)

        for k, v in initial_data.items():
            self[k] = self._wrap(v)

        if self._is_root:
            self._save()

    def __setitem__(self, key, value):
        super().__setitem__(key, self._wrap(value))
        self._save_callback()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._save_callback()

    def clear(self):
        super().clear()
        self._save_callback()

    def pop(self, key, *args):
        result = super().pop(key, *args)
        self._save_callback()
        return result

    def popitem(self):
        result = super().popitem()
        self._save_callback()
        return result

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def _save(self):
        if self._filepath:
            with open(self._filepath, 'w') as f:
                json.dump(self._raw(), f, indent=4)

    def _raw(self):
        return {k: self._unwrap(v) for k, v in self.items()}


class PersistentList(list, PersistentBase):
    def __init__(self, initial=None, root=None, save_callback=None):
        list.__init__(self)
        PersistentBase.__init__(self, root=root, save_callback=save_callback)

        if initial:
            for item in initial:
                self.append(item)

    def append(self, item):
        super().append(self._wrap(item))
        self._save_callback()

    def extend(self, iterable):
        super().extend(self._wrap(v) for v in iterable)
        self._save_callback()

    def insert(self, index, item):
        super().insert(index, self._wrap(item))
        self._save_callback()

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            value = [self._wrap(v) for v in value]
        else:
            value = self._wrap(value)
        super().__setitem__(index, value)
        self._save_callback()

    def __delitem__(self, index):
        super().__delitem__(index)
        self._save_callback()

    def remove(self, value):
        super().remove(value)
        self._save_callback()

    def pop(self, index=-1):
        result = super().pop(index)
        self._save_callback()
        return result

    def clear(self):
        super().clear()
        self._save_callback()

    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        self._save_callback()

    def reverse(self):
        super().reverse()
        self._save_callback()

    def _raw(self):
        return [self._unwrap(v) for v in self]
