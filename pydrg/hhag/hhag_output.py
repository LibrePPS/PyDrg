from pydrg.helpers.utils import ReturnCode
from pydantic import BaseModel
from typing import Optional


class HhagEdit(BaseModel):
    edit_id: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None

    def from_java(self, java_obj):
        self.edit_id = str(java_obj.getId().getDescription())
        self.description = str(java_obj.getDescription())
        self.type = str(java_obj.getType().getName())
        self.severity = str(java_obj.getServerityLevel().getName())


class HhagOutput(BaseModel):
    hipps_code: Optional[str] = None
    return_code: Optional[ReturnCode] = None
    validity_flag: Optional[str] = None
    edits: Optional[list[HhagEdit]] = None

    def from_java(self, java_obj):
        return_code = java_obj.getReturnCodeValue()
        if return_code is not None:
            self.return_code = ReturnCode()
            self.return_code.code = str(return_code)
            self.return_code.description = str(java_obj.getReturnCodeDescription())
        self.hipps_code = str(java_obj.getHippsCode())
        edits = (
            java_obj.getEdits()
        )  # <-- Returns an edit colletion, which is not iterable
        if edits is not None:
            for (
                edit
            ) in edits.getEdits():  # <--- We have to call getEdits() on the collection
                if self.edits is None:
                    self.edits = []
                new_edit = HhagEdit()
                new_edit.from_java(edit)
                self.edits.append(new_edit)
