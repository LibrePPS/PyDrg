from datetime import datetime
from typing import Optional

import jpype
from pydantic import BaseModel


class ReturnCode(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None
    explanation: Optional[str] = None

    def from_java(self, java_return_code: jpype.JClass):
        """
        Convert a Java ReturnCode object to a Python ReturnCode object.
        """
        if java_return_code is None:
            return
        self.code = str(java_return_code.getCode())
        self.description = str(java_return_code.getDescription())
        self.explanation = str(java_return_code.getExplanation())
        return


def float_or_none(value):
    """
    Convert a value to float or return None if conversion fails.
    """
    if value is None:
        return None
    try:
        return float(value.floatValue())
    except (ValueError, TypeError):
        return None


def py_date_to_java_date(self, py_date):
    """
    Convert a Python datetime object to a Java Date object.
    """
    if py_date is None:
        return None
    if isinstance(py_date, datetime):
        date = py_date.strftime("%Y%m%d")
        formatter = self.java_data_formatter.ofPattern("yyyyMMdd")
        return self.java_date_class.parse(date, formatter)
    elif isinstance(py_date, str):
        # Check that we're in YYYY-MM-DD format
        try:
            date = datetime.strptime(py_date, "%Y-%m-%d")
            return self.py_date_to_java_date(date)
        except ValueError:
            raise ValueError(
                f"Invalid date format: {py_date}. Expected format is YYYY-MM-DD."
            )
    elif isinstance(py_date, int):
        # Assuming the int is in YYYYMMDD format
        date_str = str(py_date)
        if len(date_str) != 8:
            raise ValueError(
                f"Invalid date integer: {py_date}. Expected format is YYYYMMDD."
            )
        formatter = self.java_data_formatter.ofPattern("yyyyMMdd")
        return self.java_date_class.parse(date_str, formatter)
    else:
        raise TypeError(
            f"Unsupported date type: {type(py_date)}. Expected datetime, str, or int in YYYYMMDD format."
        )
