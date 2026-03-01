"""
Google Cloud authentication helpers.

Supports two modes:
  1. Local dev  → GOOGLE_SERVICE_ACCOUNT_KEY_PATH points to a JSON key file.
  2. Cloud Run  → Application Default Credentials (ADC) provided automatically
                  by the attached service-account identity.
"""

from __future__ import annotations

import logging
import os

from google.auth import default as google_auth_default
from google.auth.credentials import Credentials
from google.oauth2 import service_account

logger = logging.getLogger(__name__)

# Read + write access (we need to append to the knowledge graph)
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive.readonly",
]


def build_credentials() -> Credentials:
    """Return scoped Google credentials.

    Resolution order:
      Use Application Default Credentials (ADC).
         On Cloud Run this uses the service-account bound to the revision.
    """

    logger.info("Authenticating via Application Default Credentials (ADC)")
    creds, _project = google_auth_default(scopes=SCOPES)

    return creds
