#!/usr/bin/env python3

import os
from anemoi.datasets import open_dataset


def str_(t):
    """Not needed, but useful for debugging"""
    import numpy as np

    if isinstance(t, (list, tuple)):
        return "[" + " , ".join(str_(e) for e in t) + "]"
    if isinstance(t, np.ndarray):
        return str(t.shape).replace(" ", "").replace(",", "-")
    if isinstance(t, dict):
        return "{" + " , ".join(f"{k}: {str_(v)}" for k, v in t.items()) + "}"
    return str(t)


def main(path, filter):
    with open(path, "r") as f:
        import yaml

        cfg = yaml.safe_load(f)
    cfg=cfg['dataset']

    ds = open_dataset(cfg)
    print(f"✅ Initialized Observations with {len(ds)} items")
    print(f"Dates: {ds.dates[0]}, {ds.dates[1]}, ..., {ds.dates[-2]}, {ds.dates[-1]}")

    print(ds)
    print(ds.tree())

    print(f"Frequency: {ds.frequency}")
    print(f"Variable: {ds.variables}")
    print(f"Name to index: {ds.name_to_index}")
    print(f"Statistics: {str_(ds.statistics)}")

    assert len(ds) == len(ds.dates), (len(ds), len(ds.dates))

    for i in range(len(ds)):
        date = ds.dates[i]
        if filter and not str(date).startswith(filter):
            continue

        data = ds[i]
        print(f"✅Got item {i} for time window ending {date}: {str_(data)}")
    


if __name__ == "__main__":
    import argparse

    HERE = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to config file", default=f"{HERE}/config.yaml")
    parser.add_argument("--filter", help="filter dates (ex: 2017 or 2017-11)")
    args = parser.parse_args()

    main(args.config, args.filter)
