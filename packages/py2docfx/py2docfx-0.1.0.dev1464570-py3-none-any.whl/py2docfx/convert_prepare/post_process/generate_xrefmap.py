"""This module generates xrefmap from external links."""
import os
import urllib.request
import yaml

from sphinx.util.inventory import InventoryFile

EXTERNAL_LINK = "https://docs.python.org/3/"
XREFMAP_NAME = "xrefmap.yml"
xref_map = []

def generate_xrefmap(doc_dir: os.PathLike):
    obj_link = os.path.join(EXTERNAL_LINK, "objects.inv")
    stream = urllib.request.urlopen(obj_link)
    inventory = InventoryFile.load(stream, EXTERNAL_LINK, os.path.join)
    for role_key, role_value in inventory.items():
        if role_key.startswith("py:"):
            for ref_name, ref_value in role_value.items():
                # Only use last element in ref_name
                title_name = ref_name.split(".")[-1]
                xref_map.append({"uid": ref_name,
                                "name": title_name,
                                "href": ref_value[2],
                                "fullName": ref_name})

    with open(os.path.join(doc_dir, XREFMAP_NAME), "w", encoding="utf8") as out_file:
        yaml.dump({"references": xref_map}, out_file, default_flow_style=False, allow_unicode=True)
