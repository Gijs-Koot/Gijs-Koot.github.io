#! /usr/bin/env python

import os
from collections import defaultdict
import re
import nbconvert

NB_DIR = "./notebooks"
POST_DIR = "./_posts"
IMG_PATH = "./assets/images"

md_re = r'\d{4}-\d{2}-\d{2}-(?P<post_name>.*).md$'
nb_re = r'(?P<post_name>.*).ipynb$'

cv = nbconvert.exporters.MarkdownExporter()

def combinations():
    # generator: find combinations of yamls and notebooks

    matches = defaultdict(dict)
    for fn in os.listdir(NB_DIR):

        md_match = re.match(md_re, fn)
        nb_match = re.match(nb_re, fn)

        if md_match:
            matches[md_match.groupdict()["post_name"]]["yaml"] = fn
            matches[md_match.groupdict()["post_name"]]["post_name"] = md_match.groupdict()["post_name"]

        if nb_match:
            matches[nb_match.groupdict()["post_name"]]["notebook"] = fn

    for pair in matches.values():
        try:
            nb, ym, pn = pair["notebook"], pair["yaml"], pair["post_name"]
        except:
            print("Unmatched pair, {}".format(pair))
            continue
        yield nb, ym, pn

def convert_notebook(nb, ym, pn):

    md, resources = cv.from_filename(os.path.join(NB_DIR, nb))

    for fn, bt in resources["outputs"].items():
        ## write to assets/images folder
        new_path = os.path.join(IMG_PATH, fn.replace('output', pn))
        with open(new_path, 'wb') as f:
            f.write(bt)
        ## replace path in md (leave out the relative dot)
        md = md.replace(']({})'.format(fn), ']({})'.format(new_path[1:]))

    content = open(os.path.join(NB_DIR, ym)).read() + md
    post_fn = os.path.join(POST_DIR, ym)
    num_bytes = open(post_fn, 'w').write(content)
    print("Written {} bytes to {}".format(num_bytes, post_fn))

if __name__ == "__main__":

    for nb, ym, pn in combinations():

        convert_notebook(nb, ym, pn)
