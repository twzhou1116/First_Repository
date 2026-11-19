"""Coordinate helpers shared by gameplay and input handling."""

from math import hypot

def distance(ax, ay, bx, by):
    return hypot(ax - bx, ay - by)


def inside(x, y, bounds):
    left, top, width, height = bounds
    return left <= x < left + width and top <= y < top + height
