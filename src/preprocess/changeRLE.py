import os
import json
import numpy as np
from itertools import chain
try:
    from itertools import zip_longest as zip_longest
except:
    from itertools import izip_longest as zip_longest

from pycocotools.coco import COCO

def maskToRLE(mask):
    h, w = mask.shape
    flattened = mask.flatten()

    padded = np.hstack([[0], flattened, [0]])
    difs = np.diff(padded)
    starts = np.where(difs == 1)[0]
    ends = np.where(difs == -1)[0]

    zipped = [x for x in chain(*zip_longest(starts, ends)) if x is not None]
    padded = [0] + zipped + [flattened.shape[0]]
    counts = np.diff(padded)
    if counts[-1] == 0:
        counts = counts[:-1]

    counts = [str(c) for c in counts]
    counts = "#".join(counts)

    rle = {}
    rle["height"] = mask.shape[0]
    rle["width"] = mask.shape[1]
    rle["counts"] = counts
    return rle


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str)
    parser.add_argument('-o', '--output_dir', type=str)
    args = parser.parse_args()

    out_fn = os.path.basename(args.input_file).replace('.json', '_#.json')
    out_path = os.path.join(args.output_dir, out_fn)
    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))

    coco = COCO(args.input_file)
    c = 0
    for annId in coco.anns:
        c += 1
        print("{}/{}".format(c, len(coco.anns)))
        ann = coco.anns[annId]
        mask = coco.annToMask(ann)
        ann["segmentation"] = maskToRLE(mask)

    output = {}
    output["images"] = list(coco.imgs.values())
    output["annotations"] = list(coco.anns.values())
    output["categories"] = list(coco.cats.values())
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
