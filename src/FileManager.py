import sys
import os
import json

objective_folder = "/home/dleyvacastro/Documents/devsavant/Langchain/Arquitectura"
# execute tree <folder-name> -J --gitignore -o <filename>.json
os.system(f"tree {objective_folder} -J --gitignore | python3 -m json.tool > filesreport.json")

with open("filesreport.json", "r") as f:
    report = json.load(f)


def format_item(item):
    if item["type"] == "directory":
        if item["name"] not in ["__pycache__", "venv", ".git"]:
            return {
                "name": item["name"],
                # "type": item["type"],
                "children": [format_item(child) for child in item["contents"]]
            }
    elif item["type"] == "file":
        return {
            "name": item["name"],
            # "type": item["type"],
            # "size": item["size"]
        }


def gen_map(report):
    map = format_item(report[0])
    return map


# print(report)
map = gen_map(report)
with open("map.json", "w") as f:
    json.dump(map, f, indent=4)
