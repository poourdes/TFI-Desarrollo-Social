from dataclasses import dataclass

from app.models.enums import CaseEventType
from app.schemas.area_config import AreaConfig


@dataclass(frozen=True)
class EscalationSuggestion:
    event_type: CaseEventType
    public_message: str


def evaluate_escalation(
    config: AreaConfig, report_count: int
) -> list[EscalationSuggestion]:
    escalation = config.escalation
    if escalation is None or report_count < 1:
        return []

    suggestions: list[EscalationSuggestion] = []
    if (
        escalation.visit_after_reports is not None
        and report_count == escalation.visit_after_reports
    ):
        suggestions.append(
            EscalationSuggestion(
                event_type=CaseEventType.visit_due,
                public_message="Se sugiere programar una visita domiciliaria.",
            )
        )
    if (
        escalation.alert_threshold is not None
        and report_count == escalation.alert_threshold
    ):
        suggestions.append(
            EscalationSuggestion(
                event_type=CaseEventType.escalation_suggested,
                public_message=(
                    "Se sugiere escalar el caso a la policía; "
                    "requiere confirmación de una persona del equipo."
                ),
            )
        )
    return suggestions
