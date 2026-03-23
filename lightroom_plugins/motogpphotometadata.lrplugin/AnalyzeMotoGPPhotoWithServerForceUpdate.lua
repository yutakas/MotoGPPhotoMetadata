-- Force Update variant: bypasses the server-side OpenAI cache
-- and re-analyzes all selected photos from scratch.

local LrApplication = import 'LrApplication'
local LrDialogs = import 'LrDialogs'
local LrFileUtils = import 'LrFileUtils'
local LrPathUtils = import 'LrPathUtils'
local LrProgressScope = import 'LrProgressScope'
local LrTasks = import 'LrTasks'
local LrHttp = import 'LrHttp'
local LrPrefs = import 'LrPrefs'

local _pendingThumbnailRequests = {}

local logFilename = LOC "yutakas.plugin.motogpphotometadata"
local logger = import 'LrLogger'( logFilename )
logger:enable( "logfile" )

local function applyMotoGPAnalysisJson(forceUpdate)
    logger:trace('applyMotoGPAnalysisJson start (forceUpdate=' .. tostring(forceUpdate) .. ') ----------------------------------------')
    LrTasks.startAsyncTask(function()

        local progress = LrProgressScope({
            title = "Analyzing MotoGP Photos (Force Update)...",
            caption = "Please wait...",
            functionContext = nil,
        })

        local processed_count = 0
        local catalog = LrApplication.activeCatalog()
        local selectedPhotos = catalog:getTargetPhotos()
        if #selectedPhotos == 0 then
            LrDialogs.message("No Selection", "Please select one or more photos to analyze.")
            return
        end

        local json = require("dkjson")

        for i, photo in ipairs(selectedPhotos) do
            logger:trace( string.format("start processing photo %d %s", i, photo:getFormattedMetadata("fileName")) )
            if progress:isCanceled() then break end

            progress:setPortionComplete(i-1, #selectedPhotos)
            progress:setCaption(string.format("Processing photo %d of %d", i, #selectedPhotos))

            local width = photo:getRawMetadata("width") / 2
            local height = photo:getRawMetadata("height") / 2
            local done = false
            local thumbnailPixels = nil
            local thumbnailErr = nil
            local request = nil

            logger:trace('requestJpegThumbnail calling')
            request = photo:requestJpegThumbnail( width, height, function( pixels, errMsg )
                logger:trace('requestJpegThumbnail callback started')
                thumbnailPixels = pixels
                thumbnailErr = errMsg
                if request then
                    _pendingThumbnailRequests[ request ] = nil
                end
                done = true
                logger:trace('requestJpegThumbnail callback ended')
            end )

            if request then
                logger:trace('requestJpegThumbnail called - set true to _pendingThumbnailRequests')
                _pendingThumbnailRequests[ request ] = true
            else
                logger:error(string.format("Could not create thumbnail request for %s", photo:getFormattedMetadata("fileName")))
                done = true
            end

            logger:trace('requestJpegThumbnail  waiting for callback to complete')
            local timeout = 300
            while not done and timeout > 0 do
                LrTasks.sleep(0.1)
                timeout = timeout - 1
            end
            if not done then
                logger:error(string.format("Timeout waiting for thumbnail for %s", photo:getFormattedMetadata("fileName")))
                if request then _pendingThumbnailRequests[ request ] = nil end
            elseif thumbnailPixels then
                logger:trace('requestJpegThumbnail pixels ok pixel size %s', string.len( thumbnailPixels ))

                local url = 'http://localhost:8500/processimg'
                local imagePath = photo:getRawMetadata("path") or ""
                local prefs = LrPrefs.prefsForPlugin()
                local headers = {
                    { field = 'Content-Type', value = "image/jpeg" },
                    { field = 'Content-Length', value = string.len( thumbnailPixels ) },
                    { field = 'X-Image-Path', value = imagePath },
                    { field = 'X-OpenAI-Api-Key', value = prefs.openai_api_key or "" },
                    { field = 'X-OpenAI-Model', value = prefs.openai_model or "" },
                    { field = 'X-Force-Update', value = forceUpdate and "true" or "false" },
                }
                local totalSize = string.len( thumbnailPixels )
                local response, _ = LrHttp.post(url, function() return thumbnailPixels end, headers, "POST", 600, totalSize)
                if not response then
                    logger:error("No response from server – is it running on localhost:8500?")
                    LrDialogs.message("Error", "No response from server. Make sure the analysis server is running on localhost:8500.")
                elseif response == "" then
                    logger:error("Empty response from server")
                    LrDialogs.message("Error", "Empty response from server.")
                else
                local data, _, err = json.decode(response, 1, nil)
                if err then
                    LrDialogs.message("Error", "Error parsing JSON: " .. err)
                else
                    logger:trace('http returned '.. response)
                    local photoMetadata = data
                    if not photoMetadata then
                        LrDialogs.message("Error", "No metadata found for photo: " .. photo:getFormattedMetadata("fileName") .. response)
                    else
                        logger:trace('catalog:withWriteAccessDo calling')
                        catalog:withWriteAccessDo("Update photo metadata", function()
                            logger:trace('catalog:withWriteAccessDo started')
                            if photoMetadata.laplacianvariance then
                                photo:setPropertyForPlugin(_PLUGIN, 'laplacianvariance', photoMetadata.laplacianvariance)
                            end
                            if photoMetadata.tenengrad then
                                photo:setPropertyForPlugin(_PLUGIN, 'tenengrad', photoMetadata.tenengrad)
                            end
                            if photoMetadata.inframed then
                                photo:setPropertyForPlugin(_PLUGIN, 'inframed', photoMetadata.inframed)
                                photo:setPropertyForPlugin(_PLUGIN, 'motorcyclesize', photoMetadata.motorcyclesize)
                                photo:setPropertyForPlugin(_PLUGIN, 'centered', photoMetadata.centered)
                            end
                            if photoMetadata.motogp_team then
                                photo:setPropertyForPlugin(_PLUGIN, 'motogp_team', photoMetadata.motogp_team)
                            end
                            if photoMetadata.bike_color then
                                photo:setPropertyForPlugin(_PLUGIN, 'bike_color', photoMetadata.bike_color)
                            end
                            if photoMetadata.sponsor_names then
                                photo:setPropertyForPlugin(_PLUGIN, 'sponsor_names', photoMetadata.sponsor_names)
                            end
                            if photoMetadata.logos then
                                photo:setPropertyForPlugin(_PLUGIN, 'logos', photoMetadata.logos)
                            end
                            processed_count = processed_count + 1
                            logger:trace('catalog:withWriteAccessDo ended')
                        end)
                    end
                end
                end -- if not response
            else
                logger:error(string.format("requestJpegThumbnail failed for %s: %s", photo:getFormattedMetadata("fileName"), thumbnailErr or "unknown error"))
            end
        end

        progress:done()
        logger:trace(string.format("Completed Processed %d photos %d succeeded", #selectedPhotos, processed_count))
        LrDialogs.message("Complete", string.format("Processed %d photos %d succeeded", #selectedPhotos, processed_count))

    end)

end


applyMotoGPAnalysisJson(true)
return nil
