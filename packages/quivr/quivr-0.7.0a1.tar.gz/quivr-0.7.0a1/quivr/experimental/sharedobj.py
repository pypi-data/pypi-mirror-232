import quivr as qv

from . import shmem


class SharedTable:
    def __init__(self, table: qv.Table):
        self.table = table

    @classmethod
    def from_shared_memory(cls, shm: shmem.SharedMemory) -> "SharedTable":
        table = qv.Table.from_shared_memory(shm)
        return cls(table)
