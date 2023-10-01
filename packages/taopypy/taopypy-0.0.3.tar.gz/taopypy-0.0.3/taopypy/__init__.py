import numpy as np
from .handler import handler


def main() -> None:
    a = np.array([1, 5, 12, 0, 5, 1])
    print(np.mean(a))
