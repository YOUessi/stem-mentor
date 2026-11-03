"""Fail-closed external, RSA-SHA256 reviewer attestations for authored lesson versions.

This verifier DOES NOT authenticate humans or perform mathematical proof review.
It only checks signatures against externally provisioned reviewer public keys.
No keys or attestations are accepted from repository-local files. An operator
must supply a separately protected key trust store and review ledger. These
prerequisites are NOT present in project source, thus default is always no
student evidence. Signed test fixtures are not evidence of teacher approval.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .deep_knowledge import ROOT, lessons

_SAFE_ID = re.compile(r"^[a-z0-9._-]{3,100}$")
_REQUIRED_PAYLOAD = frozenset({
    "knowledge_id", "content_sha256", "version",
    "reviewer_id", "key_id", "issued_at", "decision",
})


def lesson_digest(doc) -> str:
    """Hash every lesson field: even a corrected boundary invalidates approval."""
    canonical = json.dumps(doc.model_dump(mode="json"), sort_keys=True,
                           ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def _external_file(key: str) -> Path | None:
    value = os.environ.get(key, "")
    if not value:
        return None
    p = Path(value)
    if not p.is_absolute() or p.is_symlink():
        return None
    try:
        resolved = p.resolve(strict=True)
        resolved.relative_to(ROOT.resolve())
        return None                         # no author-controlled project files
    except ValueError:                     # not nested in repository: expected
        pass
    except (OSError, RuntimeError):
        return None
    if not resolved.is_file() or resolved.is_symlink():
        return None
    # Reject ANY git worktree path (including sibling project worktrees), not
    # merely the current one. Reviewer trust must be externally administered.
    if any((parent / ".git").exists() for parent in (resolved.parent, *resolved.parents)):
        return None
    # Writable trust metadata lets an unprivileged group member forge release
    # changes; require owner-only write permissions on both external files.
    try:
        if resolved.stat().st_mode & 0o022:
            return None
    except OSError:
        return None
    return resolved


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return None


def _signature_valid(public_key_pem: str, message: bytes, signature_b64: str) -> bool:
    binary = shutil.which("openssl")
    if not binary or "PRIVATE KEY" in public_key_pem:
        return False
    try:
        sig = base64.b64decode(signature_b64, validate=True)
        if len(sig) < 128 or len(sig) > 1024 or len(message) > 1600:
            return False
        with tempfile.TemporaryDirectory(prefix="stem-review-") as tmp:
            key, data, signature = (Path(tmp) / name for name in ("pub.pem", "payload.json", "signature"))
            key.write_text(public_key_pem, encoding="utf-8")
            data.write_bytes(message)
            signature.write_bytes(sig)
            result = subprocess.run(
                [binary, "dgst", "-sha256", "-verify", str(key),
                 "-signature", str(signature), str(data)],
                capture_output=True, check=False, timeout=4,
            )
            return result.returncode == 0 and b"Verified OK" in result.stdout
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def approved_lesson_ids() -> frozenset[str]:
    """Only externally attested exact versions may enter student RAG.

    On any ambiguous, missing, tampered or malformed metadata the whole release
    is disabled. Does not change authored REVIEW_PENDING statuses or imply that
    sample credentials can represent an actual teacher.
    """
    if os.environ.get("STEM_MENTOR_ENABLE_APPROVED_RAG") != "1":
        return frozenset()
    trust_path = _external_file("STEM_MENTOR_TRUSTED_REVIEWERS_PATH")
    ledger_path = _external_file("STEM_MENTOR_REVIEW_ATTESTATIONS_PATH")
    if trust_path is None or ledger_path is None:
        return frozenset()
    keys = _load_json(trust_path)
    ledger = _load_json(ledger_path)
    if (not isinstance(keys, dict) or not isinstance(keys.get("reviewers"), list)
            or not isinstance(ledger, dict) or not isinstance(ledger.get("attestations"), list)):
        return frozenset()
    try:
        refs = {}
        for row in keys["reviewers"]:
            if not isinstance(row, dict) or set(row) != {
                "reviewer_id", "key_id", "public_key_pem", "active", "role",
            }:
                return frozenset()
            rid, kid = row["reviewer_id"], row["key_id"]
            if (not isinstance(rid, str) or not isinstance(kid, str)
                    or not _SAFE_ID.fullmatch(rid) or not _SAFE_ID.fullmatch(kid)
                    or row["role"] != "MATH_TEACHER" or type(row["active"]) is not bool
                    or (rid, kid) in refs):
                return frozenset()
            refs[(rid, kid)] = row
        docs = {x.id: x for x in lessons()}
        votes = {}
        for att in ledger["attestations"]:
            if not isinstance(att, dict) or set(att) != {"payload", "signature_base64"}:
                return frozenset()
            payload = att["payload"]
            if not isinstance(payload, dict) or set(payload) != _REQUIRED_PAYLOAD:
                return frozenset()
            lesson_id, reviewer, key_id = (payload[x] for x in ("knowledge_id", "reviewer_id", "key_id"))
            if (not all(isinstance(v, str) for v in payload.values())
                    or lesson_id not in docs
                    or not _SAFE_ID.fullmatch(reviewer) or not _SAFE_ID.fullmatch(key_id)
                    or payload["decision"] not in ("APPROVE", "REVOKE")
                    or not re.fullmatch("[0-9a-f]{64}", payload["content_sha256"])):
                return frozenset()
            doc = docs[lesson_id]
            if payload["content_sha256"] != lesson_digest(doc) or payload["version"] != doc.version:
                return frozenset()       # stale or altered version; fail entire release
            ref = refs.get((reviewer, key_id))
            if not ref or not ref["active"]:
                return frozenset()
            try:
                t = datetime.fromisoformat(payload["issued_at"])
                if t.tzinfo is None or t > datetime.now(timezone.utc):
                    return frozenset()
            except (ValueError, TypeError, OverflowError):
                return frozenset()
            if not _signature_valid(ref["public_key_pem"], _canonical(payload), att["signature_base64"]):
                return frozenset()
            key = (lesson_id, reviewer)
            if key in votes:             # ambiguous duplicate/revocation ordering: fail closed
                return frozenset()
            votes[key] = payload["decision"]
        # Two distinct teacher keys are required per exact version.
        return frozenset(k for k in docs if sum(
            1 for (lesson_id, _), decision in votes.items()
            if lesson_id == k and decision == "APPROVE"
        ) >= 2)
    except (KeyError, TypeError, ValueError, OSError, AttributeError):
        return frozenset()
