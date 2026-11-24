from enum import StrEnum


class ReportCategory(StrEnum):
    abuse = "abuse"
    neglect = "neglect"
    abandonment = "abandonment"
    other = "other"


class AgeRange(StrEnum):
    range_60_69 = "range_60_69"
    range_70_79 = "range_70_79"
    range_80_plus = "range_80_plus"
    unknown = "unknown"


class CaseStatus(StrEnum):
    open = "open"
    in_review = "in_review"
    closed = "closed"


class ReportStatus(StrEnum):
    received = "received"
    linked = "linked"
    in_review = "in_review"
    closed = "closed"


class CaseEventType(StrEnum):
    report_received = "report_received"
    report_linked = "report_linked"
    visit_due = "visit_due"
    escalation_suggested = "escalation_suggested"


class StaffRole(StrEnum):
    admin = "admin"
    coordinator = "coordinador"
    social_worker = "trabajador_social"


class AuditAction(StrEnum):
    report_created = "report_created"
    escalation_suggested = "escalation_suggested"
    case_status_changed = "case_status_changed"
    area_access_denied = "area_access_denied"
