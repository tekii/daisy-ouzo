"""THE PARTY CATALOG"""

__all__ = ["ThePartyCatalog"]


class ThePartyCatalog(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_the_instance"):
            cls._the_instance = super().__new__(cls, *args, **kwargs)
            cls._is_already_configured: bool = False

        return cls._the_instance

    def __init__(self):

        if self._is_already_configured:
            return
        pass

    def __getitem__(self, key: str):
        return self.lookup(key)

    @classmethod
    def lookup(cls, key: str):
        # raise KeyError
        return None

    def purge(self):
        pass
