#!/usr/bin/env python

from math import log


def transpose_matrix(matrix):
    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]


def sizeof(n):
    if n == 0:
        return 1
    return int(log(n, 256)) + 1
