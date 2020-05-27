

class Button:
    def __init__(self, text: str, key: str = None):
        self.text = text
        self.key = key

    def set_key(self, key: str):
        self.key = key

    def __eq__(self, other: str):
        if self.key is None:
            return False
        return self.key == other

    def __bool__(self):
        return bool(self.key)

    def __repr__(self):
        return f"Button(key={self.key})"


class TextPromise:
    def __init__(self, key: str):
        self.key = key
        self.value = None
        self._format_data = None
        self._complex = None

    def fill(self, value):
        self.value: str = value

    def format(self, new_data) -> "TextPromise":
        self._format_data = new_data
        return self

    def __str__(self):
        if self._format_data is not None:
            return self.value.format(self._format_data)
        if self._complex:
            return "".join(str(item) for item in self._complex)
        return self.value

    def __add__(self, other: "TextPromise"):
        if self.complex is None:
            self._complex = [self, other]
        else:
            self._complex.append(other)

    # Workaround to make promise to keep itself
    def __deepcopy__(self, memdict={}):
        return self

    def __copy__(self):
        return self

