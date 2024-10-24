local M = {}

M.callback = nil -- set by biomes/loader.script

function M.biome_initialized(data)
  M.callback(data, msg.url())
end

return M
