#!/usr/bin/env python3
"""Local thumbnail browser. Images go directly from S3 to the web browser."""
import argparse
import json
import mimetypes
import re
import webbrowser
import threading
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from urllib.error import URLError
from urllib.request import urlopen

from botocore.exceptions import BotoCoreError, ClientError
from s3_dataset import ROOT, IMAGES, client

PARTS = ['year', 'month', 'day', 'hour', 'minute']


class FilenameIndex:
    """A metadata-only snapshot for independent wildcard filters."""
    def __init__(self, s3, bucket):
        self.entries = []
        self.count = 0
        self.ready = threading.Event()
        self.error = None
        threading.Thread(target=self.build, args=(s3, bucket), daemon=True).start()

    def build(self, s3, bucket):
        try:
            for page in s3.get_paginator('list_objects_v2').paginate(Bucket=bucket):
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    if Path(key).suffix.lower() not in IMAGES or not obj['Size']:
                        continue
                    match = re.fullmatch(r'(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})_\d{2}\.[^.]+', key)
                    values = tuple(match.groups()) if match else None
                    self.entries.append((key, obj['Size'], values))
                self.count = len(self.entries)
        except (ClientError, BotoCoreError):
            self.error = 'Could not prepare filename filters. Check AWS access and restart the viewer.'
        finally:
            self.ready.set()

    @staticmethod
    def bound(raw):
        values = json.loads(raw) if raw else []
        if not isinstance(values, list) or len(values) > 5:
            raise ValueError('Invalid time components.')
        values = values + [''] * (5 - len(values))
        for i, value in enumerate(values):
            if not isinstance(value, str) or (value and not re.fullmatch(r'\d{4}' if i == 0 else r'\d{2}', value)):
                raise ValueError('Invalid time component.')
            if value:
                low, high = [(1, 9999), (1, 12), (1, 31), (0, 23), (0, 59)][i]
                if not low <= int(value) <= high:
                    raise ValueError('Invalid time component.')
        return values

    def choices(self, level, parents):
        depth = PARTS.index(level)
        values = set()
        for _, _, components in self.entries:
            if components and all(not parents[i] or parents[i] == components[i] for i in range(depth)):
                values.add(components[depth])
        return sorted(values)

    def page(self, lower, upper, prefix, offset):
        start_axes = [i for i, value in enumerate(lower) if value]
        end_axes = [i for i, value in enumerate(upper) if value]
        start = tuple(lower[i] for i in start_axes)
        end = tuple(upper[i] for i in end_axes)
        if start_axes == end_axes and start_axes and start > end:
            raise ValueError('Reversed range.')
        images = []
        while offset < len(self.entries):
            key, size, components = self.entries[offset]
            offset += 1
            if prefix and not key.startswith(prefix):
                continue
            if start_axes or end_axes:
                if components is None:
                    continue
                if start_axes and tuple(components[i] for i in start_axes) < start:
                    continue
                if end_axes and tuple(components[i] for i in end_axes) > end:
                    continue
            images.append({'key': key, 'bytes': size})
            if len(images) == 60:
                break
        return {'images': images, 'next': str(offset) if offset < len(self.entries) else None}


def minute_bounds(start, end):
    """Return inclusive start / exclusive end S3 key bounds at minute precision."""
    def parse(value):
        if not value:
            return None
        parsed = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        if parsed.strftime('%Y-%m-%dT%H:%M') != value:
            raise ValueError('Choose a valid filename time, down to the minute.')
        return parsed
    first, last = parse(start), parse(end)
    if first and last and first > last:
        raise ValueError('The end time must be the same as or later than the start time.')
    return (first.strftime('%Y_%m_%d_%H_%M_00') if first else None,
            (last + timedelta(minutes=1)).strftime('%Y_%m_%d_%H_%M_00') if last else None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bucket', default='scg-rtms-cbdt-prod')
    parser.add_argument('--region', default='ap-southeast-1')
    parser.add_argument('--credentials', type=Path,
                        default=ROOT / 'data/svc-rtms-cbdt-s3sync_accessKeys.csv')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--open', action='store_true', help='Open the viewer in your default browser.')
    args = parser.parse_args()
    origin = f'http://127.0.0.1:{args.port}'
    if args.open:
        try:
            with urlopen(origin + '/api/config', timeout=2) as response:
                existing = json.load(response)
            if existing == {'bucket': args.bucket, 'region': args.region}:
                webbrowser.open(origin)
                print(f'Opened the already running viewer: {origin}', flush=True)
                return
        except (URLError, OSError, ValueError):
            pass
    s3 = client(args)
    index = FilenameIndex(s3, args.bucket)
    page_path = ROOT / 'tools/s3-gallery.html'

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Do not log filenames or temporary signed links.

        def reply(self, status, body, content_type='application/json', location=None):
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            if location:
                self.send_header('Location', location)
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def data(self, status, value):
            self.reply(status, json.dumps(value).encode())

        def do_GET(self):
            # Restrict the credential-bearing service to this loopback origin.
            if self.headers.get('Host') != f'127.0.0.1:{args.port}':
                self.data(403, {'error': 'Use the local viewer address.'})
                return
            if self.headers.get('Origin') not in {None, origin}:
                self.data(403, {'error': 'Only the local viewer may access this service.'})
                return
            if self.headers.get('Sec-Fetch-Site') not in {None, 'none', 'same-origin'}:
                self.data(403, {'error': 'Cross-site requests are not allowed.'})
                return
            route = urlsplit(self.path)
            query = parse_qs(route.query)
            try:
                if route.path == '/':
                    self.reply(200, page_path.read_bytes(), 'text/html; charset=utf-8')
                elif route.path == '/api/config':
                    self.data(200, {'bucket': args.bucket, 'region': args.region})
                elif route.path == '/api/time-options':
                    if not index.ready.is_set():
                        self.data(202, {'count': index.count})
                        return
                    if index.error:
                        self.data(502, {'error': index.error})
                        return
                    level = query.get('level', ['year'])[0]
                    if level == 'all':
                        self.data(200, {'values': {part: index.choices(part, [''] * 5) for part in PARTS}})
                        return
                    if level not in PARTS:
                        raise ValueError('Invalid time component.')
                    parents = index.bound(query.get('parents', [''])[0])
                    self.data(200, {'values': index.choices(level, parents)})
                elif route.path == '/api/list':
                    if not index.ready.is_set():
                        self.data(202, {'count': index.count})
                        return
                    if index.error:
                        self.data(502, {'error': index.error})
                        return
                    lower = index.bound(query.get('fromparts', [''])[0])
                    upper = index.bound(query.get('toparts', [''])[0])
                    offset = int(query.get('token', ['0'])[0])
                    if not 0 <= offset <= len(index.entries):
                        raise ValueError('Invalid page token.')
                    self.data(200, index.page(lower, upper, query.get('prefix', [''])[0], offset))
                elif route.path == '/image':
                    key = query.get('key', [''])[0]
                    content_type = mimetypes.guess_type(key)[0]
                    if content_type not in {'image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/bmp'}:
                        self.data(400, {'error': 'This format cannot be displayed in the browser.'})
                        return
                    # Send a redirect, never fetch or save the image on this server.
                    url = s3.generate_presigned_url('get_object', Params={
                        'Bucket': args.bucket, 'Key': key,
                        'ResponseContentType': content_type,
                        'ResponseContentDisposition': 'inline',
                        'ResponseCacheControl': 'no-store',
                    }, ExpiresIn=900)
                    self.reply(302, b'', location=url)
                else:
                    self.data(404, {'error': 'Not found.'})
            except ClientError as error:
                code = error.response.get('Error', {}).get('Code', 'Unknown')
                self.data(502, {'error': f'AWS returned {code}. Check dataset permissions.'})
            except BotoCoreError:
                self.data(502, {'error': 'Could not connect to AWS. Check your internet connection.'})
            except (ValueError, OverflowError):
                self.data(400, {'error': 'Choose valid start and end filename times; '
                              'the end must be the same as or later than the start.'})
            except (BrokenPipeError, ConnectionResetError):
                pass

    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'S3 image viewer: {origin}', flush=True)
    print(f'Bucket: {args.bucket} | Region: {args.region}', flush=True)
    print('Images stream directly to the browser. Keep this terminal running; Ctrl+C stops it.', flush=True)
    if args.open:
        webbrowser.open(origin)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
