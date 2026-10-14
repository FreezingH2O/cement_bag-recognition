# Viewing your cement-bag dataset in S3

Your `svc-rtms-cbdt-s3sync_accessKeys.csv` contains an **Access key ID** and a **Secret access key**. Together they let software authenticate to AWS. They are not an AWS website username/password, and they do not tell us which bucket contains the dataset.

An address such as `s3://my-bucket/phase1/` has two parts: `my-bucket` is the bucket, and `phase1/` is a prefix (similar to a folder). An individual image has an object key such as `phase1/images/bag001.jpg`.

## Your verified bucket

### Browse a scrolling grid like Finder

Double-click `Open S3 Gallery.command` in the project folder. It opens a local viewer in your browser, or reopens the viewer if it is already running.

You can also start it from Terminal:

```bash
cd /Users/airadajitauleeruk/Desktop/capstone
.venv/bin/python tools/s3_gallery.py --open
```

The viewer is at **http://127.0.0.1:8765/**. Scroll to load more images, click a thumbnail to enlarge it, and use the arrow buttons or keyboard arrows to move between images.

**Filename search** matches the beginning of the full filename, for example `1970_01_17_05`. You can use it alone or combine it with the From/Through dropdowns; both conditions must match. Click **Apply filter** (or press Enter in search) to apply it. **Show all** clears the search and time range together.

Use **From** and **Through** to filter by the time encoded in the filename. Each bound has separate **Year, Month, Day, Hour, and Minute dropdowns**, with no seconds field. Every dropdown has **Any**, which skips that component when comparing filenames to that bound. Later components remain selectable even when earlier ones are Any. Dropdowns contain distinct values from the filenames; changing earlier selections updates the choices for later components while preserving valid selections. New or invalidated selections default to Any. Click **Apply filter** to use the selected range.

The entire ending minute is included. For the observed first green run, choose From `1970 / 01 / 17 / 02 / Any` and Through `1970 / 01 / 17 / 04 / Any`. To see one minute, select the same date, hour, and minute in both bounds. To see hour 05 on every date, set Hour to 05 in both bounds and leave all other components as Any. To see hour 05 on day 17, additionally set Day to 17 in both bounds. Comparisons use the remaining selected components in filename order. Setting all five components of one bound to Any makes that entire bound unrestricted. **Show all** clears both bounds and search. These values refer to the filename clock, not verified calendar capture dates.

Independent Any choices use a metadata-only filename index held in server memory. It is prepared once when the viewer starts; the page shows progress while preparing. Images are still loaded directly from S3. Restart the viewer to refresh the index if the bucket contents change.

The local server lists metadata and redirects image requests to temporary S3 links. It does not download or save image files. Your browser receives the original images directly from S3 and scales them into thumbnails; these are not smaller server-generated thumbnail files. Image requests ask the browser not to cache the response, but browser memory and history remain browser-controlled. Viewing still uses network transfer and S3 requests.

Credentials stay in the existing CSV and the server's memory; they are not included in the HTML. The server listens only on your Mac's loopback address. Keep the Terminal window running while you browse, and press Ctrl+C in that window to stop it.

On 12 October 2026, the supplied credentials successfully listed `s3://scg-rtms-cbdt-prod/` and read metadata for an image. The bucket region is **`ap-southeast-1` (Singapore)**. JPEG images are present directly at the bucket root; a folder prefix is not needed for those files. Account-wide bucket discovery was denied, but direct access to this bucket works.

To view a verified image address without saving an image file through the helper:

```bash
cd /Users/airadajitauleeruk/Desktop/capstone
source .venv/bin/activate
python tools/s3_dataset.py --region ap-southeast-1 view 's3://scg-rtms-cbdt-prod/1970_01_17_02_28_30.jpg'
```

To find more image addresses:

```bash
python tools/s3_dataset.py --region ap-southeast-1 list 's3://scg-rtms-cbdt-prod/' --limit 30
```

Replace the filename in the `view` command with a filename from the listing. A full paginated metadata listing on 12 October 2026 found **196,311 JPEG objects**, approximately **16.34 GiB**, directly at the bucket root. This is larger than the stated 50,000-image dataset; confirm which subset is intended for phase one. Every filename parsed as `YYYY_MM_DD_HH_MM_SS.jpg`, spanning `1970_01_17_02_28_30.jpg` to `1970_01_24_16_49_33.jpg`. Most consecutive filename times differ by 1–3 seconds. Treat these as sequence identifiers until the camera clock and filename-generation logic are confirmed; they are not verified real-world capture timestamps or SKU labels.

## The local helper is ready

I installed Boto3 (the AWS Python SDK) and Pillow into this project's `.venv`. The helper reads your existing credential CSV locally, without printing the values or changing your global AWS configuration. It only lists and downloads from S3. It never uploads, deletes, or changes permissions.

Open Terminal and run:

```bash
cd /Users/airadajitauleeruk/Desktop/capstone
source .venv/bin/activate
```

After activation, `python` uses this project's installed packages. On another machine, recreate this setup with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r tools/requirements-s3.txt
```

## 1. Find the bucket

```bash
python tools/s3_dataset.py buckets
```

This prints accessible bucket names if the account permits bucket discovery. If it returns `AccessDenied`, ask the dataset owner for the **exact S3 address and region**. Account-wide bucket discovery can be denied even when access to a specific dataset is allowed.

Replace `YOUR-BUCKET` and `YOUR-PREFIX` below with the real values. Do not run these placeholders unchanged. For an entire bucket, use `s3://YOUR-BUCKET/`.

## 2. Inspect folders and files

```bash
python tools/s3_dataset.py list 's3://YOUR-BUCKET/'
python tools/s3_dataset.py list 's3://YOUR-BUCKET/YOUR-PREFIX/' --limit 30
```

Each command shows up to 30 entries directly under that prefix. Follow the printed `FOLDER` addresses to find the image folder. Preserve capitalization and the trailing slash when listing a folder.

If you know the region, put it **before** the command, for example:

```bash
python tools/s3_dataset.py --region ap-southeast-1 list 's3://YOUR-BUCKET/YOUR-PREFIX/'
```

`ap-southeast-1` is an example, not a verified region for your dataset. Without an explicit region, the helper starts with `us-east-1`; the S3 SDK normally handles bucket-region redirects.

## 3. View a small batch

### View one image directly from S3, without saving an image file

Use `list` to find a full image address. Then run the following, replacing the region and image address with the actual values:

```bash
python tools/s3_dataset.py --region YOUR-REGION view 's3://YOUR-BUCKET/YOUR-PREFIX/image.jpg'
```

This opens your browser with a presigned GET URL, valid for up to 15 minutes (credentials and bucket policy can shorten this). The helper saves no image, thumbnail, gallery, or signed link. The browser still transfers the image to display it; the response requests `no-store`, but browser memory/history behavior remains controlled by the browser. Anyone with the temporary URL can use it while valid, so keep it private. You need the correct bucket region and `s3:GetObject` permission. Generating the link locally does not itself verify access: AWS checks permission when the browser opens it. JPEG, PNG, WebP, GIF, and BMP addresses are supported.

See [AWS's explanation of presigned URLs](https://docs.aws.amazon.com/boto3/latest/guide/s3-presigned-urls.html).

### Download a batch for offline viewing

```bash
python tools/s3_dataset.py preview 's3://YOUR-BUCKET/YOUR-PREFIX/' --limit 24
open data/s3-preview/index.html
```

The helper downloads at most 24 image files, creates thumbnails, and builds a local browser gallery. Click a thumbnail to view the original. Files are stored under `data/s3-preview/images/`, with their S3 addresses in `data/s3-preview/manifest.csv`. Downloads use hashed local names to avoid collisions; the manifest preserves the source identity.

The default batch is the first images in S3 listing order, so it may show one product or session. For a random sample across the selected prefix:

```bash
python tools/s3_dataset.py preview 's3://YOUR-BUCKET/YOUR-PREFIX/' --limit 60 --random --seed 42 --out data/s3-preview/random-60
open data/s3-preview/random-60/index.html
```

Random sampling lists all keys in the prefix, then downloads only the selected images. The HTML uses local files and contains no credentials or presigned URLs. Listing and downloading use AWS requests; larger downloads can incur transfer charges depending on the account and region.

## 4. Inventory the full dataset before downloading it

```bash
python tools/s3_dataset.py inventory 's3://YOUR-BUCKET/YOUR-PREFIX/'
```

This saves `data/s3-inventory.csv` and prints object count, image-file count, and total size in GiB. It follows all S3 listing pages, so it works beyond the first 1,000 objects. It downloads metadata only. Image count is based on filename extensions, not image decoding; 50,000 files do not establish 50,000 independent physical bags. S3 `last_modified` is an object timestamp, not a verified capture time; ETags are not guaranteed content hashes.

Before training, confirm SKU labels, artwork, session/bag identities, duplicate coverage, and whether nearby frames show the same physical bag. Keep related images in the same train/validation/test split. See `experiment/data-protocol.md` for the existing evaluation plan.

## Optional: use the standard AWS CLI

For bulk downloads, install AWS CLI v2 using the [official installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html). Then create a named profile interactively:

```bash
aws configure --profile cement-data
```

At the prompts, paste the Access key ID and Secret access key from your CSV, enter the actual region, and select `json` output. The CLI stores the profile in your local AWS configuration. Do not paste the values into chat or command arguments. Your CSV lacks the `User name` column required by `aws configure import`, so use the interactive command above.

List files and download one image:

```bash
aws s3 ls 's3://YOUR-BUCKET/YOUR-PREFIX/' --profile cement-data
aws s3 cp 's3://YOUR-BUCKET/YOUR-PREFIX/example.jpg' data/example.jpg --profile cement-data
open data/example.jpg
```

For a full download, inspect the inventory size and available disk space first. Preview the action, then run the actual download when ready:

```bash
aws s3 sync 's3://YOUR-BUCKET/YOUR-PREFIX/' data/s3-download/ --profile cement-data --dryrun
aws s3 sync 's3://YOUR-BUCKET/YOUR-PREFIX/' data/s3-download/ --profile cement-data
```

The source is S3 and the destination is local. Re-running sync generally skips files that already match. These commands include all files under the selected prefix, including labels or archives. No full dataset download has been initiated by this setup.

## Troubleshooting

- `AccessDenied` on `buckets`: obtain the bucket address and try `list` directly.
- `AccessDenied` on `list`: ask the owner for `s3:ListBucket` permission on the dataset bucket/prefix.
- `AccessDenied` while downloading: ask for `s3:GetObject` on the image objects; KMS-encrypted files may also require `kms:Decrypt`.
- `InvalidAccessKeyId` / `SignatureDoesNotMatch`: ask the owner to verify the credentials. Temporary credentials additionally require a session token.
- No images found: inspect the folder with `list`. The data may be nested more deeply or packaged in ZIP files.

Keep the credential CSV private. The project `.gitignore` excludes the supplied access-key CSV and local preview/download folders.

References: [Boto3 credentials](https://docs.aws.amazon.com/boto3/latest/guide/credentials.html), [S3 pagination](https://docs.aws.amazon.com/boto3/latest/reference/services/s3/paginator/ListObjectsV2.html), [AWS CLI S3 commands](https://docs.aws.amazon.com/cli/latest/userguide/cli-services-s3-commands.html), [AWS CLI CSV import requirements](https://docs.aws.amazon.com/cli/latest/reference/configure/import.html).
