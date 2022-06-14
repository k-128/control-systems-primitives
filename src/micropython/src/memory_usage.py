import gc
import os


def get_free_memory_disk() -> float:
    '''Get free disk memory in MB'''
    s = os.statvfs("//")
    b = s[0] * s[3]  # Bytes
    return b / 1_048_576


def get_free_memory_ram() -> tuple[float, float]:
    '''Get free RAM memory in bytes: (free, total)'''
    free      = gc.mem_free()  # Bytes
    allocated = gc.mem_alloc() # Bytes
    total     = free + allocated
    return (free, total)


def print_memory_usage() -> None:
    print(f"free memory disk: {get_free_memory_disk():.2f} MB")
    m = get_free_memory_ram()
    print(f"free memory ram: {m[0]} B, {(m[0] / m[1]) * 100:.2f} % of {m[1]} B")


if __name__ == "__main__":
    print_memory_usage()
