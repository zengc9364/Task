# stage3.py
import argparse
import requests
import sys

parser = argparse.ArgumentParser()
parser.add_argument("url")
parser.add_argument("-o", "--output")

class Args:
    def __init__(self, url, output=None):
        self.url = url
        self.output = output

args = Args(
    url="https://raw.githubusercontent.com/python/cpython/main/README.rst",
    # output="custom_readme.rst"  
)

filename = args.output if args.output else args.url.split('/')[-1]
response = requests.get(args.url, stream=True)
total_size = int(response.headers.get('content-length', 0))
downloaded = 0

with open(filename, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)
        downloaded += len(chunk)
        if total_size:
            percent = (downloaded / total_size) * 100
            sys.stdout.write(f"\rProgress: {downloaded}/{total_size} Bytes [{percent:.1f}%]")
            sys.stdout.flush()

print("\nDone.")
