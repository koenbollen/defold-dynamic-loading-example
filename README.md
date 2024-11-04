# defold-dynamic-loading-example

This is a small example project for dynamically load (and download) resources.
Usecase: If you have a lot of levels, and each level has one or more 'biomes'
or asset-packs required and you don't want to load in everything from the start.

Reasons to now always load everything:
- Not everything fits into memory
- Load time is long, whilst level 1 only needs a few assets
- Download time on web, players could start playing while the rest is downloaded.

## How it works

The _bootstrap.collection_ contains a loader.script that manages the loading
of collections and levels. It first loads _main.collection_ and then the 
_game.collection_ in main.
For each level load it will send the 'ensure_biomes' and when that's ready it 
will trigger the game.collection to load a level (which is just adding random
things).

The /biomes/loader.script is in charge of loading and unloading collectionproxies.

## LiveUpdate for web

If you just build the game everything is loaded, but the biomes collections are 
only loaded when needed.

When you bundle the project and have 'Publish Live Update content' enabled it 
will enable the /biomes/downloader.lua as well.

Before running the bundle you'll need to run the split.py program to split the 
resulting resourcepack into subpacks per biome:
```sh
$ python split.py split.py build/default/game.graph.json build/packs BUNDLE_EXPORT_FOLDER
Collections:
  biome01 (5 dependencies)
  biome02 (5 dependencies)
Latest pack: build/packs/defold.resourcepack_js-web_5712998414135861967.zip
Creating zip for collection biome01 to BUNDLE_EXPORT_FOLDER/biome01.zip
Creating zip for collection biome02 to BUNDLE_EXPORT_FOLDER/biome02.zip
```

Then the game will only download the zip per biome when needed.
