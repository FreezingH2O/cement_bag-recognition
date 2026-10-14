#!/usr/bin/env python3
"""Read-only S3 dataset explorer. Credentials are read locally, never printed."""
import argparse
import csv
import hashlib
import html
import mimetypes
import random
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlsplit

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
IMAGES = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff'}


def client(args):
    with args.credentials.open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1:
        raise ValueError('Expected exactly one credential row.')
    row = rows[0]
    if not row.get('Access key ID') or not row.get('Secret access key'):
        raise ValueError('CSV needs Access key ID and Secret access key columns.')
    session = boto3.Session(
        aws_access_key_id=row['Access key ID'].strip(),
        aws_secret_access_key=row['Secret access key'].strip(),
        aws_session_token=row.get('Session token') or None,
        region_name=args.region,
    )
    return session.client('s3', config=Config(
        signature_version='s3v4',
        connect_timeout=10, read_timeout=30,
        retries={'mode': 'standard', 'max_attempts': 3},
    ))


def location(uri):
    parsed = urlsplit(uri)
    if parsed.scheme != 's3' or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('Use an S3 address such as s3://bucket/folder/.')
    # S3 object keys are literal strings; preserve spaces and percent characters.
    return parsed.netloc, parsed.path.lstrip('/')


def objects(s3, bucket, prefix, delimiter=None):
    options = {'Bucket': bucket, 'Prefix': prefix}
    if delimiter:
        options['Delimiter'] = delimiter
    yield from s3.get_paginator('list_objects_v2').paginate(**options)


def image_sample(s3, bucket, prefix, limit, randomized, seed):
    selected, seen = [], 0
    rng = random.Random(seed)
    for page in objects(s3, bucket, prefix):
        for obj in page.get('Contents', []):
            if Path(obj['Key']).suffix.lower() not in IMAGES or obj['Size'] == 0:
                continue
            seen += 1
            if len(selected) < limit:
                selected.append(obj)
            elif randomized:
                position = rng.randrange(seen)
                if position < limit:
                    selected[position] = obj
            if not randomized and len(selected) == limit:
                return selected
    if randomized:
        print(f'Sampled {len(selected)} images from {seen:,} image objects (seed {seed}).')
    return selected


def inventory(s3, bucket, prefix, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    count, images, total = 0, 0, 0
    with destination.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['s3_uri', 'key', 'size_bytes', 'last_modified', 'etag', 'is_image'])
        for page in objects(s3, bucket, prefix):
            for obj in page.get('Contents', []):
                key = obj['Key']
                is_image = Path(key).suffix.lower() in IMAGES and obj['Size'] > 0
                writer.writerow([f's3://{bucket}/{key}', key, obj['Size'],
                                 obj['LastModified'].isoformat(), obj['ETag'], is_image])
                count += 1
                images += int(is_image)
                total += obj['Size']
            print(f'Listed {count:,} objects...', flush=True)
    print(f'{count:,} objects; {images:,} image files; {total / 1024**3:.2f} GiB total.')
    print(f'Inventory: {destination.resolve()}')


def preview(s3, bucket, prefix, args):
    selected = image_sample(s3, bucket, prefix, args.limit, args.random, args.seed)
    if not selected:
        print('No images found under this prefix. Use list to inspect its contents.')
        return
    out = args.out.resolve()
    (out / 'images').mkdir(parents=True, exist_ok=True)
    (out / 'thumbs').mkdir(exist_ok=True)
    cards = []
    with (out / 'manifest.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['s3_uri', 'local_file', 'size_bytes', 'width', 'height', 'status'])
        for i, obj in enumerate(selected, 1):
            key = obj['Key']
            # Hash names prevent unsafe remote paths and same-basename collisions.
            name = hashlib.sha256(key.encode()).hexdigest()[:24] + Path(key).suffix.lower()
            local = out / 'images' / name
            if not local.exists() or local.stat().st_size != obj['Size']:
                temporary = local.with_suffix(local.suffix + '.part')
                s3.download_file(bucket, key, str(temporary))
                temporary.replace(local)
            try:
                with Image.open(local) as source:
                    image = ImageOps.exif_transpose(source)
                    width, height = image.size
                    image.thumbnail((480, 360))
                    image.convert('RGB').save(out / 'thumbs' / (name + '.jpg'))
                writer.writerow([f's3://{bucket}/{key}', f'images/{name}', obj['Size'],
                                 width, height, 'ok'])
                label = html.escape(key)
                cards.append(f'<a href="images/{name}" target="_blank" rel="noopener">'
                             f'<img src="thumbs/{name}.jpg" loading="lazy" alt="{label}">'
                             f'<p>{label}</p><small>{width} × {height}</small></a>')
            except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
                writer.writerow([f's3://{bucket}/{key}', f'images/{name}', obj['Size'],
                                 '', '', 'cannot_decode'])
                print(f'Cannot decode image: {key}')
            print(f'{i}/{len(selected)} downloaded: {key}', flush=True)
    mode = f'Random sample, seed {args.seed}' if args.random else 'First images in S3 listing order'
    page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Cement bag dataset preview</title><style>'
            'body{font:16px system-ui;background:#f5f5f5;margin:24px;color:#20252b}'
            'main{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}'
            'a{display:block;background:white;padding:12px;border-radius:10px;color:inherit;text-decoration:none}'
            'img{width:100%;height:240px;object-fit:contain;background:#e9ecef}'
            'p{overflow-wrap:anywhere;font-size:12px}small{color:#556}</style>'
            f'<h1>Cement bag dataset preview</h1><p>{html.escape(mode)}. '
            'Click a thumbnail to view the downloaded original.</p>'
            f'<p>Source: {html.escape("s3://" + bucket + "/" + prefix)}</p>'
            '<main>' + ''.join(cards) + '</main></html>')
    (out / 'index.html').write_text(page, encoding='utf-8')
    print(f'Gallery: {out / "index.html"}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--credentials', type=Path,
                        default=ROOT / 'data/svc-rtms-cbdt-s3sync_accessKeys.csv')
    parser.add_argument('--region', default='us-east-1',
                        help='Actual bucket region if known; default is an initial S3 endpoint.')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('buckets', help='List bucket names, if IAM permits account-wide listing.')
    ls = sub.add_parser('list', help='Show folders and objects immediately under a prefix.')
    ls.add_argument('uri')
    ls.add_argument('--limit', type=int, default=30)
    view = sub.add_parser('view', help='Open one image in the browser without saving an image file.')
    view.add_argument('uri', help='Full S3 address of one image, including its filename.')
    inv = sub.add_parser('inventory', help='List all object metadata to CSV; no image downloads.')
    inv.add_argument('uri')
    inv.add_argument('--out', type=Path, default=ROOT / 'data/s3-inventory.csv')
    prev = sub.add_parser('preview', help='Download a small image sample and make an offline gallery.')
    prev.add_argument('uri')
    prev.add_argument('--limit', type=int, default=24)
    prev.add_argument('--random', action='store_true', help='Scan all keys and sample images uniformly.')
    prev.add_argument('--seed', type=int, default=42)
    prev.add_argument('--out', type=Path, default=ROOT / 'data/s3-preview')
    args = parser.parse_args()
    if hasattr(args, 'limit') and args.limit < 1:
        parser.error('--limit must be at least 1')
    try:
        s3 = client(args)
        if args.command == 'buckets':
            for page in s3.get_paginator('list_buckets').paginate():
                for bucket in page.get('Buckets', []):
                    print(f's3://{bucket["Name"]}/')
            return
        bucket, prefix = location(args.uri)
        if args.command == 'view':
            content_type = mimetypes.guess_type(prefix)[0]
            if content_type not in {'image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/bmp'}:
                raise ValueError('Use the full S3 address of a browser-compatible image.')
            url = s3.generate_presigned_url(
                'get_object', Params={
                    'Bucket': bucket, 'Key': prefix,
                    'ResponseContentDisposition': 'inline',
                    'ResponseContentType': content_type,
                    'ResponseCacheControl': 'no-store',
                }, ExpiresIn=900,
            )
            if not webbrowser.open(url, new=2):
                print('Could not open a browser. Check your default browser setup.', file=sys.stderr)
                return 1
            print('Opened a temporary image link in your browser (valid for up to 15 minutes).')
            print('No image file saved by this helper. Browser access will verify S3 permissions.')
        elif args.command == 'inventory':
            inventory(s3, bucket, prefix, args.out)
        elif args.command == 'preview':
            preview(s3, bucket, prefix, args)
        else:
            count = 0
            for page in objects(s3, bucket, prefix, delimiter='/'):
                for folder in page.get('CommonPrefixes', []):
                    print(f'FOLDER  s3://{bucket}/{folder["Prefix"]}')
                    count += 1
                    if count >= args.limit:
                        return
                for obj in page.get('Contents', []):
                    print(f'{obj["Size"]:>12,} bytes  s3://{bucket}/{obj["Key"]}')
                    count += 1
                    if count >= args.limit:
                        return
            if count == 0:
                print('This prefix has no objects.')
    except ClientError as error:
        code = error.response.get('Error', {}).get('Code', 'Unknown')
        print(f'AWS error: {code}.', file=sys.stderr)
        if code == 'AccessDenied':
            print('Bucket discovery needs ListAllMyBuckets; listing a known bucket needs '
                  'ListBucket; downloading needs GetObject (and sometimes KMS Decrypt). '
                  'A denied buckets command does not prove dataset access is denied.', file=sys.stderr)
        elif code in {'InvalidAccessKeyId', 'SignatureDoesNotMatch', 'ExpiredToken'}:
            print('Ask the dataset owner to verify these credentials and any required session token.',
                  file=sys.stderr)
        elif code == 'NoSuchBucket':
            print('Check the bucket name with the dataset owner.', file=sys.stderr)
        return 1
    except BotoCoreError as error:
        # Avoid printing SDK details that could contain credential material.
        print(f'AWS connection error: {type(error).__name__}. Check network and region.', file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f'Local setup error: {type(error).__name__}. Check paths and arguments.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
