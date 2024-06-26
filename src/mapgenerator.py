import random

def generate_map(size):
    map_2d = []
    for i in range(size):
        if i == 0 or i == size - 1:
            row = [1] * size
        else:
            row = [1] + [random.choice([0, 1]) for _ in range(size - 2)] + [1]
        map_2d.append(row)
    return map_2d

def print_map(map_2d, visualized=False):
    for row in map_2d:
        if visualized:
            print("".join('|' if cell == 1 else '.' for cell in row))
        else:
            print("".join(str(cell) for cell in row))

map_size = 10

map_2d = generate_map(map_size)

print("place this map in a file:")
print_map(map_2d)

print("\nvisualize it like:")
print_map(map_2d, visualized=True)
