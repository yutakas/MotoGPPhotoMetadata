# Privacy Policy

## What This Plugin Does

MotoGP Photo Metadata is a Lightroom Classic plugin that analyzes motorcycle racing photos locally and optionally uses the OpenAI API for team identification.

## Data Processing

### Local Processing (no data leaves your machine)

- **YOLO object detection** runs entirely on your local machine to detect motorcycles in photos.
- **Sharpness, framing, and size calculations** are performed locally.
- Photo thumbnails are sent only to a **local HTTP server** running on your own computer (`localhost:8500`).

### OpenAI API (data sent externally)

When the OpenAI team-identification feature is enabled (by providing an OpenAI API key), the following data is sent to OpenAI's servers:

- A **cropped JPEG image** of the detected motorcycle region (not the full photo).
- The **year extracted from the file path or EXIF data** (used to identify the racing season).

No other personal data, filenames, or metadata is sent to OpenAI.

OpenAI's data usage policy for API calls states that API inputs and outputs are **not used to train their models**. See [OpenAI API Data Usage Policy](https://openai.com/policies/api-data-usage-policies) for details.

### Cached Data

Analysis results are cached locally in `openai_cache.json` to avoid redundant API calls. This file contains:

- Local file paths of analyzed photos.
- The analysis results (team name, bike color, sponsors, logos).

This file never leaves your machine.

## Data Storage

All data is stored locally on your machine:

- Plugin metadata is stored in your Lightroom catalog.
- OpenAI response cache is stored in the server directory.
- No data is stored on any remote server (other than what OpenAI retains per their policy).

## Your Control

- You can **disable OpenAI analysis** by not providing an API key in the plugin settings.
- You can **delete cached results** by removing the `openai_cache.json` file.
- You can **remove all plugin metadata** from Lightroom by removing the plugin.

## Third-Party Services

| Service | Purpose | Privacy Policy |
|---|---|---|
| OpenAI API | Motorcycle team identification via vision analysis | [openai.com/policies/privacy-policy](https://openai.com/policies/privacy-policy) |

## Contact

For privacy questions, please open an issue on the [GitHub repository](https://github.com/yutakasuzue/MotoGPPhotoMetadata).
