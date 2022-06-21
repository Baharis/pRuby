def cycle(iterable, start=0):
    while True:
        yield iterable[start % len(iterable)]
        start += 1
