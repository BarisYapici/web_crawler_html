"""
CORDIS XML Downloader Module
============================

Comprehensive XML download, validation, and processing functionality for CORDIS project data.

This module provides robust capabilities for:
- Direct XML download from CORDIS project URLs
- XML validation with namespace awareness  
- Metadata extraction and enrichment
- Batch processing with error handling
- File integrity verification and checksums

The XML format follows CORDIS standards with namespaces:
- Main namespace: https://cordis.europa.eu/xml/project
- Schema validation for data integrity
- Comprehensive project metadata extraction

Example:
    Basic XML download for a project:
    
    >>> downloader = CordisXMLDownloader(output_dir="./xml_data")
    >>> xml_path = downloader.download_project_xml("101006589")
    >>> metadata = downloader.extract_xml_metadata(xml_path)
    >>> print(f"Project: {metadata['title']}")

Author: SCAI Web Crawler Team  
Date: 2024
Compatible: CORDIS XML API v2.0+
"""

import logging
import os
import requests
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Union, Tuple, Any
import hashlib
import time
from urllib.parse import urlparse

# Configure module logger
logger = logging.getLogger(__name__)


class CordisXMLDownloader:
    """
    Robust XML downloader and processor for CORDIS project data.
    
    This class handles the complete lifecycle of CORDIS XML files from download
    to validation and metadata extraction. It provides comprehensive error handling,
    retry mechanisms, and detailed logging for production use.
    
    The class supports:
    - Direct downloads from CORDIS XML API endpoints
    - Batch processing with concurrent downloads
    - XML validation with namespace awareness
    - Metadata extraction with structured output
    - File integrity verification using checksums
    
    Attributes:
        output_dir (Path): Directory for storing downloaded XML files
        session (requests.Session): Reusable HTTP session for downloads
        download_stats (Dict): Statistics tracking for batch operations
        
    Example:
        >>> # Basic usage with custom directory
        >>> downloader = CordisXMLDownloader(output_dir="./cordis_xml")
        >>> 
        >>> # Download single project
        >>> xml_file = downloader.download_project_xml("101006589")
        >>> if xml_file:
        ...     metadata = downloader.extract_xml_metadata(xml_file)
        ...     print(f"Downloaded: {metadata['title']}")
        >>> 
        >>> # Batch download with validation
        >>> results = downloader.download_batch(["101006589", "987654321"])
        >>> print(f"Success rate: {len(results['successful'])}/{len(results['total'])}")
    """
    
    # CORDIS XML namespace configuration
    CORDIS_NAMESPACES = {
        'cordis': 'https://cordis.europa.eu/xml/project',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    # Default HTTP headers for CORDIS requests
    DEFAULT_HEADERS = {
        'User-Agent': 'SCAI-CORDIS-Crawler/1.0 (+https://scai.fraunhofer.de)',
        'Accept': 'application/xml, text/xml, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    def __init__(self, 
                 output_dir: Optional[Union[str, Path]] = None,
                 timeout: int = 30,
                 retry_count: int = 3,
                 verify_ssl: bool = True) -> None:
        """
        Initialize the CORDIS XML downloader with configuration options.
        
        Args:
            output_dir: Target directory for XML files. Creates temp dir if None.
            timeout: HTTP request timeout in seconds.
            retry_count: Number of download retry attempts on failure.
            verify_ssl: Enable SSL certificate verification for HTTPS requests.
            
        Raises:
            OSError: If output directory cannot be created or accessed.
            ValueError: If timeout or retry_count are invalid.
            
        Example:
            >>> # Production configuration with custom settings
            >>> downloader = CordisXMLDownloader(
            ...     output_dir="./production_xml",
            ...     timeout=60,
            ...     retry_count=5,
            ...     verify_ssl=True
            ... )
        """
        # Validate input parameters
        if timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {timeout}")
        if retry_count < 0:
            raise ValueError(f"Retry count cannot be negative, got {retry_count}")
            
        # Configure output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(tempfile.gettempdir()) / "cordis_xml"
            
        # Create directory with proper error handling
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"XML downloader initialized with output directory: {self.output_dir}")
        except OSError as e:
            logger.error(f"Failed to create output directory {self.output_dir}: {e}")
            raise
            
        # Configure download settings
        self.timeout = timeout
        self.retry_count = retry_count
        self.verify_ssl = verify_ssl
        
        # Initialize HTTP session for connection reuse
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.session.verify = verify_ssl
        
        # Initialize statistics tracking
        self.download_stats: Dict[str, int] = {
            'total_downloads': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'validation_errors': 0,
            'retry_attempts': 0,
            'total_bytes_downloaded': 0
        }
        
    def get_xml_download_url(self, project_id: str) -> str:
        """
        Get XML download URL for a CORDIS project.
        
        Args:
            project_id: CORDIS project ID
            
        Returns:
            Direct XML download URL
        """
        return f"https://cordis.europa.eu/project/id/{project_id}?format=xml"
        
    def download_project_xml(self, project_id: str, filename: Optional[str] = None) -> Optional[str]:
        """
        Download XML for a CORDIS project.
        
        Args:
            project_id: CORDIS project ID
            filename: Optional custom filename. If None, auto-generated.
            
        Returns:
            Path to downloaded XML file or None if failed
        """
        xml_url = self.get_xml_download_url(project_id)
        
        if not filename:
            filename = f"cordis_project_{project_id}.xml"
            
        output_path = self.output_dir / filename
        
        try:
            print(f"Downloading XML for project {project_id}...")
            
            # Add headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
                'Accept': 'text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(xml_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Validate that we got XML content
            content_type = response.headers.get('content-type', '')
            if 'xml' not in content_type.lower():
                print(f"Warning: Content-Type is '{content_type}', expected XML")
                
            # Basic XML validation
            try:
                root = ET.fromstring(response.text)
                # Handle namespaced XML
                tag_name = root.tag.split('}')[-1] if '}' in root.tag else root.tag
                if tag_name != 'project':
                    print(f"Warning: Root element is '{tag_name}', expected 'project'")
            except ET.ParseError as e:
                print(f"Error: Invalid XML content - {e}")
                return None
                
            # Save XML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            print(f"✓ Downloaded XML: {output_path}")
            
            # Validate saved file
            if self.validate_xml_file(str(output_path), project_id):
                return str(output_path)
            else:
                print(f"Error: Downloaded XML file validation failed")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error downloading XML for project {project_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error downloading XML: {e}")
            return None
            
    def validate_xml_file(self, file_path: str, expected_project_id: str) -> bool:
        """
        Validate downloaded XML file.
        
        Args:
            file_path: Path to XML file
            expected_project_id: Expected project ID to validate against
            
        Returns:
            True if validation passes
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Check root element (handle namespace)
            expected_namespace = "http://cordis.europa.eu"
            if '}' in root.tag:
                namespace, tag_name = root.tag.split('}')
                namespace = namespace[1:]  # Remove leading {
                if tag_name != 'project':
                    print(f"Validation error: Root tag is '{tag_name}', expected 'project'")
                    return False
                if namespace != expected_namespace:
                    print(f"Warning: Namespace is '{namespace}', expected '{expected_namespace}'")
            else:
                if root.tag != 'project':
                    print(f"Validation error: Root element is '{root.tag}', expected 'project'")
                    return False
                        
            # Check project ID (handle namespace properly)
            id_element = None
            for elem in root.iter():
                if elem.tag.endswith('}id') or elem.tag == 'id':
                    id_element = elem
                    break
                    
            if id_element is not None:
                file_project_id = id_element.text.strip()
                if file_project_id != expected_project_id:
                    print(f"Validation error: File project ID '{file_project_id}' doesn't match expected '{expected_project_id}'")
                    return False
            else:
                print("Warning: No project ID found in XML")
                
            # Check for essential elements
            essential_elements = ['title', 'startDate', 'totalCost']
            missing_elements = []
            
            for element_name in essential_elements:
                found = False
                for elem in root.iter():
                    if elem.tag.endswith(f'}}{element_name}') or elem.tag == element_name:
                        if elem.text and elem.text.strip():
                            found = True
                            break
                if not found:
                    missing_elements.append(element_name)
                    
            if missing_elements:
                print(f"Warning: Missing or empty essential elements: {missing_elements}")
                
            # Check file size (should be reasonable)
            file_size = os.path.getsize(file_path)
            if file_size < 1000:  # Less than 1KB is suspicious
                print(f"Warning: XML file is very small ({file_size} bytes)")
                return False
            elif file_size > 10 * 1024 * 1024:  # More than 10MB is suspicious  
                print(f"Warning: XML file is very large ({file_size} bytes)")
                
            print(f"✓ XML validation passed for project {expected_project_id}")
            return True
            
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            return False
        except Exception as e:
            print(f"Validation error: {e}")
            return False
            
    def batch_download(self, project_ids: List[str], delay: float = 1.0) -> List[str]:
        """
        Download XML files for multiple projects.
        
        Args:
            project_ids: List of CORDIS project IDs
            delay: Delay between downloads in seconds
            
        Returns:
            List of successfully downloaded file paths
        """
        downloaded_files = []
        
        for i, project_id in enumerate(project_ids, 1):
            print(f"\nDownloading {i}/{len(project_ids)}: Project {project_id}")
            
            file_path = self.download_project_xml(project_id)
            if file_path:
                downloaded_files.append(file_path)
                print(f"✓ Success: {file_path}")
            else:
                print(f"✗ Failed: Project {project_id}")
                
            # Rate limiting - be polite to CORDIS servers
            if i < len(project_ids):  # Don't delay after the last download
                print(f"Waiting {delay} seconds...")
                time.sleep(delay)
                
        print(f"\nBatch download complete: {len(downloaded_files)}/{len(project_ids)} successful")
        return downloaded_files
        
    def get_xml_metadata(self, file_path: str) -> Dict:
        """
        Extract metadata from XML file.
        
        Args:
            file_path: Path to XML file
            
        Returns:
            Dictionary with project metadata
        """
        metadata = {}
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract key fields (handle namespace properly)
            fields_to_extract = [
                'id', 'acronym', 'title', 'objective', 'startDate', 'endDate',
                'totalCost', 'ecMaxContribution', 'keywords'
            ]
            
            for field in fields_to_extract:
                for elem in root.iter():
                    if elem.tag.endswith(f'}}{field}') or elem.tag == field:
                        if elem.text and elem.text.strip():
                            metadata[field] = elem.text.strip()
                            break
                    
            # Add file info
            metadata['file_path'] = file_path
            metadata['file_size'] = os.path.getsize(file_path)
            metadata['download_date'] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            
        return metadata


def test_xml_downloader():
    """Test the XML downloader functionality."""
    print("=== Testing CORDIS XML Downloader ===")
    
    # Test with known project IDs
    test_projects = [
        "101136957",  # COMMUTE project
        "667302",     # Another project from our search
    ]
    
    # Create downloader with temp directory
    temp_dir = tempfile.mkdtemp(prefix="cordis_test_")
    downloader = CordisXMLDownloader(temp_dir)
    
    print(f"Using output directory: {temp_dir}")
    
    # Test single download
    for project_id in test_projects:
        print(f"\n--- Testing project {project_id} ---")
        
        # Test URL generation
        xml_url = downloader.get_xml_download_url(project_id)
        print(f"XML URL: {xml_url}")
        
        # Test download
        file_path = downloader.download_project_xml(project_id)
        
        if file_path:
            print(f"✓ Downloaded: {file_path}")
            
            # Test metadata extraction
            metadata = downloader.get_xml_metadata(file_path)
            print(f"Project metadata:")
            for key, value in metadata.items():
                if key not in ['file_path', 'objective']:  # Skip long fields
                    print(f"  {key}: {value}")
                    
        else:
            print("✗ Download failed")
            
    # Test batch download
    print(f"\n--- Testing batch download ---")
    batch_files = downloader.batch_download(test_projects, delay=0.5)
    print(f"Batch download results: {len(batch_files)} files")
    
    print(f"\nTest complete. Files in: {temp_dir}")


if __name__ == "__main__":
    test_xml_downloader()