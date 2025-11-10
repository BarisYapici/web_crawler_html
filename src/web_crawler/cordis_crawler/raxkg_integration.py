"""
RAXKG Integration Module
Connects CORDIS XML collection with the RAXKG graph building pipeline.
"""

import os
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Tuple

try:
    from .cordis_collector import CordisXMLCollector
except ImportError:
    # For standalone testing
    import sys
    sys.path.append(os.path.dirname(__file__))
    from cordis_collector import CordisXMLCollector


class CordisRAXKGIntegration:
    """Integrate CORDIS XML collection with RAXKG graph building."""
    
    def __init__(self, 
                 raxkg_root: Optional[str] = None,
                 schema_path: Optional[str] = None,
                 graph_db_root: Optional[str] = None):
        """
        Initialize the integration.
        
        Args:
            raxkg_root: Path to RAXKG repository root
            schema_path: Path to RAXKG schema file
            graph_db_root: Path to graph database output directory
        """
        self.raxkg_root = Path(raxkg_root) if raxkg_root else self._find_raxkg_root()
        self.schema_path = Path(schema_path) if schema_path else self._find_schema_path()
        self.graph_db_root = Path(graph_db_root) if graph_db_root else self._find_graph_db_root()
        
        # Validate paths
        self._validate_paths()
        
        print(f"RAXKG Integration initialized:")
        print(f"  RAXKG root: {self.raxkg_root}")
        print(f"  Schema: {self.schema_path}")
        print(f"  Graph DB root: {self.graph_db_root}")
        
    def _find_raxkg_root(self) -> Path:
        """Try to find RAXKG repository root automatically."""
        # Common locations to check
        potential_paths = [
            Path(r"C:\workspace\SCAI\COMMUTE-Knowledge-Graph"),  # User provided path
            Path.cwd().parent / "COMMUTE-Knowledge-Graph",  # Sibling directory
            Path.cwd().parent / "raxkg",  # Sibling directory
            Path.cwd().parent.parent / "raxkg",  # Uncle directory
            Path.home() / "raxkg",  # Home directory
            Path("/workspace/SCAI/raxkg"),  # Workspace
            Path("C:/workspace/SCAI/raxkg")  # Windows workspace
        ]
        
        for path in potential_paths:
            if path.exists() and (path / "src" / "raxkg").exists():
                return path
                
        # Default fallback to user provided path
        return Path(r"C:\workspace\SCAI\COMMUTE-Knowledge-Graph")
        
    def _find_schema_path(self) -> Path:
        """Find the RAXKG schema file."""
        if self.raxkg_root:
            schema_path = self.raxkg_root / "data" / "schema" / "latest_schema.json"
            if schema_path.exists():
                return schema_path
                
        # Default fallback
        return self.raxkg_root / "data" / "schema" / "latest_schema.json"
        
    def _find_graph_db_root(self) -> Path:
        """Find the graph database root directory."""
        if self.raxkg_root:
            return self.raxkg_root / "data" / "graph_db"
        return Path.cwd() / "graph_db"
        
    def _validate_paths(self):
        """Validate that required paths exist or can be created."""
        if not self.raxkg_root.exists():
            print(f"Warning: RAXKG root not found: {self.raxkg_root}")
            
        if not self.schema_path.exists():
            print(f"Warning: Schema file not found: {self.schema_path}")
            
        # Create graph DB root if it doesn't exist
        self.graph_db_root.mkdir(parents=True, exist_ok=True)
        
    def collect_and_build_graph(self, 
                              project_names: List[str],
                              version_name: Optional[str] = None,
                              interactive: bool = False,
                              cleanup_xml: bool = True) -> Tuple[str, List[str]]:
        """
        Complete workflow: collect CORDIS XML and build graph database.
        
        Args:
            project_names: List of project names/IDs to collect
            version_name: Version name for graph DB (auto-generated if None)
            interactive: Whether to prompt for disambiguation
            cleanup_xml: Whether to clean up temporary XML files
            
        Returns:
            Tuple of (graph_db_version_path, list_of_xml_files)
        """
        print(f"\n{'='*80}")
        print("CORDIS → RAXKG INTEGRATION WORKFLOW")
        print('='*80)
        
        # Step 1: Generate version name
        if not version_name:
            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            version_name = f"v{timestamp}-cordis-auto"
            
        print(f"Version: {version_name}")
        print(f"Projects to collect: {len(project_names)}")
        
        # Step 2: Create temporary directory for XML collection
        with tempfile.TemporaryDirectory(prefix="cordis_raxkg_") as temp_dir:
            print(f"Temporary XML directory: {temp_dir}")
            
            # Step 3: Collect CORDIS XML files
            collector = CordisXMLCollector(temp_dir, interactive=interactive)
            xml_files, metadata_file = collector.collect_and_save_batch(
                project_names,
                f"cordis_{version_name}",
                delay=1.0  # Be respectful to CORDIS servers
            )
            
            if not xml_files:
                raise Exception("No XML files were collected successfully!")
                
            print(f"✓ Collected {len(xml_files)} XML files")
            
            # Step 4: Build graph database using RAXKG
            graph_db_path = self._build_raxkg_graph(xml_files, version_name)
            
            # Step 5: Copy metadata to graph DB directory
            if os.path.exists(metadata_file):
                dest_metadata = Path(graph_db_path) / "cordis_collection_metadata.json"
                shutil.copy2(metadata_file, dest_metadata)
                print(f"✓ Copied collection metadata to {dest_metadata}")
                
            # Step 6: Optionally save XML files
            saved_xml_files = []
            if not cleanup_xml:
                xml_archive_dir = Path(graph_db_path) / "source_xml"
                xml_archive_dir.mkdir(exist_ok=True)
                
                for xml_file in xml_files:
                    dest_file = xml_archive_dir / os.path.basename(xml_file)
                    shutil.copy2(xml_file, dest_file)
                    saved_xml_files.append(str(dest_file))
                    
                print(f"✓ Archived {len(saved_xml_files)} XML files")
            
            return graph_db_path, saved_xml_files or xml_files
            
    def _build_raxkg_graph(self, xml_files: List[str], version_name: str) -> str:
        """
        Build RAXKG graph database from collected XML files.
        
        Args:
            xml_files: List of XML file paths
            version_name: Version name for the graph
            
        Returns:
            Path to created graph database version directory
        """
        print(f"\nBuilding RAXKG graph database...")
        print(f"  Input XML files: {len(xml_files)}")
        print(f"  Version: {version_name}")
        
        # Construct RAXKG build command
        cmd = [
            "python", "-m", "raxkg.populate_graph.build_graph_db",
            "--schema", str(self.schema_path),
            "--root", str(self.graph_db_root),
            "--version", version_name,
            "--source", "cordis"
        ]
        
        # Add XML files
        for xml_file in xml_files:
            cmd.extend(["--xml", xml_file])
            
        print(f"Executing: {' '.join(cmd)}")
        
        try:
            # Change to RAXKG directory for execution
            original_cwd = os.getcwd()
            os.chdir(self.raxkg_root)
            
            # Set PYTHONPATH to include RAXKG src
            env = os.environ.copy()
            src_path = str(self.raxkg_root / "src")
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
            else:
                env["PYTHONPATH"] = src_path
                
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                print(f"✗ RAXKG build failed!")
                print(f"STDOUT:\n{result.stdout}")
                print(f"STDERR:\n{result.stderr}")
                raise Exception(f"RAXKG build failed with code {result.returncode}")
                
            print(f"✓ RAXKG build successful!")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
                
            # Return path to created version
            version_path = self.graph_db_root / version_name
            return str(version_path)
            
        finally:
            os.chdir(original_cwd)
            
    def import_to_neo4j(self, graph_db_path: str, 
                       neo4j_uri: str = "bolt://localhost:7687",
                       user: str = "neo4j",
                       password: Optional[str] = None,
                       dry_run: bool = True) -> bool:
        """
        Import graph database to Neo4j.
        
        Args:
            graph_db_path: Path to graph database version
            neo4j_uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
            dry_run: Whether to perform dry run only
            
        Returns:
            True if successful
        """
        print(f"\nImporting to Neo4j...")
        print(f"  Graph DB: {graph_db_path}")
        print(f"  Neo4j URI: {neo4j_uri}")
        print(f"  Dry run: {dry_run}")
        
        cmd = [
            "python", "-m", "raxkg.populate_graph.import_to_neo4j.import_graph_db",
            "--graph-db", graph_db_path,
            "--neo4j-uri", neo4j_uri,
            "--user", user
        ]
        
        if password:
            cmd.extend(["--password", password])
            
        if dry_run:
            cmd.append("--dry-run")
        else:
            cmd.append("--create-constraints")
            
        print(f"Executing: {' '.join(cmd[:-1])} [password hidden]")
        
        try:
            original_cwd = os.getcwd()
            os.chdir(self.raxkg_root)
            
            env = os.environ.copy()
            src_path = str(self.raxkg_root / "src")
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
            else:
                env["PYTHONPATH"] = src_path
                
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode != 0:
                print(f"✗ Neo4j import failed!")
                print(f"STDOUT:\n{result.stdout}")
                print(f"STDERR:\n{result.stderr}")
                return False
                
            print(f"✓ Neo4j import successful!")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
                
            return True
            
        except subprocess.TimeoutExpired:
            print("✗ Neo4j import timed out!")
            return False
        finally:
            os.chdir(original_cwd)


def test_integration():
    """Test the CORDIS-RAXKG integration."""
    print("=== Testing CORDIS-RAXKG Integration ===")
    
    # Test projects
    test_projects = [
        "COMORBIDITY MECHANISMS UTILIZED IN HEALTHCARE",
        # Add more test projects as needed
    ]
    
    try:
        # Initialize integration
        integration = CordisRAXKGIntegration()
        
        # Run complete workflow
        graph_db_path, xml_files = integration.collect_and_build_graph(
            test_projects,
            version_name="test-integration-v1",
            interactive=False,
            cleanup_xml=False
        )
        
        print(f"\n✓ Integration test successful!")
        print(f"  Graph DB: {graph_db_path}")
        print(f"  XML files: {len(xml_files)}")
        
        # Test Neo4j dry run
        success = integration.import_to_neo4j(
            graph_db_path,
            dry_run=True
        )
        
        if success:
            print(f"✓ Neo4j dry run successful!")
        else:
            print(f"✗ Neo4j dry run failed!")
            
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        raise


if __name__ == "__main__":
    test_integration()