import json
import sys
import matplotlib.pyplot as plt


def _remove511(x, y):
    assert len(x) == len(y)
    new_x = []
    new_y = []
    for i, xval in enumerate(x):
        if xval == 0.511:
            continue
        new_x.append(xval)
        new_y.append(y[i])
    return new_x, new_y


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("plot_calc_result <output_filename>")
        sys.exit()

    filename = sys.argv[1]
    data = None
    with open(filename) as f:
        data = json.load(f)

    if data:
        calc_data = data['CalculationResults']
        x = calc_data['x1']
        y = calc_data['y1']
        x, y = _remove511(x, y)
        x2 = calc_data['x2']
        y2 = calc_data['y2']
        fig = plt.figure()
        plt.title(filename + '.efficiency')
        plt.plot(x, y)
        fig = plt.figure()
        plt.title(filename + '.continuum')
        plt.plot(x2, y2)
        plt.show()
