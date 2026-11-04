import time
import statistics
import gc
from algorithms import step_by_step, dda, bresenham_line, bresenham_circle


def bench(fn, args, target_time=0.15, repeats=5):
    fn(*args)
    times = []
    for _ in range(repeats):
        n = 1
        while True:
            gc.disable()
            t0 = time.perf_counter()
            for _ in range(n):
                fn(*args)
            dt = time.perf_counter() - t0
            gc.enable()
            if dt >= target_time:
                times.append(dt / n * 1e6)
                break
            n *= 2
    return statistics.median(times)


def main():
    print("=== Lines ===")
    print(f"{'L':>8} | {'step':>8} | {'dda':>8} | {'bres':>8}")
    for L in (10, 50, 100, 500, 1000, 5000, 10000):
        args = (0, 0, L, L // 2)
        s = bench(step_by_step, args)
        d = bench(dda, args)
        b = bench(bresenham_line, args)
        print(f"{L:>8} | {s:>8.1f} | {d:>8.1f} | {b:>8.1f}")

    print()
    print("=== Circle ===")
    print(f"{'R':>8} | {'time':>8} | {'pts':>6}")
    for R in (10, 100, 500, 1000, 2000):
        t = bench(bresenham_circle, (0, 0, R))
        print(f"{R:>8} | {t:>8.1f} | {len(bresenham_circle(0, 0, R)):>6}")


if __name__ == "__main__":
    main()