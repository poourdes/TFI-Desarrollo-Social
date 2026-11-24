from app.models.enums import CaseStatus
from app.schemas.area_config import AreaConfig


class InvalidTransitionError(ValueError):
    pass


def assert_transition_allowed(
    config: AreaConfig, current: CaseStatus, target: CaseStatus
) -> None:
    allowed = config.workflow.transitions.get(current, [])
    if target not in allowed:
        raise InvalidTransitionError(
            f"Transición no permitida: {current.value} -> {target.value}"
        )
