# Tool usage guide

These tools browse a cement-bag image dataset stored in Amazon S3. They can list object metadata, open images, and download small samples. They do not upload, delete, or change S3 objects.

Run the commands below from the **project root** (the folder containing `tools/`, `data/`, and `experiment/`). Replace `YOUR-BUCKET`, `YOUR-REGION`, and example filenames with values supplied by the dataset owner.

## Files

| File | Purpose |
| --- | --- |
| `s3_gallery.py` | Starts a local browser gallery with filename and time-component filters. |
| `s3-gallery.html` | Browser interface served by `s3_gallery.py`; start the server to use it. |
| `s3_dataset.py` | Command-line helper for bucket discovery, listings, single-image viewing, inventories, and sample downloads. |
| `requirements-s3.txt` | Python dependencies: Boto3 and Pillow. |
| `../Open S3 Gallery.command` | macOS launcher for the gallery using the project's `.venv`. |

## 1. Set up Python

Install Python 3 if needed, open a terminal in the project root, and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r tools/requirements-s3.txt
```

On later visits, activate the existing environment with:

```bash
source .venv/bin/activate
```

The activation command above is for macOS/Linux. In Windows PowerShell, use `.venv\Scripts\Activate.ps1`.

## 2. Supply your credentials

Obtain an AWS credential CSV from the dataset owner. By default, both tools read:

```text
data/svc-rtms-cbdt-s3sync_accessKeys.csv
```

The CSV must contain exactly one data row with these columns:

- `Access key ID`
- `Secret access key`
- `Session token` (optional; required when using temporary credentials)

To use another CSV, pass `--credentials path/to/credentials.csv`. Both tools explicitly read the CSV; setting AWS environment variables or configuring an AWS CLI profile alone does not replace this requirement.

Keep credential files local. The project `.gitignore` excludes the default CSV, other files named `*accessKeys.csv`, and local data files. A credential CSV stored elsewhere under a different name needs its own ignore rule.

## 3. Browse images in the gallery

For the project's configured bucket and region:

```bash
python tools/s3_gallery.py --open
```

On macOS, you can also double-click **Open S3 Gallery.command** in the project root after setting up `.venv` and the default credential CSV.

To choose a different bucket, region, credential file, or port:

```bash
python tools/s3_gallery.py \
  --bucket YOUR-BUCKET \
  --region YOUR-REGION \
  --credentials data/your_accessKeys.csv \
  --port 8765 \
  --open
```

The default address is [http://127.0.0.1:8765/](http://127.0.0.1:8765/). Keep the terminal running while using the gallery; press **Ctrl+C** to stop the server.

### Gallery controls

- **Scroll** to load more images. Click a thumbnail to open a larger view.
- Use the **previous/next buttons** or keyboard **left/right arrows** in the image viewer.
- **Filename search** matches the start of a filename, such as `1970_01_17_05`.
- **From / Through** filter filenames using year, month, day, hour, and minute components. **Any** ignores that component. Click **Apply filter** after changing selections.
- Choose the same date, hour, and minute in both bounds to select one minute. The ending minute is included.
- To select hour `05` across all dates, set Hour to `05` in both bounds and leave every other component as **Any**.
- **Show all** clears both the filename search and time filters.
- **Thumbnail size** adjusts the grid display size.

The filename index is built when the server starts. Wait for indexing to finish; restart the server to refresh it after bucket contents change. Time filters use timestamps encoded in filenames, which may differ from actual capture times.

The gallery does not save local image files. Your browser loads the original images from S3, so browsing still transfers image data. Credentials stay on the local server; the browser receives temporary signed image links. Browser memory and history are controlled by the browser.

## 4. Use the command-line dataset helper

For `s3_dataset.py`, put `--region` and `--credentials` **before** the subcommand. Its region defaults to `us-east-1`; specify the actual region when known. The gallery defaults to `ap-southeast-1`.

An S3 address has the form `s3://bucket/prefix/`. Use `s3://bucket/` for the bucket root, or include the complete filename when viewing one image.

### List accessible buckets

```bash
python tools/s3_dataset.py --region YOUR-REGION buckets
```

Bucket discovery may be denied even when you can access a known bucket. If so, obtain its exact address from the dataset owner and use `list` directly.

### List files and folders

```bash
python tools/s3_dataset.py --region YOUR-REGION \
  list 's3://YOUR-BUCKET/' --limit 30
```

This lists up to 30 immediate files or folders. To inspect a folder, replace the address with `s3://YOUR-BUCKET/YOUR-PREFIX/`.

### Open one image without downloading a local file

```bash
python tools/s3_dataset.py --region YOUR-REGION \
  view 's3://YOUR-BUCKET/YOUR-PREFIX/image.jpg'
```

This opens a temporary signed link in your default browser, valid for up to 15 minutes. AWS verifies permissions when the browser requests the image. Keep signed links private while they are valid.

### Export an inventory

```bash
python tools/s3_dataset.py --region YOUR-REGION \
  inventory 's3://YOUR-BUCKET/' --out data/s3-inventory.csv
```

This scans all objects under the supplied prefix and exports metadata to CSV, including object keys, sizes, modification times, and image flags. It does not download image contents.

### Download a small sample and build an offline gallery

```bash
python tools/s3_dataset.py --region YOUR-REGION \
  preview 's3://YOUR-BUCKET/' --limit 24 --out data/s3-preview
```

Open `data/s3-preview/index.html` in your browser. On macOS:

```bash
open data/s3-preview/index.html
```

The output folder contains downloaded images, thumbnails, a `manifest.csv`, and the HTML gallery. Without `--random`, the helper selects the first eligible images in S3 listing order.

For a reproducible random sample:

```bash
python tools/s3_dataset.py --region YOUR-REGION \
  preview 's3://YOUR-BUCKET/' --limit 60 --random --seed 42 \
  --out data/s3-preview/random-60
```

Random sampling scans all object keys under the prefix before downloading the selected images. Large buckets can take time to scan. Listing and viewing/downloading use AWS requests and may incur charges.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| `ModuleNotFoundError` | Activate `.venv` and install `tools/requirements-s3.txt`. |
| Missing CSV or `Local setup error` | Check the credential path, the CSV column names, and that it contains exactly one data row. |
| `AccessDenied` | Bucket discovery needs `s3:ListAllMyBuckets`; listing needs `s3:ListBucket`; reading images needs `s3:GetObject`, and some encrypted objects also need KMS decrypt access. Ask the dataset owner for the appropriate permissions. |
| `InvalidAccessKeyId`, `SignatureDoesNotMatch`, or `ExpiredToken` | Ask the dataset owner to verify or renew the credentials and any required session token. |
| `NoSuchBucket` | Verify the bucket name. |
| AWS connection error | Check your internet connection and the bucket region. |
| Gallery port is already in use | Reuse the running viewer if it matches your configuration, or start with `--port 8766`. |
| No matching gallery images | Clear filters with **Show all**, wait for indexing, and check that filenames match the timestamp format `YYYY_MM_DD_HH_MM_SS.jpg`. |

For all available options:

```bash
python tools/s3_gallery.py --help
python tools/s3_dataset.py --help
python tools/s3_dataset.py preview --help
```

For project-specific bucket details and further examples, see [the S3 guide](../data/S3-GUIDE.md). Local datasets, inventories, previews, and credentials under `data/` stay excluded from Git; this README and the tool source files remain eligible for publication.
