#!/usr/bin/env bash

set -e

# Variables
URL="https://capec.mitre.org/data/archive/capec_latest.zip"
OUTPUT_ZIP="capec_latest.zip"
OUTPUT_DIR="data/"

# Download the ZIP file
echo "Downloading file..."
curl -o "$OUTPUT_ZIP" "$URL"

# Check if the file was downloaded successfully
if [ $? -eq 0 ]; then
    echo "Download completed: $OUTPUT_ZIP"
else
    echo "Failed to download the file."
    exit 1
fi

# Unzip the file
echo "Unzipping file..."
unzip -o "$OUTPUT_ZIP" -d "$OUTPUT_DIR"

# Check if unzipping was successful
if [ $? -eq 0 ]; then
    echo "File unzipped to directory: $OUTPUT_DIR"
else
    echo "Failed to unzip the file."
    exit 1
fi

rm data/ap_schema*.xsd
mv data/capec*.xml data/capecs.xml

# Cleanup
echo "Cleaning up..."
rm -f "$OUTPUT_ZIP"

echo "Done."