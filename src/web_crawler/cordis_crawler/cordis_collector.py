"""
CORDIS XML Collector
====================

Main orchestrator module that combines search, matching, and XML download functionality
to provide a complete CORDIS project data collection pipeline.

This module serves as the primary interface for:
- Automated CORDIS project search and discovery
- Intelligent project matching using fuzzy algorithms  
- Batch XML download with validation and error handling
- Statistical reporting and progress tracking

Example:
    Basic usage for collecting project XML files:
    
    >>> collector = CordisXMLCollector(output_dir="./xml_data")
    >>> results = collector.collect_xml(["COMMUTE", "HORIZON"])
    >>> print(f"Downloaded {len(results)} XML files")

Author: SCAI Web Crawler Team
Date: 2024
"""

import logging
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any, Union
from pathlib import Path

# Handle both package and standalone imports
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .project_matcher import ProjectMatcher
    from .xml_downloader import CordisXMLDownloader
except ImportError:
    # For standalone testing and direct execution
    from project_matcher import ProjectMatcher
    from xml_downloader import CordisXMLDownloader

# Configure logging
logger = logging.getLogger(__name__)


class CordisXMLCollector:
    """
    Main orchestrator class for CORDIS project XML collection and processing.
    
    This class coordinates the entire workflow from project name input to XML file output,
    including search, matching, download, and validation phases. It provides comprehensive
    error handling, statistics tracking, and batch processing capabilities.
    
    Attributes:
        interactive (bool): Enable interactive disambiguation prompts
        matcher (ProjectMatcher): Fuzzy matching engine for project identification
        downloader (CordisXMLDownloader): XML download and validation handler
        output_dir (Path): Directory where XML files are saved
        stats (Dict[str, int]): Collection statistics and metrics
        
    Example:
        >>> # Basic collection with default settings
        >>> collector = CordisXMLCollector()
        >>> xml_files = collector.collect_xml(["COMMUTE"])
        
        >>> # Batch processing with custom output directory
        >>> collector = CordisXMLCollector(output_dir="./cordis_data")
        >>> results = collector.collect_and_save_batch(["PROJECT1", "PROJECT2"])
    """
    
    def __init__(self, 
                 output_dir: Optional[Union[str, Path]] = None, 
                 interactive: bool = True,
                 debug: bool = False) -> None:
        """
        Initialize the CORDIS XML collector with configuration options.
        
        Args:
            output_dir: Target directory for XML file storage. Creates temp dir if None.
            interactive: Enable user prompts for project disambiguation.
            debug: Enable detailed debug logging for troubleshooting.
            
        Raises:
            OSError: If output directory cannot be created or accessed.
            ImportError: If required dependencies are not available.
            
        Example:
            >>> collector = CordisXMLCollector(
            ...     output_dir="./my_xml_data", 
            ...     interactive=False,
            ...     debug=True
            ... )
        """
        # Configure logging level
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        
        logger.info(f"Initializing CordisXMLCollector with output_dir='{output_dir}'")
        
        self.interactive = interactive
        self.debug = debug
        self.start_time = datetime.now()
        
        # Initialize core components
        try:
            self.matcher = ProjectMatcher()
            self.downloader = CordisXMLDownloader(output_dir)
            self.output_dir = self.downloader.output_dir
            
            logger.info(f"Collector initialized successfully. Output directory: {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Failed to initialize collector components: {e}")
            raise
        
        # Initialize statistics tracking
        self.stats: Dict[str, int] = {
            'projects_requested': 0,
            'projects_found': 0,
            'projects_downloaded': 0,
            'projects_failed': 0,
            'search_failures': 0,
            'download_failures': 0,
            'validation_failures': 0,
            'total_execution_time_seconds': 0
        }
        
    def collect_project_xml(self, project_name: str) -> Optional[Dict]:
        """
        Collect XML for a single project by name.
        
        Args:
            project_name: Project name, acronym, or ID to search for
            
        Returns:
            Dictionary with project info and XML file path, or None if failed
        """
        self.stats['projects_requested'] += 1
        
        print(f"\n{'='*60}")
        print(f"Collecting XML for: {project_name}")
        print('='*60)
        
        # Step 1: Find the project
        print("Step 1: Searching for project...")
        project = self.matcher.find_best_project(project_name, interactive=self.interactive)
        
        if not project:
            print(f"✗ Could not find project: {project_name}")
            self.stats['search_failures'] += 1
            return None
            
        self.stats['projects_found'] += 1
        print(f"✓ Found project: {project['title'][:50]}... (ID: {project['id']})")
        
        # Step 2: Download XML
        print("Step 2: Downloading XML...")
        xml_path = self.downloader.download_project_xml(project['id'])
        
        if not xml_path:
            print(f"✗ Failed to download XML for project {project['id']}")
            self.stats['download_failures'] += 1
            self.stats['projects_failed'] += 1
            return None
            
        self.stats['projects_downloaded'] += 1
        
        # Step 3: Extract metadata
        print("Step 3: Extracting metadata...")
        metadata = self.downloader.get_xml_metadata(xml_path)
        
        # Combine all information
        result = {
            'search_query': project_name,
            'project_id': project['id'],
            'project_url': project['url'],
            'match_score': project.get('match_score', 0),
            'xml_file_path': xml_path,
            'xml_file_size': os.path.getsize(xml_path),
            'metadata': metadata
        }
        
        print(f"✓ Successfully collected XML for {project['title'][:30]}...")
        print(f"  File: {xml_path}")
        print(f"  Size: {result['xml_file_size']:,} bytes")
        
        return result
        
    def collect_multiple_projects(self, project_names: List[str], 
                                 delay: float = 1.0) -> List[Dict]:
        """
        Collect XML for multiple projects.
        
        Args:
            project_names: List of project names/IDs to collect
            delay: Delay between downloads in seconds
            
        Returns:
            List of successful collection results
        """
        print(f"\n{'='*80}")
        print(f"BATCH COLLECTION: {len(project_names)} projects")
        print('='*80)
        
        results = []
        
        for i, project_name in enumerate(project_names, 1):
            print(f"\n[{i}/{len(project_names)}] Processing: {project_name}")
            print("-" * 60)
            
            result = self.collect_project_xml(project_name)
            if result:
                results.append(result)
                
            # Rate limiting between projects
            if i < len(project_names) and delay > 0:
                import time
                print(f"Waiting {delay} seconds before next project...")
                time.sleep(delay)
                
        self._print_summary()
        return results
        
    def collect_and_save_batch(self, project_names: List[str], 
                              batch_name: Optional[str] = None,
                              delay: float = 1.0) -> Tuple[List[str], str]:
        """
        Collect XML for multiple projects and save metadata.
        
        Args:
            project_names: List of project names/IDs to collect
            batch_name: Optional name for the batch
            delay: Delay between downloads in seconds
            
        Returns:
            Tuple of (list of XML file paths, metadata file path)
        """
        if not batch_name:
            from datetime import datetime
            batch_name = f"cordis_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        print(f"Batch name: {batch_name}")
        
        # Collect projects
        results = self.collect_multiple_projects(project_names, delay)
        
        if not results:
            print("No projects were successfully collected!")
            return [], ""
            
        # Save batch metadata
        metadata_file = self.output_dir / f"{batch_name}_metadata.json"
        self._save_batch_metadata(results, metadata_file, batch_name)
        
        # Return list of XML files
        xml_files = [result['xml_file_path'] for result in results]
        
        print(f"\n✓ Batch complete:")
        print(f"  XML files: {len(xml_files)}")
        print(f"  Metadata: {metadata_file}")
        
        return xml_files, str(metadata_file)
        
    def _save_batch_metadata(self, results: List[Dict], 
                           metadata_file: Path, batch_name: str):
        """Save batch collection metadata to JSON file."""
        import json
        from datetime import datetime
        
        batch_metadata = {
            'batch_name': batch_name,
            'collection_date': datetime.now().isoformat(),
            'output_directory': str(self.output_dir),
            'statistics': self.stats.copy(),
            'projects': []
        }
        
        for result in results:
            project_info = {
                'search_query': result['search_query'],
                'project_id': result['project_id'],
                'project_title': result['metadata'].get('title', 'Unknown'),
                'project_acronym': result['metadata'].get('acronym', ''),
                'match_score': result['match_score'],
                'xml_file_path': result['xml_file_path'],
                'xml_file_size': result['xml_file_size'],
                'project_url': result['project_url']
            }
            batch_metadata['projects'].append(project_info)
            
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(batch_metadata, f, indent=2, ensure_ascii=False)
            
        print(f"✓ Saved batch metadata: {metadata_file}")
        
    def _print_summary(self):
        """Print collection statistics."""
        print(f"\n{'='*60}")
        print("COLLECTION SUMMARY")
        print('='*60)
        print(f"Projects requested: {self.stats['projects_requested']}")
        print(f"Projects found:     {self.stats['projects_found']}")
        print(f"Projects downloaded: {self.stats['projects_downloaded']}")
        print(f"Projects failed:    {self.stats['projects_failed']}")
        print(f"Search failures:    {self.stats['search_failures']}")
        print(f"Download failures:  {self.stats['download_failures']}")
        
        if self.stats['projects_requested'] > 0:
            success_rate = (self.stats['projects_downloaded'] / 
                          self.stats['projects_requested'] * 100)
            print(f"Success rate:       {success_rate:.1f}%")
            
        print(f"Output directory:   {self.output_dir}")
        print('='*60)


def test_xml_collector():
    """Test the CORDIS XML collector."""
    print("=== Testing CORDIS XML Collector ===")
    
    # Create collector with temp directory
    temp_dir = tempfile.mkdtemp(prefix="cordis_collector_")
    collector = CordisXMLCollector(temp_dir, interactive=False)
    
    print(f"Using output directory: {temp_dir}")
    
    # Test single project collection
    print("\n--- Testing single project ---")
    result = collector.collect_project_xml("COMMUTE")
    
    if result:
        print("✓ Single project collection successful")
        print(f"  Project: {result['metadata'].get('title', 'Unknown')}")
        print(f"  File: {result['xml_file_path']}")
    else:
        print("✗ Single project collection failed")
        
    # Test batch collection  
    print("\n--- Testing batch collection ---")
    test_projects = [
        "COMORBIDITY MECHANISMS UTILIZED IN HEALTHCARE",
        "CoCA",  # Try acronym
        "artificial intelligence"  # General search
    ]
    
    xml_files, metadata_file = collector.collect_and_save_batch(
        test_projects, 
        "test_batch",
        delay=0.5
    )
    
    print(f"\nBatch test results:")
    print(f"  XML files collected: {len(xml_files)}")
    print(f"  Metadata file: {metadata_file}")
    
    # List collected files
    if xml_files:
        print("  Collected files:")
        for xml_file in xml_files:
            size = os.path.getsize(xml_file)
            print(f"    {os.path.basename(xml_file)} ({size:,} bytes)")


if __name__ == "__main__":
    test_xml_collector()