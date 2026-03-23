local LrView = import 'LrView'
local LrPrefs = import 'LrPrefs'

local function sectionsForTopOfDialog( f, _ )
    local prefs = LrPrefs.prefsForPlugin()

    if not prefs.openai_model or prefs.openai_model == "" then
        prefs.openai_model = "gpt-5-mini"
    end

    return {
        {
            title = "OpenAI Settings",
            synopsis = prefs.openai_api_key and "API Key set" or "API Key not set",

            f:row {
                spacing = f:control_spacing(),
                f:static_text {
                    title = "API Key:",
                    alignment = 'right',
                    width = LrView.share 'label_width',
                },
                f:password_field {
                    value = LrView.bind { key = 'openai_api_key', object = prefs },
                    width_in_chars = 40,
                    tooltip = "Your OpenAI API key",
                },
            },

            f:row {
                spacing = f:control_spacing(),
                f:static_text {
                    title = "Model:",
                    alignment = 'right',
                    width = LrView.share 'label_width',
                },
                f:edit_field {
                    value = LrView.bind { key = 'openai_model', object = prefs },
                    width_in_chars = 25,
                    tooltip = "OpenAI model name (e.g. gpt-5-mini, gpt-4o)",
                },
            },
        },
    }
end

return {
    sectionsForTopOfDialog = sectionsForTopOfDialog,
}
