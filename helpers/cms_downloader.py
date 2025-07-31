#!/usr/bin/env python3
"""
# CMS Software Downloader
This script downloads and processes the necessary JAR files and ZIP packages for the CMS MSDRG Grouper
and MCE Editor software, including the necessary dependencies like GFC, GRPC, and SLF4J.
"""

import os
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import logging
from tqdm import tqdm
import time
import zipfile
import shutil
import glob
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cms_downloads.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cms_downloader")

# Constants
DOWNLOAD_DIR = "downloads"
JARS_DIR = "jars"
MSDRG_URL = "https://www.cms.gov/medicare/payment/prospective-payment-systems/acute-inpatient-pps/ms-drg-classifications-and-software"
IOCE_URL = "https://www.cms.gov/medicare/coding-billing/outpatient-code-editor-oce/quarterly-release-files"
JAVA_SOURCE_PATTERN = "java-source.zip"
JAVA_STANDALONE_PATTERN = "java-standalone"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
GFC_JAR = "https://github.com/3mcloud/GFC-Grouper-Foundation-Classes/releases/download/v3.4.9/gfc-base-api-3.4.9.jar"
GRPC_JAR1="https://repo1.maven.org/maven2/com/google/protobuf/protobuf-java/3.22.2/protobuf-java-3.22.2.jar"
GRPC_JAR2="https://repo1.maven.org/maven2/com/google/protobuf/protobuf-java/3.21.7/protobuf-java-3.21.7.jar"
SLF4J_JAR="https://repo1.maven.org/maven2/org/slf4j/slf4j-simple/2.0.9/slf4j-simple-2.0.9.jar" 
SLF4J_JAR2="https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.9/slf4j-api-2.0.9.jar"

def download_sl4j_jar():
    #link https://repo1.maven.org/maven2/org/slf4j/slf4j-simple/2.0.9/slf4j-simple-2.0.9.jar
    #and
    #link https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.9/slf4j-api-2.0.9.jar
    try:
        logger.info(f"Downloading SLF4J JAR file from: {SLF4J_JAR} and {SLF4J_JAR2}")
        path_1 = download_file(SLF4J_JAR, "slf4j-simple-2.0.9.jar")
        path_2 = download_file(SLF4J_JAR2, "slf4j-api-2.0.9.jar")
        return [path_1, path_2]
    except Exception as e:
        logger.error(f"Error downloading SLF4J JAR file: {str(e)}")
        return None

def process_sl4j_jar():
    """Process the SLF4J JAR file."""
    try:
        sl4j_jar_path = download_sl4j_jar()
        if not sl4j_jar_path:
            logger.error("SLF4J JAR file not found")
            return
        
        # Move the JAR file to the jars directory
        for path in sl4j_jar_path:
            dest_path = os.path.join(JARS_DIR, os.path.basename(path))
            shutil.move(path, dest_path)
            logger.info(f"Moved SLF4J JAR file to jars directory: {os.path.basename(path)}")
    except Exception as e:
        logger.error(f"Error processing SLF4J JAR file: {str(e)}")

def create_directory(directory):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")

def download_file(url, filename, directory=DOWNLOAD_DIR):
    """Download a file with progress bar."""
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        file_path = os.path.join(directory, filename)
        
        with open(file_path, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    size = f.write(chunk)
                    bar.update(size)
                    
        logger.info(f"Successfully downloaded: {filename}")
        return file_path
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
        return None

def get_filename_from_url(url):
    """Extract filename from URL."""
    return url.split('/')[-1]

def download_gfc_jar():
    """Download the GFC Base API JAR file."""
    try:
        logger.info(f"Downloading GFC Base API JAR file from: {GFC_JAR}")
        return download_file(GFC_JAR, "gfc-base-api-3.4.9.jar")
    except Exception as e:
        logger.error(f"Error downloading GFC Base API JAR file: {str(e)}")
        return None
    
def download_grpc_jar():
    #link https://repo1.maven.org/maven2/com/google/protobuf/protobuf-java/3.22.2/protobuf-java-3.22.2.jar
    #and
    #link https://repo1.maven.org/maven2/com/google/protobuf/protobuf-java/3.21.7/protobuf-java-3.21.7.jar
    try:
        logger.info(f"Downloading GRPC JAR file from: {GRPC_JAR1} and {GRPC_JAR2}")
        path_1 = download_file(GRPC_JAR1, "protobuf-java-3.22.2.jar")
        path_2 = download_file(GRPC_JAR2, "protobuf-java-3.21.7.jar")
        return [path_1, path_2]
    except Exception as e:
        logger.error(f"Error downloading GRPC JAR file: {str(e)}")
        return None
    
def process_gfc_jar():
    """Process the GFC Base API JAR file."""
    try:
        gfc_jar_path = download_gfc_jar()
        if not gfc_jar_path:
            logger.error("GFC JAR file not found")
            return
        
        # Move the JAR file to the jars directory
        dest_path = os.path.join(JARS_DIR, "gfc-base-api-3.4.9.jar")
        shutil.move(gfc_jar_path, dest_path)
        logger.info("Moved GFC JAR file to jars directory")
    except Exception as e:
        logger.error(f"Error processing GFC JAR file: {str(e)}")

def process_grpc_jar():
    """Process the GRPC JAR file."""
    try:
        grpc_jar_path = download_grpc_jar()
        if not grpc_jar_path:
            logger.error("GRPC JAR file not found")
            return
        
        # Move the JAR file to the jars directory
        for path in grpc_jar_path:
            dest_path = os.path.join(JARS_DIR, os.path.basename(path))
            shutil.move(path, dest_path)
            logger.info(f"Moved GRPC JAR file to jars directory: {os.path.basename(path)}")
    except Exception as e:
        logger.error(f"Error processing GRPC JAR file: {str(e)}")

def process_zip_for_jars(zip_path, prefix=""):
    """Process a ZIP file to extract JAR files with an optional prefix."""
    if not zip_path or not os.path.exists(zip_path):
        logger.error(f"ZIP file not found: {zip_path}")
        return
    
    zip_filename = os.path.basename(zip_path)
    logger.info(f"Processing ZIP file: {zip_filename}")
    
    # Create a temporary directory for extraction
    temp_extract_dir = os.path.join(DOWNLOAD_DIR, f"temp_extract_{int(time.time())}")
    create_directory(temp_extract_dir)
    
    try:
        # Extract the ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        
        # Find any nested ZIP files
        nested_zips = glob.glob(os.path.join(temp_extract_dir, "**", "*.zip"), recursive=True)
        logger.info(f"Found {len(nested_zips)} nested ZIP files in package")
        
        # Process each nested ZIP
        for nested_zip in nested_zips:
            nested_zip_name = os.path.basename(nested_zip)
            logger.info(f"Extracting nested ZIP: {nested_zip_name}")
            
            # Create a subdirectory for this nested ZIP
            nested_extract_dir = os.path.join(temp_extract_dir, f"nested_{nested_zip_name.split('.')[0]}")
            create_directory(nested_extract_dir)
            
            # Extract the nested ZIP
            with zipfile.ZipFile(nested_zip, 'r') as zip_ref:
                zip_ref.extractall(nested_extract_dir)
        
        # Find all JAR files from both the main extraction and nested extractions
        all_jar_files = glob.glob(os.path.join(temp_extract_dir, "**", "*.jar"), recursive=True)
        logger.info(f"Found {len(all_jar_files)} JAR files in {prefix} package")
        
        # Move JAR files to jars directory
        jar_count = 0
        for jar_file in all_jar_files:
            jar_filename = os.path.basename(jar_file)
            dest_path = os.path.join(JARS_DIR, jar_filename)
            
            # If the file already exists, add a prefix and timestamp
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(jar_filename)
                jar_filename = f"{base}_{prefix}_{int(time.time())}{ext}"
                dest_path = os.path.join(JARS_DIR, jar_filename)
            
            # Move the JAR file
            shutil.move(jar_file, dest_path)
            logger.info(f"Moved {prefix} JAR file: {jar_filename}")
            jar_count += 1
        
        logger.info(f"{prefix} JAR extraction complete. Moved {jar_count} JAR files to {JARS_DIR} directory.")
    
    except Exception as e:
        logger.error(f"Error processing ZIP file {zip_filename}: {str(e)}")
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)

def download_msdrg_files():
    """Download MSDRG Grouper and MCE Editor files."""
    try:
        logger.info(f"Connecting to MS-DRG website: {MSDRG_URL}")
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(MSDRG_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the link to java-source.zip
        java_source_link = None
        for link in soup.find_all('a', href=re.compile(JAVA_SOURCE_PATTERN)):
            java_source_link = link['href']
            break
        
        if not java_source_link:
            logger.error(f"Could not find '{JAVA_SOURCE_PATTERN}' link on the MS-DRG page")
            return None
        
        # Download the java source zip file
        full_url = urljoin(MSDRG_URL, java_source_link)
        filename = get_filename_from_url(full_url)
        
        logger.info(f"Found MS-DRG Java source zip: {filename}")
        return download_file(full_url, filename)
    
    except Exception as e:
        logger.error(f"Error downloading MSDRG files: {str(e)}")
        return None

def download_ioce_files():
    """Download IOCE Editor Java files."""
    try:
        logger.info(f"Connecting to IOCE website: {IOCE_URL}")
        session = requests.Session()
        headers = {"User-Agent": USER_AGENT}
        
        # First request to find the java-standalone link
        response = session.get(IOCE_URL, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the link with "java-standalone" text
        java_standalone_link = None
        for link in soup.find_all('a'):
            href = link.get('href', '')
            inner_text = link.get_text()
            if JAVA_STANDALONE_PATTERN in href.lower() \
            or 'Java Standalone' in inner_text:
                java_standalone_link = href
                logger.info(f"Found IOCE standalone Java link: {java_standalone_link}")
                break
        
        if not java_standalone_link:
            logger.error(f"Could not find '{JAVA_STANDALONE_PATTERN}' link on the IOCE page")
            return None
        
        # Follow the link to the license agreement page
        license_url = urljoin(IOCE_URL, java_standalone_link)
        license_response = session.get(license_url, headers=headers)
        license_response.raise_for_status()
        
        license_soup = BeautifulSoup(license_response.content, 'html.parser')
        
        # Find the form with the "agree" button
        form = None
        for form_tag in license_soup.find_all('form'):
            if form_tag.find('input', attrs={'name': 'agree'}):
                form = form_tag
                break
        
        if not form:
            logger.error("Could not find license agreement form")
            return None
        
        # Get the form action URL
        form_action = form.get('action', '')
        if not form_action:
            logger.error("Could not find form action URL")
            return None
        
        form_url = urljoin(license_url, form_action)
        
        # Extract all form data - includes hidden fields
        form_data = {}
        for input_tag in form.find_all('input'):
            name = input_tag.get('name')
            value = input_tag.get('value', '')
            if name:
                form_data[name] = value
        
        # Make sure we have the 'agree' value
        form_data['agree'] = 'Yes'
        
        # Submit the form to download the file
        logger.info("Submitting license agreement form")
        download_response = session.post(form_url, data=form_data, headers=headers, stream=True)
        download_response.raise_for_status()
        
        # Get the filename from Content-Disposition header if available
        content_disposition = download_response.headers.get('Content-Disposition', '')
        filename = ''
        if 'filename=' in content_disposition:
            filename = re.findall('filename=(.+)', content_disposition)[0].strip('"\'')
        
        # If no filename in header, use a default
        if not filename:
            filename = f"ioce_java_standalone_{int(time.time())}.zip"
        
        # Save the file
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        with open(file_path, 'wb') as f, tqdm(
            desc=filename,
            total=int(download_response.headers.get('content-length', 0)),
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in download_response.iter_content(chunk_size=1024):
                if chunk:
                    size = f.write(chunk)
                    bar.update(size)
        
        logger.info(f"Successfully downloaded IOCE file: {filename}")
        return file_path
    
    except Exception as e:
        logger.error(f"Error downloading IOCE files: {str(e)}")
        return None

def extract_jar_files():
    """Extract JAR files from downloaded ZIP files and move them to jars directory."""
    try:
        # Create jars directory
        create_directory(JARS_DIR)
        
        # Get list of all ZIP files in the download directory
        zip_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.zip"))
        logger.info(f"Found {len(zip_files)} ZIP files to process")
        
        for zip_file in zip_files:
            # Skip the MSDRG and IOCE files as they are processed separately
            zip_filename = os.path.basename(zip_file)
            if JAVA_SOURCE_PATTERN in zip_filename or JAVA_STANDALONE_PATTERN in zip_filename:
                continue
            
            process_zip_for_jars(zip_file, "pricer")
        
        logger.info("JAR extraction from pricer ZIPs complete")
    except Exception as e:
        logger.error(f"An error occurred during JAR extraction: {str(e)}")

if __name__ == "__main__":
    # If jars dir already exists delete it and create a new one
    if not os.path.exists(JARS_DIR):
        os.makedirs(JARS_DIR)
    else:
        shutil.rmtree(JARS_DIR)
        os.makedirs(JARS_DIR)
        
    try:
        logger.info("Starting CMS Software download process")
        # Create directories
        create_directory(DOWNLOAD_DIR)
        create_directory(JARS_DIR)
        
        # Download and process MSDRG files
        logger.info("Starting MSDRG file download process")
        msdrg_zip_path = download_msdrg_files()
        if msdrg_zip_path:
            logger.info("Processing MSDRG ZIP file")
            process_zip_for_jars(msdrg_zip_path, "msdrg")

        # Download and process IOCE files
        logger.info("Starting IOCE file download process")
        ioce_zip_path = download_ioce_files()
        if ioce_zip_path:
            logger.info("Processing IOCE ZIP file")
            process_zip_for_jars(ioce_zip_path, "ioce")
        
        # Process the GFC JAR file
        process_gfc_jar()
        # Process the GRPC JAR file
        process_grpc_jar()

        #process slf4j jar file
        process_sl4j_jar()

        shutil.rmtree(DOWNLOAD_DIR)
    except Exception as e:
        logger.error(f"An unhandled error occurred: {str(e)}")
        if os.path.exists(DOWNLOAD_DIR):
            shutil.rmtree(DOWNLOAD_DIR)