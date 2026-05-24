from pydantic import BaseModel


class RepairPolicy(BaseModel):
    """Minimal permission policy for applying a generated patch plan."""

    require_confirmation: bool = True
    approved: bool = False

    def can_apply_patch(self) -> bool:
        return (not self.require_confirmation) or self.approved
