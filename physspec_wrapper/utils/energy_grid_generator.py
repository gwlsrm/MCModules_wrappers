import argparse
import json

from energy_grid import EnergyGrid


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='generate energy-grid and saves it to json')

    parser.add_argument('positional', help='energy grid parameters: minimal energy, maximal energy, points', nargs='*')
    parser.add_argument('--grid_log', help='is energy grid logarithmic', action="store_true")
    parser.add_argument('--intensity', help='intensity for every energy', type=float, default=1)

    args = parser.parse_args()

    if len(args.positional) != 3:
        raise ValueError('need 3 positional arguments')

    grid = EnergyGrid(
        min_energy=float(args.positional[0]),
        max_energy=float(args.positional[1]),
        point_count=int(args.positional[2]),
        is_log=args.grid_log
    )

    intensity = [args.intensity] * len(grid.grid)
    res = [{'E': energy, 'I': intensity} for energy, intensity in zip(grid.grid, intensity)]

    with open('energy_grid.json', 'w') as f:
        json.dump(res, f)
