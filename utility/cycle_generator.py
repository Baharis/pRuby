def cycle_generator(iterable, start=0):
    n = start
    while True:
        yield iterable[n % len(iterable)]
        n += 1
