# CORDIS Web Crawler - Copilot Instructions

## Project Overview

This project provides automated collection of CORDIS (Community Research and Development Information Service) XML project data and integration with the RAXKG (Research Analytics eXploration Knowledge Graph) pipeline. The system enables researchers to search for EU research projects by name, download their complete XML metadata, and automatically build knowledge graphs for analysis.

### Core Functionality
- **Automated CORDIS Search**: Multi-strategy web scraping with fuzzy matching
- **XML Data Collection**: Complete project metadata extraction with validation
- **RAXKG Integration**: Seamless connection to knowledge graph pipeline
- **Production CLI**: Command-line interface for batch operations and Neo4j import

## Architecture and Design Patterns

### Directory Structure
```
src/web_crawler/cordis_crawler/
├── cordis_cli.py           # Command-line interface (entry point)
├── cordis_collector.py     # Main orchestrator
├── raxkg_integration.py    # RAXKG pipeline integration
├── cordis_search.py        # Web scraping and search functionality
├── project_matcher.py      # Fuzzy matching algorithms
├── xml_downloader.py       # XML download and validation
└── cordis_research.py      # Research and analysis tools
```

### Design Principles
1. **Modular Architecture**: Each component has a single responsibility
2. **Graceful Error Handling**: Comprehensive error recovery and logging
3. **Rate Limiting**: Respectful interaction with CORDIS servers
4. **Flexible Matching**: Multiple fallback strategies for project identification
5. **Data Validation**: XML namespace validation and integrity checks

## Key Components

### 1. CordisSearcher (`cordis_search.py`)
**Purpose**: Web scraping CORDIS database using Selenium WebDriver
- **Methods**: `search_projects()`, `setup_driver()`, `cleanup()`
- **Technology**: Selenium Chrome WebDriver with dynamic content handling
- **Rate Limiting**: Built-in delays to prevent server overload
- **Fallback Strategy**: Multiple CSS selectors for robust element detection

### 2. ProjectMatcher (`project_matcher.py`)
**Purpose**: Intelligent fuzzy matching for ambiguous project names
- **Algorithm**: fuzzywuzzy with Levenshtein distance scoring
- **Accuracy**: Achieved 87% match score in testing
- **Methods**: `find_best_project()`, `calculate_match_score()`
- **Fallback**: Multiple matching criteria (title, description, acronym)

### 3. CordisXMLDownloader (`xml_downloader.py`)
**Purpose**: XML download, validation, and metadata extraction
- **URL Pattern**: `https://cordis.europa.eu/project/id/{ID}?format=xml`
- **Validation**: ElementTree parsing with namespace support
- **Methods**: `download_xml()`, `validate_xml()`, `extract_metadata()`
- **Batch Processing**: Concurrent downloads with error handling

### 4. CordisXMLCollector (`cordis_collector.py`)
**Purpose**: Main orchestrator coordinating the entire workflow
- **Workflow**: Search → Match → Download → Validate
- **Statistics**: Success/failure tracking with detailed reporting
- **Methods**: `collect_xml()`, `collect_and_save_batch()`
- **Error Recovery**: Comprehensive fallback mechanisms

### 5. CordisRAXKGIntegration (`raxkg_integration.py`)
**Purpose**: Bridge between CORDIS collection and RAXKG pipeline
- **Integration**: Subprocess execution of RAXKG build_graph_db
- **Path Detection**: Automatic detection of COMMUTE-Knowledge-Graph location
- **Methods**: `collect_and_build_graph()`, `run_raxkg_pipeline()`
- **Neo4j Support**: Dry-run and production import capabilities

### 6. CLI Interface (`cordis_cli.py`)
**Purpose**: Production command-line interface for end users
- **Commands**: Collect, build-graph, full-pipeline, neo4j-import
- **Options**: Batch processing, custom paths, dry-run mode
- **Examples**: Comprehensive usage examples for all scenarios

## Technical Dependencies

### Core Libraries
- **Python 3.8+**: Required for modern type hints and async support
- **Selenium >= 4.6.0**: Web scraping with Chrome WebDriver
- **fuzzywuzzy >= 0.18.0**: Fuzzy string matching algorithms
- **python-levenshtein >= 0.12.0**: Fast string distance calculations
- **requests >= 2.32.3**: HTTP client for XML downloads
- **lxml >= 6.0.1**: XML parsing and validation

### External Dependencies
- **Chrome Browser**: Required for Selenium WebDriver
- **ChromeDriver**: Automatically managed by Selenium
- **RAXKG Pipeline**: Located at `C:\workspace\SCAI\COMMUTE-Knowledge-Graph`

## Usage Patterns

### Basic XML Collection
```python
from cordis_collector import CordisXMLCollector

collector = CordisXMLCollector()
xml_files = collector.collect_xml(["COMMUTE"], output_dir="./xml_output")
```

### Full Pipeline with RAXKG
```python
from raxkg_integration import CordisRAXKGIntegration

integration = CordisRAXKGIntegration()
results = integration.collect_and_build_graph(
    project_names=["COMMUTE"],
    raxkg_path="C:/workspace/SCAI/COMMUTE-Knowledge-Graph"
)
```

### CLI Usage
```bash
# Collect XML only
python cordis_cli.py collect "COMMUTE" --output ./xml_data

# Full pipeline with Neo4j
python cordis_cli.py full-pipeline "COMMUTE" --raxkg-path ./COMMUTE-Knowledge-Graph --neo4j-import
```

## Configuration and Environment

### Environment Variables
- `CORDIS_DELAY`: Override default search delay (default: 2 seconds)
- `CHROME_BINARY_PATH`: Custom Chrome browser location
- `RAXKG_DEFAULT_PATH`: Default RAXKG installation path

### WebDriver Configuration
```python
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Production mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
```

### XML Namespace Handling
```xml
<project xmlns="https://cordis.europa.eu/xml/project" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
```

## Error Handling and Debugging

### Common Error Patterns
1. **Selenium TimeoutException**: CORDIS page load timeout
   - **Solution**: Increase wait times, check network connectivity
2. **XMLSyntaxError**: Malformed XML from CORDIS
   - **Solution**: Validate XML before processing, implement fallback parsing
3. **ProcessExecutionError**: RAXKG pipeline failure
   - **Solution**: Check RAXKG dependencies, validate file paths

### Logging Configuration
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cordis_crawler.log'),
        logging.StreamHandler()
    ]
)
```

### Debug Mode
Enable detailed logging for troubleshooting:
```python
collector = CordisXMLCollector(debug=True)
```

## Testing and Validation

### Test Data
- **COMMUTE Project**: Primary test case (ID: 101006589)
- **Expected Output**: 62,949 bytes XML file
- **Match Score**: 87% accuracy with ProjectMatcher
- **RAXKG Output**: 22 nodes, 23 relationships

### Validation Checklist
- [ ] XML files are valid and well-formed
- [ ] Project metadata extraction is complete
- [ ] RAXKG pipeline executes successfully
- [ ] Neo4j import completes without errors
- [ ] All temporary files are cleaned up

### Performance Benchmarks
- **Search Time**: ~5-10 seconds per project
- **XML Download**: ~2-5 seconds per file
- **RAXKG Build**: ~30-60 seconds depending on data size
- **Memory Usage**: <500MB for typical batch operations

## Integration Guidelines

### RAXKG Pipeline Requirements
1. **Path Structure**: Must contain `build_graph_db` and `neo4j_import` modules
2. **Python Environment**: Compatible with CORDIS crawler dependencies  
3. **Configuration**: Proper Neo4j connection settings in RAXKG config

### Extension Points
1. **Custom Matchers**: Implement `ProjectMatcherInterface`
2. **Alternative Downloaders**: Extend `XMLDownloaderBase`
3. **Pipeline Stages**: Add custom processors to `CordisXMLCollector`

### API Integration
```python
# For programmatic access
from cordis_crawler.cordis_collector import CordisXMLCollector

class CustomCordisIntegration:
    def __init__(self):
        self.collector = CordisXMLCollector()
    
    def process_projects(self, names: List[str]) -> Dict[str, Any]:
        return self.collector.collect_and_save_batch(names)
```

## Troubleshooting Guide

### Issue: "No module named 'fuzzywuzzy'"
**Solution**: Install missing dependencies
```bash
pip install fuzzywuzzy python-levenshtein
```

### Issue: Chrome WebDriver not found
**Solution**: Update Selenium (auto-manages ChromeDriver)
```bash
pip install --upgrade selenium
```

### Issue: RAXKG path not found
**Solution**: Specify correct path or use auto-detection
```python
integration = CordisRAXKGIntegration()
integration.find_raxkg_path()  # Auto-detection
```

### Issue: XML namespace errors
**Solution**: Update XML parsing configuration
```python
namespaces = {
    'cordis': 'https://cordis.europa.eu/xml/project'
}
```

## Future Development

### Planned Enhancements
1. **Multi-threading**: Parallel XML downloads for improved performance
2. **Caching Layer**: Redis/file-based caching for repeated searches
3. **Advanced Matching**: Machine learning-based project matching
4. **API Server**: REST API for remote access
5. **Monitoring**: Prometheus metrics and health checks

### Extension Opportunities
1. **Additional Data Sources**: Horizon Europe, FP7 archives
2. **Export Formats**: JSON, CSV, RDF serialization
3. **Visualization**: Interactive project network graphs
4. **Analytics**: Project trend analysis and reporting

---

## Quick Reference

### Key File Locations
- **Main CLI**: `src/web_crawler/cordis_crawler/cordis_cli.py`
- **Configuration**: `pyproject.toml`
- **RAXKG Integration**: `C:\workspace\SCAI\COMMUTE-Knowledge-Graph`
- **Output Directory**: `./cordis_xml_output/` (default)

### Important URLs
- **CORDIS Search**: `https://cordis.europa.eu/projects/en`
- **XML Pattern**: `https://cordis.europa.eu/project/id/{ID}?format=xml`
- **CORDIS API Docs**: `https://cordis.europa.eu/data/`

### Contact and Support
- **Primary Developer**: Development team via GitHub issues
- **Documentation**: README.md and inline docstrings
- **Integration Support**: RAXKG team for knowledge graph questions