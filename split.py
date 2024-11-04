# This script takes a game.graph.json file and a resource pack, and splits the
# resource pack into multiple smaller packs.

import json
import os.path
import sys
import zipfile
import subprocess

MANIFEST_NAME = "liveupdate.game.dmanifest"

def extract_excluded_collections(graph_file):
  """
  Reads the Defold game.graph.json, generated when you Bundle the game and
  placed in build/default/game.graph.json.
  It finds all collections that are excluded from the main bundle and
  returns a list of tuples with the name of the collection and a list of
  dependencies for that collection.
  """
  objects = {}
  with open(graph_file, "r") as f:
    graph = json.load(f)
  for n in graph:
    path = n["path"]
    objects[path] = n

  collections = []
  for path, n in objects.items():
    if path.endswith(".collectionc") and not n["isInMainBundle"]:
      name = os.path.basename(path)[:-len(".collectionc")]
      collections.append((name, sorted(list_dependencies(path, objects))))

  return collections

def list_dependencies(root, objects):
  """
  Recursively lists all dependencies for a given object in the game.graph.json.
  """
  obj = objects[root]
  if obj["isInMainBundle"]:
    return []
  deps = [obj["hexDigest"]]
  for path in obj["children"]:
    deps.extend(list_dependencies(path, objects))
  return deps

def find_latest_resourcepack(dir):
  """
  Finds the latest resource pack in the given directory.
  """
  if os.path.isfile(dir):
    return dir
  packs = [f for f in os.listdir(dir) if f.endswith(".zip")]
  packs = [(os.path.getmtime(os.path.join(dir, f)), f) for f in packs]
  packs.sort()
  return os.path.join(dir, packs[-1][1])

if __name__ == "__main__":
  if len(sys.argv) <= 3:
    print("Usage: python split.py <path to game.graph.json> <path to resourcepack(s)> <output dir>", file=sys.stderr)
    sys.exit(1)

  excluded_collections = extract_excluded_collections(sys.argv[1])
  print("Collections:")
  for name, deps in excluded_collections:
    print(f"  {name} ({len(deps)} dependencies)")

  latest_pack_path = find_latest_resourcepack(sys.argv[2])
  print("Latest pack:", latest_pack_path)

  gitsha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()

  with zipfile.ZipFile(latest_pack_path, "r") as source:
    manifest_content = source.read(MANIFEST_NAME)
    for name, deps in excluded_collections:
      resultfile = os.path.join(sys.argv[3], f"{name}.zip")
      print("Creating zip for collection", name, "to", resultfile)
      with zipfile.ZipFile(resultfile, "w", zipfile.ZIP_DEFLATED, True, 9) as target:
        # all split resourcepacks need a manifest, just copying over the original one completely:
        target.writestr(MANIFEST_NAME, manifest_content)
        # Write current gitsha to metadata:
        target.writestr(f"metadata_{name}.json", json.dumps({"gitsha": gitsha}))
        for dep in deps:
          target.writestr(dep, source.read(dep))

