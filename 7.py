import urllib.request
import urllib.error
import base64
import sys
from pathlib import Path
from typing import Dict, Any
import argparse
import time


def download_with_progress(url: str, output_filename: str, retries: int, timeout: float = 10,
                           user=None, password=None, headers: Dict[str, Any] = None):
    if headers is None:
        headers = {}
    attempt = 0
    while attempt < retries:
        try:
            if output_filename:
                filename = output_filename
            else:
                url_path = url.split('?')[0]
                last_part = url_path.split('/')[-1]
                filename = last_part if '.' in last_part else "downloaded_file"
            filepath = Path(filename)

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0.0.0 Safari/537.36')
            req.add_header('Accept', '*/*')
            req.add_header('Connection', 'keep-alive')
            
            for key, value in headers.items():
                req.add_header(key.strip(), value.strip())

            if user and password:
                auth_str = f"{user}:{password}"
                auth_bytes = auth_str.encode('utf-8')
                base64_auth = base64.b64encode(auth_bytes).decode('utf-8')
                req.add_header("Authorization", f"Basic {base64_auth}")

            opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
            urllib.request.install_opener(opener)

            response = urllib.request.urlopen(req, timeout=timeout)
            status_code = response.getcode()
            print(f"Attempt {attempt+1}/{retries} | HTTP Status: {status_code}")

            total_size = int(response.headers.get('Content-Length', 0))
            block_size = 65536  
            downloaded = 0

            start_time = time.time()
            last_time = start_time
            last_downloaded = 0

            with open(filepath, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    f.write(buffer)
                    downloaded += len(buffer)

                    current_time = time.time()
                    if total_size > 0:
                        speed = (downloaded - last_downloaded) / (current_time - last_time + 1e-3)
                        last_downloaded = downloaded
                        last_time = current_time

                        if speed >= 1024 * 1024:
                            speed_str = f"{speed/(1024*1024):.2f} MB/s"
                        elif speed >= 1024:
                            speed_str = f"{speed/1024:.2f} KB/s"
                        else:
                            speed_str = f"{speed:.2f} B/s"

                        eta = (total_size - downloaded) / speed if speed > 0 else 0
                        eta_str = f"{int(eta//60)}m{int(eta%60)}s" if eta >= 60 else f"{int(eta)}s"

                        progress = (downloaded / total_size) * 100
                        bar = '=' * int(progress // 2) + '>' + '-' * (49 - int(progress // 2))
                        print(f"\r[{bar}] {progress:.1f}% | {speed_str} | ETA: {eta_str}", end="")

            print("\n\nDownload completed successfully!")
            print(f"File saved to: {filepath.absolute()}")
            return

        except Exception as e:
            attempt += 1
            print(f"\nError: {e}")
            print(f"Attempt {attempt} failed")
            if attempt < retries:
                print(f"Retrying in 2 seconds... ({retries - attempt} attempts left)\n")
                time.sleep(2)

    print(f"\nAll {retries} attempts failed. Download aborted.")
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple wget-like CLI tool")
    parser.add_argument("url", nargs='?', 
                       default="https://httpbin.org/basic-auth/test/123", 
                       help="URL to download")
    parser.add_argument("-o", "--output", help="Output filename")
    parser.add_argument("-r", "--retry", type=int, default=3, help="Number of retries (default: 3)")
    parser.add_argument("--user", help="Username for basic authentication")
    parser.add_argument("--password", help="Password for basic authentication")
    parser.add_argument("--header", action="append", help="Custom header (e.g., --header 'Key: Value')")

    args, unknown = parser.parse_known_args()

    custom_headers = {}
    if args.header:
        for h in args.header:
            try:
                key, value = h.split(':', 1)
                custom_headers[key] = value
            except ValueError:
                print(f"Invalid header format: {h}")

    download_with_progress(
        url=args.url,
        output_filename=args.output,
        retries=args.retry,
        timeout=10,
        user=args.user,
        password=args.password,
        headers=custom_headers
    )
