from dataclasses import dataclass
from typing import List, Optional, Any, Dict


@dataclass
class MXRecord:
    priority: int
    host: str = ""


@dataclass
class VerificationResult:
    email: str
    status: str
    is_valid: bool
    syntax_valid: bool
    domain: str
    domain_valid: bool
    has_mx: bool
    is_disposable: bool
    is_role_based: bool
    is_catch_all: bool
    is_free_provider: bool
    confidence_score: int
    status_reason: str
    provider: str
    verification_time_ms: int
    cached: bool
    smtp_checked: bool = True
    smtp_response_code: Optional[int] = None
    mx_records: Optional[List[Dict[str, Any]]] = None
    # Suggested fix for a mistyped domain ("lead@gmail.com" for "lead@gmial.com"). Never changes status.
    did_you_mean: Optional[str] = None
    # Plain-English reason, e.g. "The mail server said this mailbox doesn't exist (550)."
    explanation: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "VerificationResult":
        return cls(
            email=data.get("email", ""),
            status=data.get("status", "unknown"),
            is_valid=data.get("is_valid", False),
            syntax_valid=data.get("syntax_valid", False),
            domain=data.get("domain", ""),
            domain_valid=data.get("domain_valid", False),
            has_mx=data.get("has_mx", False),
            is_disposable=data.get("is_disposable", False),
            is_role_based=data.get("is_role_based", False),
            is_catch_all=data.get("is_catch_all", False),
            is_free_provider=data.get("is_free_provider", False),
            confidence_score=data.get("confidence_score", 0),
            status_reason=data.get("status_reason", ""),
            provider=data.get("provider", "unknown"),
            verification_time_ms=data.get("verification_time_ms", 0),
            cached=data.get("cached", False),
            smtp_checked=data.get("smtp_checked", True),
            smtp_response_code=data.get("smtp_response_code"),
            mx_records=data.get("mx_records"),
            did_you_mean=data.get("did_you_mean"),
            explanation=data.get("explanation"),
        )


@dataclass
class BulkJobStatus:
    job_id: str
    status: str
    total_emails: int
    processed_emails: int
    valid_count: int
    invalid_count: int
    credits_used: int
    created_at: str
    completed_at: Optional[str] = None
    results: Optional[List[dict]] = None

    @classmethod
    def from_dict(cls, data: dict) -> "BulkJobStatus":
        return cls(
            job_id=data.get("job_id", ""),
            status=data.get("status", "pending"),
            total_emails=data.get("total_emails", 0),
            processed_emails=data.get("processed_emails", 0),
            valid_count=data.get("valid_count", 0),
            invalid_count=data.get("invalid_count", 0),
            credits_used=data.get("credits_used", 0),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at"),
            results=data.get("results"),
        )
