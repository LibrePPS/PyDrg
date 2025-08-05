#!/usr/bin/env python3
"""
CMS Downloader Module

This module provides the CMSDownloader class for downloading and organizing CMS software 
for the CMS MSDRG Grouper and MCE Editor software, including the necessary dependencies like GFC, GRPC, and SLF4J.

Usage Example:
    # Basic usage - downloads all JARs to default directories
    downloader = CMSDownloader()
    success = downloader.build_jar_environment()
    
    # Custom directories
    downloader = CMSDownloader(
        jars_dir="/path/to/custom/jars",
        download_dir="/path/to/custom/downloads"
    )
    success = downloader.build_jar_environment(clean_existing=True)
    
    # Individual components
    downloader = CMSDownloader()
    downloader.download_web_pricers()  # Pricers go to jars/pricers/
    downloader.download_msdrg_files()
    downloader.process_gfc_jar()
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


class CMSDownloader:
    """
    A class to download and manage CMS software JAR files and dependencies.
    """
    
    # Constants
    CMS_URL = "https://www.cms.gov/pricersourcecodesoftware"
    TARGET_HEADER = "Software (Executable JAR Files)"
    ZIP_PATH_PATTERN = "/files/zip/"
    MSDRG_URL = "https://www.cms.gov/medicare/payment/prospective-payment-systems/acute-inpatient-pps/ms-drg-classifications-and-software"
    IOCE_URL = "https://www.cms.gov/medicare/coding-billing/outpatient-code-editor-oce/quarterly-release-files"
    JAVA_SOURCE_PATTERN = "java-source.zip"
    JAVA_STANDALONE_PATTERN = "java-standalone"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    GFC_JAR = "https://github.com/3mcloud/GFC-Grouper-Foundation-Classes/releases/download/v3.4.9/gfc-base-api-3.4.9.jar"
    GRPC_JAR1 = "https://repo1.maven.org/maven2/com/google/protobuf/protobuf-java/3.22.2/protobuf-java-3.22.2.jar"
    GRPC_JAR2 = "https://repo1.maven.org/maven2/com/google/protobuf/protobuf-java/3.21.7/protobuf-java-3.21.7.jar"
    SLF4J_JAR = "https://repo1.maven.org/maven2/org/slf4j/slf4j-simple/2.0.9/slf4j-simple-2.0.9.jar"
    SLF4J_JAR2 = "https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.9/slf4j-api-2.0.9.jar"

    def __init__(self, jars_dir="jars", download_dir="downloads", log_level=logging.INFO):
        """
        Initialize the CMS Downloader.
        
        Args:
            jars_dir (str): Directory to store JAR files
            download_dir (str): Temporary directory for downloads
            log_level (int): Logging level
        """
        self.jars_dir = jars_dir
        self.download_dir = download_dir
        self.pricers_dir = os.path.join(jars_dir, "pricers")
        
        # Setup logging
        self.logger = self._setup_logging(log_level)
        
    def _setup_logging(self, log_level):
        """Setup logging configuration."""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("cms_downloads.log"),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger("cms_downloader")

    def create_directory(self, directory):
        """Create a directory if it doesn't exist."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            self.logger.info(f"Created directory: {directory}")

    def download_file(self, url, filename, directory=None):
        """Download a file with progress bar."""
        if directory is None:
            directory = self.download_dir
            
        try:
            headers = {"User-Agent": self.USER_AGENT}
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
                        
            self.logger.info(f"Successfully downloaded: {filename}")
            return file_path
        except Exception as e:
            self.logger.error(f"Error downloading {url}: {str(e)}")
            return None

    def get_filename_from_url(self, url):
        """Extract filename from URL."""
        return url.split('/')[-1]

    def download_slf4j_jar(self):
        """Download SLF4J JAR files."""
        try:
            self.logger.info(f"Downloading SLF4J JAR file from: {self.SLF4J_JAR} and {self.SLF4J_JAR2}")
            path_1 = self.download_file(self.SLF4J_JAR, "slf4j-simple-2.0.9.jar")
            path_2 = self.download_file(self.SLF4J_JAR2, "slf4j-api-2.0.9.jar")
            return [path_1, path_2]
        except Exception as e:
            self.logger.error(f"Error downloading SLF4J JAR file: {str(e)}")
            return None

    def process_slf4j_jar(self):
        """Process the SLF4J JAR file."""
        try:
            slf4j_jar_paths = self.download_slf4j_jar()
            if not slf4j_jar_paths:
                self.logger.error("SLF4J JAR file not found")
                return
            
            # Move the JAR file to the jars directory
            for path in slf4j_jar_paths:
                if path:
                    dest_path = os.path.join(self.jars_dir, os.path.basename(path))
                    shutil.move(path, dest_path)
                    self.logger.info(f"Moved SLF4J JAR file to jars directory: {os.path.basename(path)}")
        except Exception as e:
            self.logger.error(f"Error processing SLF4J JAR file: {str(e)}")
    
    def download_gfc_jar(self):
        """Download the GFC Base API JAR file."""
        try:
            self.logger.info(f"Downloading GFC Base API JAR file from: {self.GFC_JAR}")
            return self.download_file(self.GFC_JAR, "gfc-base-api-3.4.9.jar")
        except Exception as e:
            self.logger.error(f"Error downloading GFC Base API JAR file: {str(e)}")
            return None
           
    def download_grpc_jar(self):
        """Download GRPC JAR files."""
        try:
            self.logger.info(f"Downloading GRPC JAR file from: {self.GRPC_JAR1} and {self.GRPC_JAR2}")
            path_1 = self.download_file(self.GRPC_JAR1, "protobuf-java-3.22.2.jar")
            path_2 = self.download_file(self.GRPC_JAR2, "protobuf-java-3.21.7.jar")
            return [path_1, path_2]
        except Exception as e:
            self.logger.error(f"Error downloading GRPC JAR file: {str(e)}")
            return None
    
    def process_gfc_jar(self):
        """Process the GFC Base API JAR file."""
        try:
            gfc_jar_path = self.download_gfc_jar()
            if not gfc_jar_path:
                self.logger.error("GFC JAR file not found")
                return
            
            # Move the JAR file to the jars directory
            dest_path = os.path.join(self.jars_dir, "gfc-base-api-3.4.9.jar")
            shutil.move(gfc_jar_path, dest_path)
            self.logger.info("Moved GFC JAR file to jars directory")
        except Exception as e:
            self.logger.error(f"Error processing GFC JAR file: {str(e)}")

    def process_grpc_jar(self):
        """Process the GRPC JAR file."""
        try:
            grpc_jar_paths = self.download_grpc_jar()
            if not grpc_jar_paths:
                self.logger.error("GRPC JAR file not found")
                return
            
            # Move the JAR file to the jars directory
            for path in grpc_jar_paths:
                if path:
                    dest_path = os.path.join(self.jars_dir, os.path.basename(path))
                    shutil.move(path, dest_path)
                    self.logger.info(f"Moved GRPC JAR file to jars directory: {os.path.basename(path)}")
        except Exception as e:
            self.logger.error(f"Error processing GRPC JAR file: {str(e)}")

    def process_zip_for_jars(self, zip_path, prefix="", dest_dir=None):
        """Process a ZIP file to extract JAR files with an optional prefix."""
        if dest_dir is None:
            dest_dir = self.jars_dir
            
        if not zip_path or not os.path.exists(zip_path):
            self.logger.error(f"ZIP file not found: {zip_path}")
            return
        self.create_directory(dest_dir)
        
        zip_filename = os.path.basename(zip_path)
        self.logger.info(f"Processing ZIP file: {zip_filename}")
        
        # Create a temporary directory for extraction
        temp_extract_dir = os.path.join(self.download_dir, f"temp_extract_{int(time.time())}")
        self.create_directory(temp_extract_dir)
        
        try:
            # Extract the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)
            
            # Find any nested ZIP files
            nested_zips = glob.glob(os.path.join(temp_extract_dir, "**", "*.zip"), recursive=True)
            self.logger.info(f"Found {len(nested_zips)} nested ZIP files in package")
            
            # Process each nested ZIP
            for nested_zip in nested_zips:
                nested_zip_name = os.path.basename(nested_zip)
                self.logger.info(f"Extracting nested ZIP: {nested_zip_name}")
                
                # Create a subdirectory for this nested ZIP
                nested_extract_dir = os.path.join(temp_extract_dir, f"nested_{nested_zip_name.split('.')[0]}")
                self.create_directory(nested_extract_dir)
                
                # Extract the nested ZIP
                with zipfile.ZipFile(nested_zip, 'r') as zip_ref:
                    zip_ref.extractall(nested_extract_dir)
            
            # Find all JAR files from both the main extraction and nested extractions
            all_jar_files = glob.glob(os.path.join(temp_extract_dir, "**", "*.jar"), recursive=True)
            self.logger.info(f"Found {len(all_jar_files)} JAR files in {prefix} package")
            
            # Move JAR files to jars directory
            jar_count = 0
            for jar_file in all_jar_files:
                jar_filename = os.path.basename(jar_file)
                dest_path = os.path.join(dest_dir, jar_filename)

                # If the file already exists, add a prefix and timestamp
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(jar_filename)
                    jar_filename = f"{base}_{prefix}_{int(time.time())}{ext}"
                    dest_path = os.path.join(dest_dir, jar_filename)
                
                # Move the JAR file
                shutil.move(jar_file, dest_path)
                self.logger.info(f"Moved {prefix} JAR file: {jar_filename}")
                jar_count += 1
            
            self.logger.info(f"{prefix} JAR extraction complete. Moved {jar_count} JAR files to {dest_dir} directory.")
        
        except Exception as e:
            self.logger.error(f"Error processing ZIP file {zip_filename}: {str(e)}")
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_extract_dir):
                shutil.rmtree(temp_extract_dir)

    def download_msdrg_files(self):
        """Download MS-DRG Java source files from the MS-DRG website."""
        try:
            self.logger.info(f"Connecting to MS-DRG website: {self.MSDRG_URL}")
            headers = {"User-Agent": self.USER_AGENT}
            response = requests.get(self.MSDRG_URL, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the link to java-source.zip
            java_source_link = None
            for link in soup.find_all('a', href=re.compile(self.JAVA_SOURCE_PATTERN)):
                java_source_link = link['href']
                break
            
            if not java_source_link:
                self.logger.error(f"Could not find '{self.JAVA_SOURCE_PATTERN}' link on the MS-DRG page")
                return None
            
            # Download the java source zip file
            full_url = urljoin(self.MSDRG_URL, java_source_link)
            filename = self.get_filename_from_url(full_url)
            
            self.logger.info(f"Found MS-DRG Java source zip: {filename}")
            return self.download_file(full_url, filename)
        
        except Exception as e:
            self.logger.error(f"Error downloading MSDRG files: {str(e)}")
            return None

    def download_ioce_files(self):
        """Download IOCE Editor Java files."""
        try:
            self.logger.info(f"Connecting to IOCE website: {self.IOCE_URL}")
            session = requests.Session()
            headers = {"User-Agent": self.USER_AGENT}
            
            # First request to find the java-standalone link
            response = session.get(self.IOCE_URL, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the link with "java-standalone" text
            java_standalone_link = None
            for link in soup.find_all('a'):
                href = link.get('href', '')
                inner_text = link.get_text()
                if self.JAVA_STANDALONE_PATTERN in href.lower() \
                or 'Java Standalone' in inner_text:
                    java_standalone_link = href
                    self.logger.info(f"Found IOCE standalone Java link: {java_standalone_link}")
                    break
            
            if not java_standalone_link:
                self.logger.error(f"Could not find '{self.JAVA_STANDALONE_PATTERN}' link on the IOCE page")
                return None
            
            # Follow the link to the license agreement page
            license_url = urljoin(self.IOCE_URL, java_standalone_link)
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
                self.logger.error("Could not find license agreement form")
                return None
            
            # Get the form action URL
            form_action = form.get('action', '')
            if not form_action:
                self.logger.error("Could not find form action URL")
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
            self.logger.info("Submitting license agreement form")
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
            file_path = os.path.join(self.download_dir, filename)
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
            
            self.logger.info(f"Successfully downloaded IOCE file: {filename}")
            return file_path
        
        except Exception as e:
            self.logger.error(f"Error downloading IOCE files: {str(e)}")
            return None

    def extract_jar_files(self, dest_dir=None):
        """Extract JAR files from downloaded ZIP files and move them to jars directory."""
        if dest_dir is None:
            dest_dir = self.jars_dir
            
        try:
            # Create jars directory
            self.create_directory(dest_dir)
            
            # Get list of all ZIP files in the download directory
            zip_files = glob.glob(os.path.join(self.download_dir, "*.zip"))
            self.logger.info(f"Found {len(zip_files)} ZIP files to process")
            
            for zip_file in zip_files:
                # Skip the MSDRG and IOCE files as they are processed separately
                zip_filename = os.path.basename(zip_file)
                if self.JAVA_SOURCE_PATTERN in zip_filename or self.JAVA_STANDALONE_PATTERN in zip_filename:
                    continue
                
                self.process_zip_for_jars(zip_file, "pricer", dest_dir)
            
            self.logger.info("JAR extraction from pricer ZIPs complete")
        except Exception as e:
            self.logger.error(f"An error occurred during JAR extraction: {str(e)}")

    def download_web_pricers(self, download_dir=None):
        """Main function to scrape the CMS website and download files."""
        if download_dir is None:
            download_dir = self.download_dir
            
        try:
            headers = {"User-Agent": self.USER_AGENT}
            response = requests.get(self.CMS_URL, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the target header
            target_section = None
            for h2 in soup.find_all('h2'):
                if self.TARGET_HEADER in h2.text:
                    target_section = h2
                    break
            
            if not target_section:
                self.logger.error(f"Could not find section with header: {self.TARGET_HEADER}")
                return
                
            # Look at content following the header until we hit another h2 or reach the end
            download_links = []
            current = target_section.next_sibling
            
            while current and (not current.name or current.name != 'h2'):
                if current.name == 'a' and self.ZIP_PATH_PATTERN in current.get('href', ''):
                    download_links.append(current['href'])
                elif hasattr(current, 'find_all'):
                    for link in current.find_all('a', href=re.compile(self.ZIP_PATH_PATTERN)):
                        download_links.append(link['href'])
                current = current.next_sibling
            
            if not download_links:
                self.logger.warning("No download links found matching the criteria")
                return
                
            self.logger.info(f"Found {len(download_links)} files to download")
            
            # Create pricers subdirectory as requested by user
            pricers_dir = os.path.join(self.jars_dir, "pricers")
            self.create_directory(pricers_dir)
            
            # Download each file
            success_count = 0
            for link in download_links:
                full_url = urljoin(self.CMS_URL, link)
                filename = self.get_filename_from_url(full_url)
                
                self.logger.info(f"Downloading: {filename} from {full_url}")
                if self.download_file(full_url, filename):
                    success_count += 1
                    # Add a small delay between downloads to be nice to the server
                    time.sleep(1)
            
            self.logger.info(f"Download complete. Successfully downloaded {success_count} of {len(download_links)} files.")
            self.extract_jar_files(dest_dir=pricers_dir)

        except Exception as e:
            self.logger.error(f"An error occurred: {str(e)}")

    def build_jar_environment(self, clean_existing=True):
        """Main method to build the complete JAR environment needed for processing."""
        try:
            # If jars dir already exists delete it and create a new one
            if clean_existing:
                if os.path.exists(self.jars_dir):
                    shutil.rmtree(self.jars_dir)
                os.makedirs(self.jars_dir, exist_ok=True)
            else:
                self.create_directory(self.jars_dir)
                
            self.logger.info("Starting CMS Software download process")
            # Create directories
            self.create_directory(self.download_dir)
            self.create_directory(self.jars_dir)
            
            # Download and process MSDRG files
            self.logger.info("Starting MSDRG file download process")
            msdrg_zip_path = self.download_msdrg_files()
            if msdrg_zip_path:
                self.logger.info("Processing MSDRG ZIP file")
                self.process_zip_for_jars(msdrg_zip_path, "msdrg")

            # Download and process IOCE files
            self.logger.info("Starting IOCE file download process")
            ioce_zip_path = self.download_ioce_files()
            if ioce_zip_path:
                self.logger.info("Processing IOCE ZIP file")
                self.process_zip_for_jars(ioce_zip_path, "ioce")
            
            # Process the GFC JAR file
            self.process_gfc_jar()
            # Process the GRPC JAR file
            self.process_grpc_jar()

            # Process slf4j jar file
            self.process_slf4j_jar()

            # Get CMS Web Pricers - these go in their own subdirectory
            self.logger.info("Starting CMS Web Pricers download process")
            self.download_web_pricers()

            # Clean up download directory
            if os.path.exists(self.download_dir):
                shutil.rmtree(self.download_dir)

            # Remove sources jar files
            sources_jar_files = glob.glob(os.path.join(self.jars_dir, "*sources*.jar"))
            for jar_file in sources_jar_files:
                os.remove(jar_file)
                self.logger.info(f"Removed sources JAR file: {jar_file}")
                
            self.logger.info("JAR environment build complete!")
            return True
            
        except Exception as e:
            self.logger.error(f"An unhandled error occurred: {str(e)}")
            if os.path.exists(self.download_dir):
                shutil.rmtree(self.download_dir)
            return False

if __name__ == "__main__":
    # Create downloader instance and build the JAR environment
    downloader = CMSDownloader()
    success = downloader.build_jar_environment(clean_existing=True)
    
    if success:
        print("JAR environment build completed successfully!")
    else:
        print("JAR environment build failed. Check logs for details.")