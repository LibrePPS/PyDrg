"""Top-level public API for the pydrg package.

This module re-exports commonly used classes and functions so users can write
concise imports like:

    from pydrg import (
        Claim, DiagnosisCode, ProcedureCode, PoaType, DxType,
        DrgClient, MsdrgOutput,
        MceClient, MceOutput,
        IoceClient, IoceOutput,
        IppsClient, IppsOutput, OppsClient, OppsOutput,
        IpfClient, IpfOutput, LtchClient, LtchOutput, HospiceClient, HospiceOutput,
        CMSDownloader, IPSFDatabase, OPSFDatabase, IPSFProvider, OPSFProvider, UrlLoader,
        Pypps,
    )
"""

# Core input models
# Helper utilities
from .helpers.cms_downloader import CMSDownloader
from .input.claim import (
    Address,
    Claim,
    DiagnosisCode,
    DxType,
    LineItem,
    OccurrenceCode,
    Patient,
    PoaType,
    ProcedureCode,
    Provider,
    SpanCode,
    ValueCode,
    ICDConvertOptions,
    ICDConvertOption,
    IrfPai,
    OasisAssessment,
    Modules,
)

# IOCE (OPPS code editor)
from .ioce.ioce_client import IoceClient
from .ioce.ioce_output import IoceOutput

# MCE editor
from .mce import MceClient, MceOutput, MceOutputDxCode, MceOutputPrCode

# MSDRG grouper
from .msdrg import DrgClient, MsdrgOutput, MsdrgOutputDxCode, MsdrgOutputPrCode
from .pricers.hospice import HospiceClient, HospiceOutput
from .pricers.ipf import IpfClient, IpfOutput

# HHA Grouper
from .hhag import HhagClient, HhagOutput, HhagEdit

# CMG Grouper
from .irfg.irfg_client import IrfgClient
from .irfg.irfg_output import IrfgOutput

# Pricers
from .pricers.ipps import IppsClient, IppsOutput

# Provider data access and classpath utilities
from .pricers.ipsf import IPSFDatabase, IPSFProvider
from .pricers.ltch import LtchClient, LtchOutput
from .pricers.opps import OppsClient, OppsOutput
from .pricers.opsf import OPSFDatabase, OPSFProvider
from .pricers.snf import SnfClient, SnfOutput
from .pricers.hha import HhaClient, HhaOutput
from .pricers.url_loader import UrlLoader
from .pricers.irf import IrfClient, IrfOutput
from .pricers.esrd import EsrdClient, EsrdOutput
from .pricers.fqhc import FqhcClient, FqhcOutput

from .converter import (
    create_database,
    expand_code_range,
    parse_icd_conversion_table,
    ICD10Conversion,
    ICDConverter,
    ICD10ConvertOutput,
)

# High-level orchestrator
from .pypps.pypps import Pypps, PyppsOutput

__all__ = [
    # Input models
    "Address",
    "Patient",
    "Provider",
    "Claim",
    "ValueCode",
    "ProcedureCode",
    "OccurrenceCode",
    "SpanCode",
    "DxType",
    "DiagnosisCode",
    "LineItem",
    "PoaType",
    "ICDConvertOption",
    "ICDConvertOptions",
    "IrfPai",
    "OasisAssessment",
    "Modules",
    # MSDRG
    "DrgClient",
    "MsdrgOutput",
    "MsdrgOutputDxCode",
    "MsdrgOutputPrCode",
    # CMG
    "IrfgClient",
    "IrfgOutput",
    # HHA
    "HhagClient",
    "HhagOutput",
    "HhagEdit",
    # MCE
    "MceClient",
    "MceOutput",
    "MceOutputDxCode",
    "MceOutputPrCode",
    # IOCE
    "IoceClient",
    "IoceOutput",
    # Pricers
    "IppsClient",
    "IppsOutput",
    "OppsClient",
    "OppsOutput",
    "IpfClient",
    "IpfOutput",
    "LtchClient",
    "LtchOutput",
    "HospiceClient",
    "HospiceOutput",
    "SnfClient",
    "SnfOutput",
    "HhaClient",
    "HhaOutput",
    "IrfClient",
    "IrfOutput",
    "EsrdClient",
    "EsrdOutput",
    "FqhcClient",
    "FqhcOutput",
    # Helpers and utilities
    "CMSDownloader",
    "IPSFDatabase",
    "OPSFDatabase",
    "IPSFProvider",
    "OPSFProvider",
    "UrlLoader",
    # Converter
    "ICD10Conversion",
    "ICDConverter",
    "create_database",
    "parse_icd_conversion_table",
    "expand_code_range",
    "ICD10ConvertOutput",
    # Orchestrator
    "Pypps",
    "PyppsOutput"
]
