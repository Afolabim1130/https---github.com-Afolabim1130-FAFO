"""FAFO Role Definitions and Permission Mappings"""
from enum import Enum
from typing import Dict, List

class Role(Enum):
    SUBMITTER = "submitter"
    REVIEWER = "reviewer"
    LAWYER = "lawyer"
    ADMIN = "admin"

class Permissions:
    INCIDENT_CREATE = "incident:create"
    INCIDENT_READ = "incident:read"
    INCIDENT_UPDATE = "incident:update"
    INCIDENT_DELETE = "incident:delete"
    INCIDENT_APPROVE = "incident:approve"
    EVIDENCE_UPLOAD = "evidence:upload"
    EVIDENCE_READ = "evidence:read"
    EVIDENCE_DELETE = "evidence:delete"
    EVIDENCE_VERIFY = "evidence:verify"
    AUDIT_READ = "audit:read"
    USER_MANAGE = "user:manage"
    CONFIG_MANAGE = "config:manage"
    EXPORT_CREATE = "export:create"
    EXPORT_DOWNLOAD = "export:download"

ROLE_PERMISSIONS: Dict[Role, List[str]] = {
    Role.SUBMITTER: [
        Permissions.INCIDENT_CREATE,
        Permissions.INCIDENT_READ,
        Permissions.EVIDENCE_UPLOAD,
        Permissions.EVIDENCE_READ,
        Permissions.EXPORT_DOWNLOAD,
    ],
    Role.REVIEWER: [
        Permissions.INCIDENT_CREATE,
        Permissions.INCIDENT_READ,
        Permissions.INCIDENT_UPDATE,
        Permissions.INCIDENT_APPROVE,
        Permissions.EVIDENCE_UPLOAD,
        Permissions.EVIDENCE_READ,
        Permissions.EVIDENCE_VERIFY,
        Permissions.EXPORT_CREATE,
        Permissions.EXPORT_DOWNLOAD,
        Permissions.AUDIT_READ,
    ],
    Role.LAWYER: [
        Permissions.INCIDENT_READ,
        Permissions.EVIDENCE_READ,
        Permissions.EVIDENCE_VERIFY,
        Permissions.EXPORT_DOWNLOAD,
        Permissions.AUDIT_READ,
    ],
    Role.ADMIN: [
        Permissions.INCIDENT_CREATE,
        Permissions.INCIDENT_READ,
        Permissions.INCIDENT_UPDATE,
        Permissions.INCIDENT_DELETE,
        Permissions.INCIDENT_APPROVE,
        Permissions.EVIDENCE_UPLOAD,
        Permissions.EVIDENCE_READ,
        Permissions.EVIDENCE_DELETE,
        Permissions.EVIDENCE_VERIFY,
        Permissions.AUDIT_READ,
        Permissions.USER_MANAGE,
        Permissions.CONFIG_MANAGE,
        Permissions.EXPORT_CREATE,
        Permissions.EXPORT_DOWNLOAD,
    ]
}

DEFAULT_USERS = {
    "submitter": {"email": "submitter@fafo.local", "role": Role.SUBMITTER},
    "reviewer": {"email": "reviewer@fafo.local", "role": Role.REVIEWER},
    "lawyer": {"email": "lawyer@fafo.local", "role": Role.LAWYER},
    "admin": {"email": "admin@fafo.local", "role": Role.ADMIN},
}

DEFAULT_PASSWORDS = {
    "submitter": "Submitter@123",
    "reviewer": "Reviewer@123",
    "lawyer": "Lawyer@123",
    "admin": "Admin@123",
}

def has_permission(role: Role, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])

def get_role_permissions(role: Role) -> List[str]:
    return ROLE_PERMISSIONS.get(role, [])
