-- Lightroom XMP File Loader Plugin Sample Code

local LrApplication = import 'LrApplication'
local LrDialogs = import 'LrDialogs'
local LrFileUtils = import 'LrFileUtils'
local LrPathUtils = import 'LrPathUtils'
local LrProgressScope = import 'LrProgressScope'
local LrTasks = import 'LrTasks'

local function loadJsonFile(path)
    local motogpAnalysisJsonPath = LrPathUtils.child(path, "motogp_analysis.json")

    if not LrFileUtils.exists(motogpAnalysisJsonPath) then
        LrDialogs.message("Error", "motogp_analysis.json not found for photo: " .. photo:getFormattedMetadata("fileName"))
        return nil
    end
    local file = io.open(motogpAnalysisJsonPath, "r")
    if not file then
        LrDialogs.message("Error", "Could not open motogp_analysis.json for photo: " .. photo:getFormattedMetadata("fileName"))
        return nil
    end
    local content = file:read("*all")
    file:close()
    
    -- LrDialogs.message("GO", content)
    local json = require("dkjson") -- Ensure dkjson.lua is in your plugin folder
    local data, pos, err = json.decode(content, 1, nil)
    if err then
        LrDialogs.message("Error", "Error parsing JSON: " .. err)
        return nil
    end
    return data
end

local function selectAndLoadJsonFile()
    -- Open file selection dialog
    local result = LrDialogs.runOpenPanel({
        title = "Select motogp_analysis.json file",
        canChooseFiles = true,
        canChooseDirectories = false,
        allowsMultipleSelection = false,
        canCreateDirectories = false,
        fileTypes = "json",  -- only show JSON files
    })

    if not result then  -- user cancelled
        LrDialogs.message("Cancelled", "No file was selected")
        return nil
    end

    -- result is a table with selected paths
    local jsonPath = result[1]  -- get first (only) selected path
    
    -- Now you can use the selected path
    local file = io.open(jsonPath, "r")
    if not file then
        LrDialogs.message("Error", "Could not open selected file")
        return nil
    end

    local content = file:read("*all")
    file:close()
    
    return content
end

-- Main function to load XMP file and apply to selected photos
local function applyMotoGPAnalysisJson()
    
    -- LrDialogs.message("GO")
    
    LrTasks.startAsyncTask(function()
        local content = selectAndLoadJsonFile()
        if not content then
            return
        end
        local json = require("dkjson") -- Ensure dkjson.lua is in your plugin folder
        local data, pos, err = json.decode(content, 1, nil)
        if err then
            LrDialogs.message("Error", "Error parsing JSON: " .. err)
            return
        end
        local jsondata = data

        local catalog = LrApplication.activeCatalog()
        local selectedPhotos = catalog:getTargetPhotos()
        
        if #selectedPhotos == 0 then
            LrDialogs.message("No Selection", "Please select one or more photos to apply XMP metadata to.")
            return
        end
        
        -- Create progress scope
        local progress = LrProgressScope({
            title = "Processing Photos",
            caption = "Reading XMP data...",
        })

        -- Process each photo
        for i, photo in ipairs(selectedPhotos) do

            -- if jsondata == nil then
            --     local filePath = photo:getRawMetadata("path")
            --     local parentPath = LrPathUtils.parent(filePath)
            --     -- local motogpAnalysisJsonPath = LrPathUtils.child(parentPath, "motogp_analysis.json")
            -- end

            if progress:isCanceled() then break end
            
            progress:setPortionComplete(i-1, #selectedPhotos)
            progress:setCaption(string.format("Processing photo %d of %d", i, #selectedPhotos))

            local photoMetadata = nil
            for _, item in ipairs(jsondata.photos) do
                if LrPathUtils.removeExtension(item.filename) == LrPathUtils.removeExtension(photo:getFormattedMetadata("fileName")) then
                    photoMetadata = item.metadata
                    break
                end
            end
            if not photoMetadata then
                -- LrDialogs.message("Error", "No metadata found for photo: " .. photo:getFormattedMetadata("fileName"))
            else
                -- LrDialogs.message("Processing"," photo " .. motogpAnalysisJsonPath .. photo:getFormattedMetadata("fileName") .. photoMetadata.laplacianvariance)
                -- Your photo processing code here
                catalog:withWriteAccessDo("Update photo metadata", function()
                    -- Example: Set metadata for each photo
                    if photoMetadata.laplacianvariance then
                        photo:setPropertyForPlugin(_PLUGIN, 'laplacianvariance', photoMetadata.laplacianvariance)
                    end
                    if photoMetadata.inframed then
                        photo:setPropertyForPlugin(_PLUGIN, 'inframed', photoMetadata.inframed)
                    end
                    if photoMetadata.inframed then
                        photo:setPropertyForPlugin(_PLUGIN, 'motorcyclesize', photoMetadata.motorcyclesize)
                    end
                    if photoMetadata.inframed then
                        photo:setPropertyForPlugin(_PLUGIN, 'centered', photoMetadata.centered)
                    end
                end)
            end
        end

        progress:done()
        LrDialogs.message("Complete", string.format("Processed %d photos", #selectedPhotos))

        
    end)
end


applyMotoGPAnalysisJson()
-- Export the function for use in plugin
return nil