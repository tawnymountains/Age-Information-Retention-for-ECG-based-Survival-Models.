"""Public reference utilities, not the private experiment runner."""
from .metrics import global_age_r2, km_event_risk, subgroup_error, rank_agreement
from .probing import crossfit_age
from .selection import select_encoder

__version__ = "0.2.0"
__all__ = ["global_age_r2", "km_event_risk", "subgroup_error", "rank_agreement", "crossfit_age", "select_encoder"]
