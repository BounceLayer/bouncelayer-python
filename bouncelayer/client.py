import os
import time
import hmac
import hashlib
import json
from typing import List, Optional, Dict, Any, Union
import urllib.request
import urllib.error

from .exceptions import (
    BounceLayerError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
)
from .models import VerificationResult, BulkJobStatus


class BounceLayer:
    """Official Python Client for BounceLayer API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.bouncelayer.com/v1",
        timeout: int = 30,
    ):
        self.api_key = api_key or os.environ.get("BOUNCELAYER_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "Missing BounceLayer API key. Pass BounceLayer(api_key='bl_live_...') "
                "or set BOUNCELAYER_API_KEY environment variable."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        if params:
            query = urllib.parse.urlencode(params)
            url = f"{url}?{query}"

        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "BounceLayer-Python-SDK/1.0.0",
        }

        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8")
            try:
                err_json = json.loads(err_body)
            except Exception:
                err_json = {"detail": err_body or err.reason}

            msg = err_json.get("detail") or err_json.get("message") or str(err)

            if err.code == 401:
                raise AuthenticationError(msg, err.code, err_json)
            elif err.code == 402:
                raise InsufficientCreditsError(msg, err.code, err_json)
            elif err.code == 429:
                raise RateLimitError(msg, err.code, err_json)
            else:
                raise BounceLayerError(msg, err.code, err_json)
        except Exception as e:
            raise BounceLayerError(f"Request failed: {str(e)}")

    class _Verify:
        def __init__(self, client: "BounceLayer"):
            self._client = client

        def single(self, email: str) -> VerificationResult:
            """Verify a single email address in real-time across 7 layers."""
            res = self._client._request(
                "POST", "/verify/single", data={"email": email.strip().lower()}
            )
            return VerificationResult.from_dict(res.get("result", {}))

        def bulk(
            self, emails: List[str], webhook_url: Optional[str] = None
        ) -> dict:
            """Submit a list of up to 10,000 email addresses for async bulk verification."""
            payload = {"emails": emails}
            if webhook_url:
                payload["webhook_url"] = webhook_url
            return self._client._request("POST", "/verify/bulk", data=payload)

        def get_job(self, job_id: str) -> BulkJobStatus:
            """Fetch status and results of a bulk verification job."""
            res = self._client._request("GET", f"/verify/bulk/{job_id}")
            return BulkJobStatus.from_dict(res)

        def wait_for_job(
            self,
            job_id: str,
            interval: float = 2.0,
            max_wait: float = 120.0,
        ) -> BulkJobStatus:
            """Poll until a bulk job is completed or cancelled."""
            start_time = time.time()
            while time.time() - start_time < max_wait:
                job = self.get_job(job_id)
                if job.status in ("completed", "cancelled", "failed"):
                    return job
                time.sleep(interval)
            raise BounceLayerError(f"Job {job_id} timed out after {max_wait}s")

        def cancel_job(self, job_id: str) -> dict:
            """Cancel a pending bulk job and release reserved credits."""
            return self._client._request("DELETE", f"/verify/bulk/{job_id}")

    class _Credits:
        def __init__(self, client: "BounceLayer"):
            self._client = client

        def get(self) -> dict:
            """Return current credit balance and account telemetry."""
            return self._client._request("GET", "/credits")

    class _Intelligence:
        def __init__(self, client: "BounceLayer"):
            self._client = client

        def analyze_risk(self, email_or_domain: str) -> dict:
            """Analyze threat and disposable domain risk signals."""
            key = "email" if "@" in email_or_domain else "domain"
            return self._client._request("GET", f"/intelligence/risk?{key}={email_or_domain}")

    @property
    def verify(self) -> _Verify:
        return self._Verify(self)

    @property
    def credits(self) -> _Credits:
        return self._Credits(self)

    @property
    def intelligence(self) -> _Intelligence:
        return self._Intelligence(self)

    @staticmethod
    def verify_webhook_signature(
        payload: Union[str, bytes], signature_header: str, secret: str
    ) -> bool:
        """Verify HMAC-SHA256 signature from BounceLayer webhooks."""
        if not payload or not signature_header or not secret:
            return False
        try:
            body = payload.encode("utf-8") if isinstance(payload, str) else payload
            expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
            given = signature_header.replace("sha256=", "").strip()
            return hmac.compare_digest(expected, given)
        except Exception:
            return False
