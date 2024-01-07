import logging
from typing import Dict, Any
from uuid import uuid4
from digiprod_gen.backend.models.session import DigiProdGenStatus, ProcessingData
from digiprod_gen.backend.models.export import MBAUploadData

logger = logging.getLogger("GlobalMemoryContainer")

class GlobalMemoryContainer:
    """Global Memory Container storey ai agent data in memory and behaves like dict"""
    _memory: Dict[str, Any] = {}

    def __init__(self):
        self.status = DigiProdGenStatus()

    def add(self, item: Any) -> str:
        """Story any item into memory and returns a generated uuid"""
        uuid = uuid4().hex
        self.__setitem__(uuid, item)
        return uuid

    def __setitem__(self, key, item):
        if key in self._memory:
            logger.warning(f"'{key}' already exists in memory and will be overwritten")
        self._memory[key] = item

    def __getitem__(self, key):
        return self._memory[key]

    def __len__(self):
        return len(self._memory)

    def __delitem__(self, key):
        del self._memory[key]

    def update(self, *args, **kwargs):
        return self._memory.update(*args, **kwargs)

    def keys(self):
        return self._memory.keys()

    def values(self):
        return self._memory.values()

    def items(self):
        return self._memory.items()

    def pop(self, *args):
        return self._memory.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.__dict__, dict_)

    def __contains__(self, item):
        return item in self._memory

    def __iter__(self):
        return iter(self._memory)


global_memory_container = GlobalMemoryContainer()
