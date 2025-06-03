import json
from itertools import product

det_list = ["hpge", "scintil"]
collimator_list = ["nocol", "col1", "col2"]
geom_list = ["point", "barrel", "nzk", "nzk_chamfered", "point_zshift_old", "point_xshift_old",
             "point_zshift_new", "point_xshift_new"]
CALC_PARAMS = "calc_params"


def _read_from_json(obj):
    with open(obj + '.json') as f:
        return json.load(f)


def main():
    for det, col, geom in product(det_list, collimator_list, geom_list):
        in_name = f"physspec_input_{det}_{col}_{geom}.json"
        det_obj = _read_from_json(det)
        if col != "nocol":
            col_obj = _read_from_json(col)
        else:
            col_obj = None
        geom_obj = _read_from_json(geom)
        calc_params_obj = _read_from_json(CALC_PARAMS)

        res = det_obj | geom_obj | calc_params_obj
        if col_obj:
            res |= col_obj

        with open(in_name, 'w') as f:
            json.dump(res, f, indent=4)


if __name__ == "__main__":
    main()
