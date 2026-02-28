# MotoGP Photo Metadata Plugin

Analyzes MotoGP photos using YOLO object detection and writes metadata (sharpness, framing, motorcycle size, centering) back into Lightroom Classic via a local Python server.

---

## Requirements

- Lightroom Classic
- Conda
- YOLO model file: `models/yolo12x.pt`

---

## 1. Start the Python Server

The plugin sends photos to a local HTTP server for analysis. Start it before using the plugin in Lightroom.

```bash
conda activate motogp-server
cd /path/to/MotoGPImageClustering/lightroom_plugins_server
python motogp_analysis_server.py
```

The server starts on `http://localhost:8500`. Leave this terminal running.

### First-time setup (install dependencies)

```bash
conda activate motogp-server
pip install opencv-python-headless numpy ultralytics torch
```

---

## 2. Install the Lightroom Plugin

1. Open Lightroom Classic
2. Go to **File → Plug-in Manager**
3. Click **Add** (bottom left)
4. Navigate to and select the folder:
   ```
   lightroom_plugins/motogpphotometadata.lrplugin
   ```
5. The plugin **MotoGP Photo Metadata** should appear with status **Installed and running**
6. Click **Done**

---

## 3. Invoke the Plugin

1. In the **Library** module, select one or more photos to analyze
2. Go to **Library → Plug-in Extras → Analyze MotoGP Photos**
3. A progress bar appears while photos are sent to the server
4. When complete, a dialog shows how many photos were processed

### What gets written

The following custom metadata fields are populated per photo:

| Field | Description |
|---|---|
| `laplacianvariance` | Laplacian variance sharpness score of the motorcycle region (higher = sharper) |
| `tenengrad` | Tenengrad sharpness score of the motorcycle region (higher = sharper) |
| `inframed` | `true` if the motorcycle is fully within the frame edges |
| `motorcyclesize` | Relative size of the motorcycle in the frame (rounded to nearest 10) |
| `centered` | `true` if the motorcycle center is near the image center |

### Viewing the metadata

The custom fields appear in the **Metadata** panel in the Library module. Select the **MotoGP Photo Metadata** tagset from the metadata panel dropdown to see them.

---

## Troubleshooting

**"Timeout waiting for thumbnail"**
- Build previews first: **Library → Previews → Build Standard-Sized Previews**, then retry.

**HTTP error / no response**
- Make sure the Python server is running (`python motogp_analysis_server.py`) before invoking the plugin.

**Plugin not appearing in Plug-in Extras**
- Confirm you are in the **Library** module (not Develop).
- Re-check the plugin is listed as **Installed and running** in Plug-in Manager.
