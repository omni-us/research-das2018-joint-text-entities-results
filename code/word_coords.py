#!/usr/bin/env python3

import sys
import pagexml
from jsonargparse import ArgumentParser, ActionPath


parser = ArgumentParser()
parser.add_argument('xml',
    action=ActionPath(mode='fr'),
    help='Page XML file to process.')


cfg = parser.parse_args()

pxml = pagexml.PageXML(cfg.xml())
width = float(pxml.getValue('//_:Page/@imageWidth'))
height = float(pxml.getValue('//_:Page/@imageHeight'))
coords = []

for xword in pxml.select('//_:Word'):
    txt = pxml.getTextEquiv(xword).strip()
    if not txt:
        continue
    pts = pxml.getPoints(xword)
    for num in range(len(txt.split())):
        coords.append(f'{pts[0].x/width:.4f},{pts[0].y/height:.4f},{pts[2].x/width:.4f},{pts[2].y/height:.4f},0')

print(' '.join(coords))
