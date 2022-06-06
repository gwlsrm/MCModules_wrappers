import json
from itertools import product

det_list = ["hpge", "scintil"]
geom_list = ["point", "cylinder", "marinelli", "cone"]
ANAL = "analyzer"
CALC_PARAMS = "calc_params"
nuclide = "default_nuclide"


def _read_from_json(obj):
    with open(obj + '.json') as f:
        return json.load(f)


if __name__ == "__main__":
    for det, geom in product(det_list, geom_list):
        det_obj = _read_from_json(det)
        geom_obj = _read_from_json(geom)
        nuclide_obj = _read_from_json(nuclide)
        calc_params_obj = _read_from_json(CALC_PARAMS)

        res = det_obj | geom_obj | calc_params_obj | nuclide_obj
        in_name = f"tccfcalc_input_{det}_{geom}.json"
        with open(in_name, 'w') as f:
            json.dump(res, f, indent=4)
