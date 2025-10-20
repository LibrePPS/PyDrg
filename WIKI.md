# PyDrg Wiki

Welcome to the PyDrg wiki! This document provides a comprehensive guide to using the PyDrg library, a powerful Python toolkit for interacting with various components of the US healthcare reimbursement system.

## Table of Contents

1.  [Introduction](#introduction)
2.  [Installation](#installation)
3.  [Core Concepts](#core-concepts)
    -   [The `Claim` Object](#the-claim-object)
    -   [Pricer and Grouper Clients](#pricer-and-grouper-clients)
    -   [Provider Data (IPSF & OPSF)](#provider-data-ipsf--opsf)
4.  [Getting Started: The `Pypps` Class](#getting-started-the-pypps-class)
5.  [Usage Examples](#usage-examples)
    -   [MS-DRG Grouper (`DrgClient`)](#ms-drg-grouper-drgclient)
    -   [MCE Editor (`MceClient`)](#mce-editor-mceclient)
    -   [IOCE Editor (`IoceClient`)](#ioce-editor-ioceclient)
    -   [HHA Grouper (`HhagClient`)](#hha-grouper-hhagclient)
    -   [IRF Grouper (`IrfgClient`)](#irf-grouper-irfgclient)
    -   [IPPS Pricer (`IppsClient`)](#ipps-pricer-ippsclient)
    -   [OPPS Pricer (`OppsClient`)](#opps-pricer-oppsclient)
    -   [IPF Pricer (`IpfClient`)](#ipf-pricer-ipfclient)
    -   [LTCH Pricer (`LtchClient`)](#ltch-pricer-ltchclient)
    -   [SNF Pricer (`SnfClient`)](#snf-pricer-snfclient)
    -   [Hospice Pricer (`HospiceClient`)](#hospice-pricer-hospiceclient)
    -   [ESRD Pricer (`EsrdClient`)](#esrd-pricer-esrdclient)
6.  [Advanced Features](#advanced-features)
    -   [ICD-10 Code Conversion](#icd-10-code-conversion)
7.  [Extending PyDrg with Plugins](#extending-pydrg-with-plugins)
8.  [Under the Hood: `CMSDownloader`](#under-the-hood-cmsdownloader)

---

## Introduction

PyDrg provides a unified, developer-friendly interface to official CMS (Centers for Medicare & Medicaid Services) software. It wraps the official Java-based tools, allowing you to perform complex healthcare reimbursement tasks like grouping, editing, and pricing claims directly within your Python applications.

PyDrg simplifies interaction with major PPS (Prospective Payment System) components, including:

*   **Groupers:** MS-DRG, HHA (Home Health), IRF (Inpatient Rehabilitation Facility)
*   **Code Editors:** MCE (Medicare Code Editor), IOCE (Integrated Outpatient Code Editor)
*   **Pricers:** IPPS, OPPS, IPF, LTCH, SNF, Hospice, and ESRD.

By using the official CMS software, PyDrg ensures accuracy and reliability in your reimbursement-related workflows.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/LibrePPS/PyDrg.git
    cd PyDrg
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    Or, using `uv`:
    ```bash
    uv sync
    ```

3.  **Java Requirement:**
    Ensure you have a Java Runtime Environment (JRE) or Java Development Kit (JDK) installed (Java 17+ is recommended). You can verify your installation with:
    ```bash
    java -version
    ```

## Core Concepts

### The `Claim` Object

The `pydrg.input.claim.Claim` object is the central data structure in PyDrg. It's a Pydantic model that represents a healthcare claim, containing all the necessary information for processing, such as:

*   Patient and provider details
*   Dates of service (`from_date`, `thru_date`)
*   Diagnosis codes (`principal_dx`, `secondary_dxs`)
*   Procedure codes (`inpatient_pxs`)
*   Line items, value codes, and condition codes

It also contains fields for specialized data, such as `oasis_assessment` for home health claims and `irf_pai` for inpatient rehabilitation claims.

You can easily create and manipulate `Claim` objects in your code. For more details on the available fields, refer to the source code in `pydrg/input/claim.py`.

### Pricer and Grouper Clients

Each CMS tool is accessed through a dedicated client class (e.g., `DrgClient`, `IppsClient`). These clients handle the interaction with the underlying Java libraries, providing a simple `process()` method that takes a `Claim` object (and sometimes other data) and returns a Pydantic output model with the results.

### Provider Data (IPSF & OPSF)

Many of the pricers (IPPS, OPPS, ESRD, etc.) depend on provider-specific data that varies based on location and fiscal year. This includes values like wage indices, cost-to-charge ratios, and various adjustment factors.

PyDrg manages this by loading provider-specific data from two main sources provided by CMS:

*   **IPSF (Inpatient Provider Specific File):** Used for inpatient-based pricers.
*   **OPSF (Outpatient Provider Specific File):** Used for outpatient-based pricers.

When you build the database (`Pypps(build_db=True)`), PyDrg downloads these files and stores them in a local SQLite database. During processing, the library automatically looks up the correct provider data based on the provider's NPI or CCN and the claim's service date.

#### Overriding Provider Data

For testing or what-if scenarios, you may need to override the provider data fetched from the database. You can do this by adding a dictionary to the `additional_data` field of the `Provider` object on your claim.

*   For inpatient pricers, use the key `"ipsf"`.
*   For outpatient pricers, use the key `"opsf"`.

The keys within this dictionary must match the attribute names in the `IPSFProvider` or `OPSFProvider` Pydantic models (see `pydrg/pricers/ipsf.py` and `pydrg/pricers/opsf.py` for all available fields).

**Example: Overriding the `special_wage_index` for an IPPS claim**

```python
claim = claim_example()

# Add the override dictionary to the billing provider
if claim.billing_provider:
    claim.billing_provider.additional_data["ipsf"] = {
        "special_wage_index": 1.25
    }

# When this claim is processed by the IPPS pricer, it will use 1.25
# for the special_wage_index, regardless of the value in the database.
drg_output = pypps.drg_client.process(claim)
ipps_output = pypps.ipps_client.process(claim, drg_output)
```

This provides a powerful way to isolate variables and test the impact of different provider-specific attributes on the final payment.

## Getting Started: The `Pypps` Class

The `pydrg.pypps.Pypps` class is the easiest way to get started with PyDrg. It acts as a manager for all the different clients and handles the complex setup process for you.

When you instantiate `Pypps`, you can configure it to:

*   Download the necessary CMS JAR files.
*   Set up the required SQLite databases for the pricers.

Here's how to initialize `Pypps` and set up all the clients:

```python
from pydrg.pypps import Pypps

# This will download JARs and build the database if they don't exist.
pypps = Pypps(build_jar_dirs=True, build_db=True)
pypps.setup_clients()
```

Once `pypps.setup_clients()` has been called, you can access the individual clients as attributes of the `pypps` object (e.g., `pypps.drg_client`).

## Usage Examples

Below are examples of how to use each of the main components of PyDrg.

### MS-DRG Grouper (`DrgClient`)

Assigns an MS-DRG to an inpatient claim.

```python
from pydrg.helpers import claim_example

# Assuming 'pypps' is an initialized Pypps instance
claim = claim_example()
drg_output = pypps.drg_client.process(claim)
print(drg_output.model_dump_json(indent=2))
```

### MCE Editor (`MceClient`)

Validates an inpatient claim against the Medicare Code Editor edits.

```python
from pydrg.helpers import claim_example

claim = claim_example()
mce_output = pypps.mce_client.process(claim)
print(mce_output.model_dump_json(indent=2))
```

### IOCE Editor (`IoceClient`)

Processes an outpatient claim to assign APCs and check for edits.

```python
from pydrg.helpers import opps_claim_example

opps_claim = opps_claim_example()
ioce_output = pypps.ioce_client.process(opps_claim)
print(ioce_output.model_dump_json(indent=2))
```

### HHA Grouper (`HhagClient`)

Groups a home health claim. This requires OASIS assessment data, which can be passed in the `additional_data` field of the `Claim` object.

```python
from pydrg.helpers import claim_example
from datetime import datetime

claim = claim_example()
claim.from_date = datetime(2025, 1, 1)
claim.thru_date = datetime(2025, 1, 31)

# Add OASIS data
claim.additional_data["oasis"] = {
    "fall_risk": True,
    "grooming": "1",
    "dress_upper": "2",
    # ... other OASIS fields
}

hhag_output = pypps.hhag_client.process(claim)
print(hhag_output.model_dump_json(indent=2))
```

### IRF Grouper (`IrfgClient`)

Groups an Inpatient Rehabilitation Facility (IRF) claim into a Case-Mix Group (CMG). This client requires an `IrfPai` assessment object to be attached to the claim.

**Required Fields:**

*   `claim.irf_pai`: An `IrfPai` object containing the Patient Assessment Instrument data.
*   `claim.admit_date`
*   `claim.patient.date_of_birth`
*   `claim.principal_dx`

The `IrfPai` object has numerous fields corresponding to the IRF-PAI form. Key fields include:

*   `impairment_admit_group_code`
*   Codes for various functional abilities (e.g., `eating_self_admsn_cd`, `walk_150_feet_cd`)

**Example:**

```python
from pydrg.input import IrfPai
from datetime import datetime

claim = claim_example()
claim.irf_pai = IrfPai()
claim.principal_dx.code = "D61.03"
claim.admit_date = datetime(2025, 1, 1)
claim.thru_date = datetime(2025, 1, 30)
claim.patient.date_of_birth = datetime(1970, 1, 1)

# Populate the IRF-PAI data
claim.irf_pai.assessment_system = "IRF-PAI"
claim.irf_pai.transaction_type = 1
claim.irf_pai.impairment_admit_group_code = "0012.9   "
claim.irf_pai.eating_self_admsn_cd = "06"
claim.irf_pai.walk_150_feet_cd = "06"
# ... and other assessment codes

irf_output = pypps.irfg_client.process(claim)
print(irf_output.model_dump_json(indent=2))
```

The `IrfgOutput` will contain the calculated `cmg_group`, `motor_score`, and any errors encountered during processing.

### IPPS Pricer (`IppsClient`)

Calculates payment for an inpatient claim. Requires the output from the `DrgClient`.

```python
claim = claim_example()
drg_output = pypps.drg_client.process(claim)
ipps_output = pypps.ipps_client.process(claim, drg_output)
print(ipps_output.model_dump_json(indent=2))
```

### OPPS Pricer (`OppsClient`)

Calculates payment for an outpatient claim. Requires the output from the `IoceClient`.

```python
opps_claim = opps_claim_example()
ioce_output = pypps.ioce_client.process(opps_claim)
opps_output = pypps.opps_client.process(opps_claim, ioce_output)
print(opps_output.model_dump_json(indent=2))
```

### IPF Pricer (`IpfClient`)

Calculates payment for an inpatient psychiatric facility claim.

```python
claim = claim_example()
drg_output = pypps.drg_client.process(claim)
ipf_output = pypps.ipf_client.process(claim, drg_output)
print(ipf_output.model_dump_json(indent=2))
```

### LTCH Pricer (`LtchClient`)

Calculates payment for a long-term care hospital claim.

```python
claim = claim_example()
# LTCH may require specific provider IDs
claim.billing_provider.other_id = "012006"
drg_output = pypps.drg_client.process(claim)
ltch_output = pypps.ltch_client.process(claim, drg_output)
print(ltch_output.model_dump_json(indent=2))
```

### SNF Pricer (`SnfClient`)

Calculates payment for a skilled nursing facility claim.

```python
from datetime import datetime

snf_claim = claim_example()
snf_claim.admit_date = datetime(2025, 1, 1)
snf_claim.from_date = datetime(2025, 1, 1)
snf_claim.thru_date = datetime(2025, 1, 20)
snf_claim.bill_type = "227" # SNF bill type
snf_output = pypps.snf_client.process(snf_claim)
print(snf_output.model_dump_json(indent=2))
```

### Hospice Pricer (`HospiceClient`)

Calculates payment for a hospice claim.

```python
hospice_claim = claim_example()
hospice_claim.bill_type = "812" # Hospice bill type
# ... other hospice-specific claim modifications
hospice_output = pypps.hospice_client.process(hospice_claim)
print(hospice_output.model_dump_json(indent=2))
```

### ESRD Pricer (`EsrdClient`)

Calculates payment for an End-Stage Renal Disease (ESRD) claim.

The `EsrdClient` has specific data requirements. Notably, some optional parameters are passed via the `additional_data` dictionary on the `Claim` object.

**Required Fields:**

*   `esrd_initial_date`: The date of the initial ESRD service.
*   `patient.date_of_birth`: The patient's date of birth.
*   Value codes `A8` (patient weight) and `A9` (patient height).
*   At least one dialysis line item with a revenue code of `0821`, `0831`, `0841`, `0851`, or `0881`.

**Optional `additional_data` for ESRD:**

You can provide additional ESRD-related data under the `"esrd"` key in the `additional_data` dictionary.

```python
claim.additional_data["esrd"] = {
    "ect_choice": "H",  # 'H', 'P', 'B', or None
    "ppa_adjustment": 0.5
}
```

*   `ect_choice` (str): The "Election of Treatment Choices" indicator. Can be one of:
    *   `'H'`: Home dialysis
    *   `'P'`: In-facility dialysis, with PPA
    *   `'B'`: Both home and in-facility, with PPA
    *   `None` or `""`: No special treatment choice.
*   `ppa_adjustment` (float): The **Performance Payment Adjustment** percentage. This is **required** if `ect_choice` is `'P'` or `'B'`.

**Example:**

```python
from datetime import datetime, timedelta
from pydrg.input import ValueCode, LineItem

claim = claim_example()
claim.billing_provider.other_id = "012525"
claim.esrd_initial_date = datetime(2025, 1, 1)
claim.cond_codes.append("74")

# Add required value codes
claim.value_codes.append(ValueCode(code="A8", amount=70.0)) # Weight
claim.value_codes.append(ValueCode(code="A9", amount=180.0)) # Height

# Add dialysis line items
start_date = datetime(2025, 1, 1)
while start_date < datetime(2025, 1, 26):
    line = LineItem(revenue_code="0821", service_date=start_date)
    claim.lines.append(line)
    start_date += timedelta(days=1)

# Add optional data
claim.additional_data["esrd"] = {
    "ect_choice": "P",
    "ppa_adjustment": 0.85
}

esrd_output = pypps.esrd_client.process(claim)
print(esrd_output.model_dump_json(indent=2))
```

## Advanced Features

### ICD-10 Code Conversion

CMS updates the valid set of ICD-10 codes annually for each fiscal year. This can create challenges when processing claims, as the diagnosis codes on a claim might be from a different fiscal year than the one the MS-DRG grouper expects.

PyDrg provides an `ICDConverter` to handle this complexity. It can map ICD-10 codes forward or backward to match the required version for the grouper.

#### How it Works

The `ICDConverter` uses a local SQLite database containing the official CMS conversion tables. When you process a claim, you can enable the converter to ensure all diagnosis codes are valid for the target grouper version.

The converter can be configured on the `Claim` object through the `icd_convert` attribute.

*   **`AUTO` mode (default):** The converter automatically determines the ICD-10 version of the claim based on its `thru_date`. It then compares this to the target version required by the grouper and performs the necessary mappings.
*   **`MANUAL` mode:** You can explicitly specify both the `billed_version` and `target_version` if you need to control the conversion process precisely.

#### Usage with the MS-DRG Grouper

Here is how you would use the `ICDConverter` before passing a claim to the `DrgClient`.

```python
from pydrg.input import ICDConvertOptions, ICDConvertOption
from pydrg.converter.icd_converter import ICDConverter

# Assuming 'pypps' is an initialized Pypps instance
claim = claim_example()

# 1. Initialize the converter
icd_converter = ICDConverter(db=pypps.db)

# 2. Set the conversion options on the claim
claim.icd_convert = ICDConvertOptions(
    option=ICDConvertOption.AUTO
)

# 3. Generate the mappings
# The target_vers for the DRG grouper is typically the DRG version (e.g., "410")
mappings = icd_converter.generate_claim_mappings(claim, target_vers="410")

# 4. (Optional) Apply the mappings to the claim object
# The DrgClient will do this automatically if mappings are found,
# but you can do it manually if needed.
# ... logic to update claim.principal_dx, etc., based on mappings ...

# 5. Process the claim. The DrgClient will use the converted codes.
drg_output = pypps.drg_client.process(claim)
print(drg_output.model_dump_json(indent=2))
```

When `drg_client.process(claim)` is called and it detects that `claim.icd_convert` is set, it will automatically run the `generate_claim_mappings` function and use the results for grouping, simplifying the process.

## Extending PyDrg with Plugins

PyDrg uses `pluggy` to allow for extending the functionality of the clients. This is an advanced feature for users who need to customize the behavior of the library.

The following hooks are available:

*   `client_load_classes(client)`: Allows you to load additional Java classes onto a client instance.
*   `client_methods(client)`: Allows you to add new methods to a client instance.

For more details, see `pydrg/plugins/hookspecs.py`.

## Under the Hood: `CMSDownloader`

The `pydrg.helpers.cms_downloader.CMSDownloader` class is responsible for downloading all the necessary JAR files from the CMS website. It's a powerful tool that can be used independently of the `Pypps` class if you need more control over the download process.

The downloader is designed to be robust, with features like:

*   Asynchronous downloads for improved performance.
*   Automatic extraction of JARs from ZIP archives.
*   Intelligent checking for existing files to avoid redundant downloads.

While you typically won't need to interact with `CMSDownloader` directly, it's a key part of what makes PyDrg easy to set up.