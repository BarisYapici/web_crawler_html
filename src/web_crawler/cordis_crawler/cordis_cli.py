#!/usr/bin/env python3
"""
CORDIS to RAXKG Command Line Interface
======================================

Production-ready CLI for automated CORDIS project data collection and knowledge graph generation.

This command-line interface provides comprehensive functionality for:
- CORDIS project search and XML data collection
- Intelligent project matching with disambiguation  
- RAXKG knowledge graph pipeline integration
- Neo4j database import with validation
- Batch processing with detailed progress reporting

The CLI supports multiple operation modes:
- collect: XML collection only
- build-graph: RAXKG graph generation from existing XML  
- full-pipeline: Complete end-to-end automation
- neo4j-import: Database import with dry-run support

Example Usage:
    # Basic XML collection
    python cordis_cli.py collect "COMMUTE" --output ./xml_data
    
    # Full pipeline with Neo4j import
    python cordis_cli.py full-pipeline "COMMUTE" \\
        --raxkg-path ./COMMUTE-Knowledge-Graph \\
        --neo4j-import --neo4j-password "password"
    
    # Batch processing multiple projects  
    python cordis_cli.py collect "COMMUTE,AI4EU,HORIZON" \\
        --output ./batch_xml --timeout 60

Author: SCAI Web Crawler Team
Version: 1.0.0
Python: 3.8+ required
Dependencies: selenium, fuzzywuzzy, requests, lxml
"""

import argparse
import logging
import sys
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

# Configure path for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import core modules with error handling
try:
    from raxkg_integration import CordisRAXKGIntegration
    from cordis_collector import CordisXMLCollector
except ImportError as e:
    print(f"❌ Error importing required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("  pip install selenium fuzzywuzzy python-levenshtein requests lxml")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORDIS to RAXKG Pipeline - Collect CORDIS project XML and build knowledge graphs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect and build graph for a single project
  python cordis_cli.py --projects "COMMUTE" --version "commute_v1"
  
  # Collect multiple projects
  python cordis_cli.py --projects "COMMUTE" "artificial intelligence" "climate change"
  
  # Just collect XML files without building graph
  python cordis_cli.py --collect-only --projects "COMMUTE" --output-dir ./xml_files
  
  # Build graph and import to Neo4j (dry run)
  python cordis_cli.py --projects "COMMUTE" --neo4j-import --dry-run
  
  # Build graph and import to Neo4j (real import - requires password)
  python cordis_cli.py --projects "COMMUTE" --neo4j-import --neo4j-password "your_password"
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--projects', '-p',
        nargs='+',
        required=True,
        help='Project names, acronyms, or IDs to search for'
    )
    
    # Optional arguments
    parser.add_argument(
        '--version', '-v',
        help='Version name for the graph database (auto-generated if not provided)'
    )
    
    parser.add_argument(
        '--raxkg-path',
        default=r"C:\workspace\SCAI\COMMUTE-Knowledge-Graph",
        help='Path to RAXKG repository (default: C:\\workspace\\SCAI\\COMMUTE-Knowledge-Graph)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for XML files (temp directory if not provided)'
    )
    
    parser.add_argument(
        '--collect-only',
        action='store_true',
        help='Only collect XML files, do not build knowledge graph'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Enable interactive mode for project disambiguation'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Delay between CORDIS requests in seconds (default: 1.0)'
    )
    
    # Neo4j import options
    neo4j_group = parser.add_argument_group('Neo4j Import Options')
    neo4j_group.add_argument(
        '--neo4j-import',
        action='store_true',
        help='Import built graph to Neo4j'
    )
    
    neo4j_group.add_argument(
        '--neo4j-uri',
        default='bolt://localhost:7687',
        help='Neo4j connection URI (default: bolt://localhost:7687)'
    )
    
    neo4j_group.add_argument(
        '--neo4j-user',
        default='neo4j',
        help='Neo4j username (default: neo4j)'
    )
    
    neo4j_group.add_argument(
        '--neo4j-password',
        help='Neo4j password (required for real import)'
    )
    
    neo4j_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run of Neo4j import (show what would be imported)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print banner
    print("=" * 80)
    print("CORDIS to RAXKG Pipeline")
    print("=" * 80)
    print(f"Projects to process: {len(args.projects)}")
    for i, project in enumerate(args.projects, 1):
        print(f"  {i}. {project}")
    print(f"RAXKG path: {args.raxkg_path}")
    if args.version:
        print(f"Version: {args.version}")
    print()
    
    try:
        if args.collect_only:
            # Just collect XML files
            print("🔍 XML Collection Mode")
            collector = CordisXMLCollector(args.output_dir, args.interactive)
            xml_files, metadata_file = collector.collect_and_save_batch(
                args.projects,
                args.version or "cordis_collection",
                delay=args.delay
            )
            
            print(f"\n✅ Collection complete!")
            print(f"📁 XML files: {len(xml_files)}")
            print(f"📄 Metadata: {metadata_file}")
            
            if xml_files:
                print("\nCollected files:")
                for xml_file in xml_files:
                    size = os.path.getsize(xml_file)
                    print(f"  📄 {os.path.basename(xml_file)} ({size:,} bytes)")
                    
        else:
            # Full pipeline: collect + build graph
            print("🚀 Full Pipeline Mode")
            integration = CordisRAXKGIntegration(args.raxkg_path)
            
            graph_db_path, xml_files = integration.collect_and_build_graph(
                args.projects,
                version_name=args.version,
                interactive=args.interactive,
                cleanup_xml=not args.output_dir  # Keep XML if output dir specified
            )
            
            print(f"\n✅ Pipeline complete!")
            print(f"🗄️  Graph database: {graph_db_path}")
            print(f"📁 XML files processed: {len(xml_files)}")
            
            # Neo4j import if requested
            if args.neo4j_import:
                print(f"\n📊 Neo4j Import")
                
                if args.dry_run:
                    print("🔍 Performing dry run...")
                elif not args.neo4j_password:
                    print("⚠️  No password provided, performing dry run instead")
                    args.dry_run = True
                else:
                    print("🚀 Importing to Neo4j...")
                
                success = integration.import_to_neo4j(
                    graph_db_path,
                    neo4j_uri=args.neo4j_uri,
                    user=args.neo4j_user,
                    password=args.neo4j_password,
                    dry_run=args.dry_run
                )
                
                if success:
                    if args.dry_run:
                        print("✅ Dry run completed successfully!")
                    else:
                        print("✅ Neo4j import completed successfully!")
                else:
                    print("❌ Neo4j import failed!")
                    sys.exit(1)
                    
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    print("\n🎉 All operations completed successfully!")


if __name__ == "__main__":
    main()