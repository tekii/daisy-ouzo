"""GS1"""

import re

__all__ = ["GTIN", "GLN"]


class _Base:

    def __init__(self, digits) -> None:
        match = self.RE.match(digits)
        if match:
            self.digits = match[1]
            self.parity = match[2]
        else:
            raise ValueError

    def verify(self):
        sum: int = 0
        parity: int = 0
        current: int = len(self.digits) - 1
        while current >= 0:
            k: int = 1 if parity % 2 else 3
            sum += k * int(self.digits[current])
            current -= 1
            parity += 1
        multiple = sum + ((10 - (sum % 10)) if (sum % 10) else 0)
        calculated = multiple - sum

        if int(self.parity) != calculated:
            raise ValueError

        return True


class GTIN(_Base):

    RE = re.compile(r"^(\d?\d{12})(\d)$")

    def __init__(self, digits) -> None:
        super().__init__(digits)

    def __str__(self):
        return (self.digits + self.parity).zfill(14)


class GLN(_Base):

    RE = re.compile(r"^(\d{12})(\d)$")

    def __init__(self, digits) -> None:
        super().__init__(digits)

    def __str__(self):
        return self.digits + self.parity
