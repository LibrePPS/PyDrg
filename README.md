# PyDrg

PyDrg is a comprehensive Python toolkit for interacting with key components of the US healthcare reimbursement system. It provides a unified, developer-friendly interface to official CMS (Centers for Medicare & Medicaid Services) software, enabling programmatic access to:

- **MS-DRG Grouper:** Assigns inpatient claims to Diagnosis-Related Groups (DRGs) for payment determination.
- **MCE Editor:** Validates inpatient claims against the Medicare Code Editor (MCE) to ensure clinical coherence.
- **IOCE Editor:** Processes outpatient claims through the Integrated Outpatient Code Editor (IOCE) to assign Ambulatory Payment Classifications (APCs).
- **IPPS Pricer:** Calculates the reimbursement amount for inpatient claims under the Inpatient Prospective Payment System (IPPS).
- **OPPS Pricer:** Calculates the reimbursement amount for outpatient claims under the Outpatient Prospective Payment System (OPPS).

Built on top of the official Java-based CMS tools, PyDrg uses `jpype` to create a seamless bridge to Python, allowing developers, analysts, and researchers to integrate these critical healthcare components into their workflows for automation, analytics, and research.

## What is PyDrg?

In the complex world of healthcare reimbursement, claims are processed through a series of steps to determine how much a provider should be paid. PyDrg simplifies this process by providing a single, easy-to-use Python library that handles the most important of these steps:

- **Grouping:** Assigning a standardized code (like a DRG or APC) that categorizes the patient's episode of care.
- **Editing:** Checking the claim for errors or inconsistencies based on clinical and coding rules.
- **Pricing:** Calculating the final payment amount based on the assigned group and other factors.

By wrapping the official CMS software, PyDrg ensures that you are using the same logic as Medicare and other major payers, providing a high degree of accuracy and reliability.

## Features

- **Unified Interface:** A single, consistent API for interacting with multiple CMS tools.
- **Flexible Claim Construction:** Easily create and modify claims using Pydantic data models.
- **Support for Multiple Editors:** Includes interfaces for both the MCE (inpatient) and IOCE (outpatient) editors.
- **Inpatient Pricing:** A full-featured IPPS pricer for calculating inpatient reimbursement.
- **Extensible:** The underlying architecture makes it easy to add new components or customize existing ones.
- **Example Scripts:** Get up and running quickly with a comprehensive set of examples in `main.py`.

## Requirements

- Python 3.10+
- Java (JRE/JDK, Java 17+ is recommended)
- JPype1 (Python-Java bridge)
- DRG, MCE, IOCE, and IPPS Java JAR files (provided in the `jars/` directory or downloadable)

## Installation

1.  **Clone this repository:**
    ```bash
    git clone https://github.com/LibrePPS/PyDrg.git
    cd PyDrg
    ```
2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    or, if you use [uv](https://github.com/astral-sh/uv):
    ```bash
    uv sync
    ```
3.  **Ensure Java is installed and available in your PATH.**
    - Check with: `java -version`

## Setup

- **JAR Files:**
    - Place all required JAR files in the `jars/` directory. These are needed for the Java logic to run.
    - You can use the `helpers/cms_downloader.py` script to automatically download the latest JARs from CMS.
- **IPSF Database:**
    - The IPPS Pricer requires a database of provider-specific information. To create this database, run the following command once:
        ```python
        from pricers.ipsf import IPSFDatabase
        db_path = "./ipsf_data.db"
        ipsf_db = IPSFDatabase(db_path)
        ipsf_db.to_sqlite()
        ```

## Usage

The `main.py` script provides a comprehensive set of examples for using all the features of PyDrg. Here's a brief overview of how to use each component:

### MS-DRG Grouper

The `DrgClient` is used to process inpatient claims and assign a DRG.

```python
from msdrg.drg_client import DrgClient
from input.claim import Claim, DiagnosisCode

drg_client = DrgClient()
claim = Claim()
claim.principal_dx = DiagnosisCode(code="I10", poa="Y")
# ... set other claim fields ...
drg_output = drg_client.process(claim)
print(drg_output.model_dump_json(indent=2))
```

### MCE Editor

The `MceClient` is used to validate inpatient claims against the MCE edits.

```python
from mce.mce_client import MceClient

mce_client = MceClient()
# ... create a claim ...
mce_output = mce_client.process(claim)
print(mce_output.model_dump_json(indent=2))
```

### IOCE Editor

The `IoceClient` is used to process outpatient claims through the IOCE editor.

```python
from ioce.ioce import IoceClient

ioce_client = IoceClient()
# ... create an outpatient claim ...
ioce_output = ioce_client.process(ioce_claim)
print(ioce_output.model_dump_json(indent=2))
```

### IPPS Pricer

The `IppsClient` is used to calculate the reimbursement for an inpatient claim. It requires the output from the `DrgClient`.

```python
from pricers.ipps import IppsClient
from pricers.ipsf import IPSFDatabase

db_path = "./ipsf_data.db"
ipsf_db = IPSFDatabase(db_path)
ipps_client = IppsClient("path/to/ipps-pricer.jar", ipsf_db.connection)
# ... create a claim and get the DRG output ...
ipps_output = ipps_client.process(claim, drg_output)
print(ipps_output.model_dump_json(indent=2))
```

## Project Structure

- `main.py` – Example script for running the various clients
- `msdrg/` – MS-DRG Grouper client and output models
- `mce/` – MCE Editor client and output models
- `ioce/` – IOCE Editor client and output models
- `pricers/` – IPPS and Opps Pricer client(s) and related components
- `input/` – Pydantic models for claims and related data
- `helpers/` – Utility scripts, including the CMS downloader
- `jars/` – Directory for Java JAR files (not tracked in git)

## Troubleshooting

- **JVM Not Started:** Ensure Java is installed and the JAR path is correct.
- **Missing JARs:** Download or copy the required JARs into the `jars/` directory.
- **JPype Errors:** Make sure JPype1 is installed and matches your Python version.
- **IPPS Pricer Errors:** Ensure you have created the `ipsf_data.db` file and that the path to the IPPS pricer JAR is correct.

## License

MIT License. See [LICENSE](LICENSE).