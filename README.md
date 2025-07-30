# PyDrg

PyDrg is a Python interface for DRG (Diagnosis-Related Group) grouping, leveraging official Java-based CMS DRG Grouper via JPype. It enables healthcare and analytics developers to programmatically group inpatient claims into DRGs using the same logic as CMS and other payers, directly from Python.

## What is DRG Grouping?
Diagnosis-Related Groups (DRGs) are a patient classification system that standardizes prospective payment to hospitals and encourages cost containment initiatives. DRG grouping is the process of assigning a hospital claim to a DRG based on diagnoses, procedures, patient demographics, and other claim data. This is essential for:
- Hospital billing and reimbursement
- Healthcare analytics and reporting
- Quality and compliance initiatives

PyDrg wraps the official Java DRG grouper, making it accessible from Python for integration, automation, and research.

## Features
- Loads and manages multiple DRG grouper Java versions (JARs)
- Processes claims and returns DRG results using official logic
- Supports dynamic claim construction and flexible input
- Example scripts for quick start and testing

## Requirements
- Python 3.10+
- Java (JRE/JDK, Java 17+ is recommended)
- JPype1 (Python-Java bridge)
- DRG Java JAR files (provided in the `jars/` directory or downloadable)

## Installation
1. **Clone this repository:**
   ```bash
   git clone https://github.com/LibrePPS/PyDrg.git
   cd PyDrg
   ```
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   or, if you use [uv](https://github.com/astral-sh/uv):
   ```bash
   uv sync
   ```
3. **Ensure Java is installed and available in your PATH.**
   - Check with: `java -version`

## Setup
- **JAR Files:**
  - Place all required DRG JAR files in the `jars/` directory. These are needed for the Java logic to run.
  - You can use the `helpers/cms_downloader.py` script to automatically download the latest JARs from CMS.
- **Environment Variable (Optional):**
  - By default, the code loads all JARs in `jars/`. To override, set the `MSDRG_JAR_PATH` environment variable:
    ```bash
    export MSDRG_JAR_PATH="/path/to/your/jars/*"
    ```

## Usage
1. **Run the main script to process a sample claim:**
   ```bash
   python main.py
   ```
   This will load the Java DRG logic, create a sample claim, and print the DRG result.

2. **Integrate in your own scripts:**
   Import and use the `DrgClient` and claim classes:
   ```python
   from drg_client import DrgClient
   from claim import Claim, DiagnosisCode

   drg_client = DrgClient()
   claim = Claim()
   claim.principal_dx = DiagnosisCode(code="I10", poa="Y")
   # ... set other claim fields ...
   drg_client.process(claim)
   ```

3. **Customizing Claims:**
   - See `main.py` for a full example of claim construction.
   - Claims can include principal and secondary diagnoses, procedures, patient demographics, and more.

## Project Structure
- `main.py` – Example script for running the grouper
- `drg_client.py` – Main Python interface to the Java DRG logic
- `claim.py` – Data models for claims, diagnoses, procedures, etc.
- `helpers/cms_downloader.py` – Script to download official JARs
- `jars/` – Directory for Java JAR files (not tracked in git)

## Troubleshooting
- **JVM Not Started:** Ensure Java is installed and the JAR path is correct.
- **Missing JARs:** Download or copy the required JARs into the `jars/` directory.
- **JPype Errors:** Make sure JPype1 is installed and matches your Python version.

## License
MIT License. See [LICENSE](LICENSE).
