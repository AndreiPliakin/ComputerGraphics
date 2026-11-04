import time
from algorithms import step_by_step, dda, bresenham_line, bresenham_circle


def bench(fn, args, n=500):
    fn(*args)
    t0 = time.perf_counter()
    for _ in range(n):
        fn(*args)
    return (time.perf_counter() - t0) / n * 1e6


def main():
    print("L       step    dda     bres")
    for L in (10, 50, 100, 500, 1000, 5000, 10000):
        args = (0, 0, L, L // 2)
        s = bench(step_by_step, args)
        d = bench(dda, args)
        b = bench(bresenham_line, args)
        print(L, s, d, b)

    print("Circle")
    for R in (10, 100, 500, 1000, 2000):
        t = bench(bresenham_circle, (0, 0, R), n=200)
        print(R, t, len(bresenham_circle(0, 0, R)))


if __name__ == "__main__":
    main()
