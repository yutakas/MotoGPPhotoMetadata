# MotoGP Photo Metadata Plugin

Analyzes MotoGP photos using YOLO object detection and OpenAI vision analysis, then writes metadata (team name, bike color, sharpness, framing, motorcycle size, centering) back into Lightroom Classic via a local Python server.

**License:** [AGPL-3.0](LICENSE) (due to the [Ultralytics YOLO](https://www.ultralytics.com/license) dependency)

---

## Requirements

- Lightroom Classic
- Python 3.10+ (Conda recommended)
- YOLO model file: `models/yolo12x.pt` (download separately -- not included in this repo)
- OpenAI API key (optional, for team identification)

---

## 1. First-Time Setup

```bash
conda create -n motogp-server python=3.12
conda activate motogp-server
pip install -r requirements.txt
```

Copy the environment template and add your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Download the YOLO model file and place it at `models/yolo12x.pt`.

---

## 2. Start the Python Server

The plugin sends photos to a local HTTP server for analysis. Start it before using the plugin in Lightroom.

```bash
conda activate motogp-server
cd lightroom_plugins_server
python motogp_analysis_server.py
```

The server starts on `http://localhost:8500`. Leave this terminal running.

---

## 3. Install the Lightroom Plugin

1. Open Lightroom Classic
2. Go to **File > Plug-in Manager**
3. Click **Add** (bottom left)
4. Navigate to and select the folder:
   ```
   lightroom_plugins/motogpphotometadata.lrplugin
   ```
5. The plugin **MotoGP Photo Metadata** should appear with status **Installed and running**
6. (Optional) In the plugin settings, enter your **OpenAI API key** and **model name** for team identification
7. Click **Done**

---

## 4. Invoke the Plugin

1. In the **Library** module, select one or more photos to analyze
2. Go to **Library > Plug-in Extras** and choose:
   - **Analyze MotoGP Photos** -- uses cached results when available
   - **Analyze MotoGP Photos (Force Update)** -- bypasses cache and re-analyzes with OpenAI
3. A progress bar appears while photos are sent to the server
4. When complete, a dialog shows how many photos were processed

---

## Metadata Fields

The following custom metadata fields are populated per photo:

| Field | Description |
|---|---|
| `laplacianvariance` | Laplacian variance sharpness score of the motorcycle region (higher = sharper) |
| `tenengrad` | Tenengrad sharpness score of the motorcycle region (higher = sharper) |
| `inframed` | `true` if the motorcycle is fully within the frame edges |
| `motorcyclesize` | Relative size of the motorcycle in the frame (rounded to nearest 10) |
| `centered` | `true` if the motorcycle center is near the image center |
| `motogp_team` | Official team name identified by OpenAI (e.g. "Repsol Honda Team") |
| `bike_color` | Primary bike livery color (e.g. "red", "blue", "orange") |
| `sponsor_names` | Comma-separated list of visible sponsor names |
| `logos` | Comma-separated list of visible logos on the bike |

### Viewing the metadata

The custom fields appear in the **Metadata** panel in the Library module. Select the **MotoGP Photo Metadata** tagset from the metadata panel dropdown to see them.

---

## Privacy

- **YOLO detection runs locally** on your machine -- no photos leave your computer for this step.
- **OpenAI analysis** (if enabled) sends a **cropped motorcycle image** to OpenAI's API over HTTPS for team identification. No filenames or personal data are sent.
- See [PRIVACY.md](PRIVACY.md) for full details.

---

## Troubleshooting

**"Timeout waiting for thumbnail"**
- Build previews first: **Library > Previews > Build Standard-Sized Previews**, then retry.

**HTTP error / no response**
- Make sure the Python server is running (`python motogp_analysis_server.py`) before invoking the plugin.

**Plugin not appearing in Plug-in Extras**
- Confirm you are in the **Library** module (not Develop).
- Re-check the plugin is listed as **Installed and running** in Plug-in Manager.

---

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE) due to its dependency on [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) (AGPL-3.0).

### Third-Party Licenses

| Dependency | License |
|---|---|
| [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) | AGPL-3.0 |
| [OpenAI Python SDK](https://github.com/openai/openai-python) | Apache 2.0 |
| [OpenCV](https://github.com/opencv/opencv) | Apache 2.0 |
| [PyTorch](https://github.com/pytorch/pytorch) | BSD-3-Clause |
| [NumPy](https://github.com/numpy/numpy) | BSD-3-Clause |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | BSD-3-Clause |
| [dkjson](http://dkolf.de/dkjson-lua/) | MIT |
