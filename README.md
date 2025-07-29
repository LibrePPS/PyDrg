# PyDrg

A Python interface for DRG (Diagnosis-Related Group) grouping using Java-based DRG logic via JPype.

## Features
- Loads Java DRG grouping logic from JAR files
- Processes claims and returns DRG results

## Requirements
- Python 3.7+
- Java (JRE/JDK, version compatible with your JARs)
- JPype1
- DRG Java JAR files (provided in the `jars/` directory)

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/LibrePPS/PyDrg.git
   cd PyDrg
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   or
   ```bash
   uv sync
   ```
3. Ensure Java is installed and available in your PATH.

## Setup
- Place all required DRG JAR files in the `jars/` directory.
- Optionally, set the `MSDRG_JAR_PATH` environment variable to override the default JAR path.
- Optionally use the `cms_downloader.py` script located in the `helpers/` directory to download the necessary JARs automatically.

## Usage
Run the main script to process a sample claim:
```bash
python main.py
```

You can modify `main.py` to construct and process your own claims. Example usage:
```python
from drg_client import DrgClient
from claim import Claim, DiagnosisCode

drg_client = DrgClient()
claim = Claim()
claim.principal_dx = DiagnosisCode(code="I10", poa="Y")
# ... set other claim fields ...
drg_client.process(claim)
```

## License
MIT License. See [LICENSE](LICENSE).
