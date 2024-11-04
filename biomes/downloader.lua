local M = {}

local gitsha = sys.get_config("project.gitsha") -- make sure that this setting is change when building in CI

function M.init()
  print("Checking mounts, current gitsha:", gitsha)
	local mounts = liveupdate.get_mounts()
  for _, mount in ipairs(mounts) do
    if mount.uri:sub(1, 4) == "zip:" then
      if gitsha == "dev-build" then
        print("Dev build, unloading", mount.name)
        liveupdate.remove_mount(mount.name)
      else
        local meta = sys.load_resource("/metadata_" .. mount.name .. ".json")
        if not meta then
          print("Missing metadata, unloading", mount.name)
          liveupdate.remove_mount(mount.name)
        elseif json.decode(meta).gitsha ~= gitsha then
          print("Mount is outdated, unloading", mount.name, gitsha, json.decode(meta).gitsha)
          liveupdate.remove_mount(mount.name)
        else
          print("Mount is up to date", mount.name)
        end
      end
    end
  end
end

function M.load(biome_id, biome_name, missing_resources, callback)
  local zip_filename = biome_name .. ".zip"
  local download_path = sys.get_save_file("biomes", zip_filename)
  local url = "/" .. biome_name .. ".zip"
  http.request(url, "GET", function(self, id, response)
    if response.status == 200 or response.status == 304 then
      liveupdate.add_mount(biome_name, "zip:" .. download_path, 5, function(_uri, _path, _status)
        print("Mounting", _uri, _path, _status)
        callback(biome_id)
      end)
    else
      print("Failed to download archive ", download_path, "from", url, ":", response.status)
    end
  end, nil, nil, {path=download_path})
end

return M
