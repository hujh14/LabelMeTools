import argparse
import os
import json
import math

from pycocotools.coco import COCO

from coco_format import save_coco, print_coco

def split_coco(coco, num=10):
    images = coco.dataset["images"]
    annotations = coco.dataset["annotations"]
    categories = coco.dataset["categories"]

    size = math.ceil(len(images) / num)
    cocos = []
    for i in range(num):
        imgs = []
        anns = []
        for img in images[i*size:(i+1)*size]:
            imgs.append(img)

            annIds = coco.getAnnIds(imgIds=[img["id"]])
            anns.extend(coco.loadAnns(annIds))

        c = COCO()
        c.dataset["images"] = imgs
        c.dataset["annotations"] = anns
        c.dataset["categories"] = categories
        c.createIndex()
        cocos.append(c)
    return cocos


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--ann_fn', type=str)
    args = parser.parse_args()

    coco = COCO(args.ann_fn)
    cocos = split_coco(coco)

    for n, c in enumerate(cocos):
        out_fn = args.ann_fn.replace(".json", "{}.json".format(n))
        print_coco(c)
        save_coco(c, out_fn)