from enum import IntEnum

class Button(IntEnum):
    LEFT   = 0
    RIGHT  = 1
    MIDDLE = 2

    def to_bytes(self) -> bytes:
        return super().to_bytes(1, 'little')
