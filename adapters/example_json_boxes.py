"""Example adapter: a folder with images and a labels.json of [x1, y1, x2, y2] pixel boxes."""

import json

from cairnml.datasets import Adapter


class ExampleJsonBoxes(Adapter):
    modalities = {"image": "image"}
    labels = {"bbox2d": "bbox2d"}

    def run(self, source, writer):
        for item in json.loads((source / "labels.json").read_text()):
            boxes = [{"box": box, "label": name} for box, name in item["boxes"]]
            writer.add(item["id"], item["split"], {"image": item["file"]}, {"bbox2d": boxes})
