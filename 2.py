import urllib.request
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any
import argparse


def download_file(url: str, output_filename: str):
    try:
        if output_filename:
            filename = output_filename
        else:
            url_path = url.split('?')[0]
            last_part = url_path.split('/')[-1]
            if '.' in last_part:
                filename = last_part
            else:
                filename = "downloaded_file"
        filepath = Path(filename)
        print(f"Downloading {url} to {filepath}...")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            out_file.write(response.read())
            
        print("Download completed successfully!")
        print(f"File saved to: {filepath.absolute()}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple wget-like CLI tool")
    parser.add_argument("url", nargs='?', default="https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Tux.svg/200px-Tux.svg.png", help="URL to download")
    parser.add_argument("-o", "--output", help="Output filename")
    args, unknown = parser.parse_known_args()
    download_file(args.url, args.output)
