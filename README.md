# bouncelayer (Python SDK)

Official Python library for [BounceLayer](https://bouncelayer.com) — real-time email verification with direct TCP port 25 SMTP handshakes.

## Installation

```bash
pip install bouncelayer
```

## Quickstart

```python
from bouncelayer import BounceLayer
import os

client = BounceLayer(api_key=os.environ.get("BOUNCELAYER_API_KEY"))

# Single real-time verification (<150ms)
result = client.verify.single("alex@stripe.com")

print(result.status)            # "valid"
print(result.confidence_score)  # 98
print(result.is_disposable)     # False
print(result.smtp_checked)      # True
```

## Bulk Verification

```python
# Submit a list of up to 10,000 addresses
job = client.verify.bulk([
    "sarah@linear.app",
    "john@workmail.com",
    "disposable@burner.org"
], webhook_url="https://api.myapp.com/webhooks/bouncelayer")

# Wait for job completion automatically
completed = client.verify.wait_for_job(job["job_id"])
print(f"Valid: {completed.valid_count}, Invalid: {completed.invalid_count}")
```

## Webhook Verification (Flask / FastAPI)

```python
from bouncelayer import BounceLayer

# In your webhook route
is_valid = BounceLayer.verify_webhook_signature(
    raw_body_bytes,
    request.headers.get("X-BounceLayer-Signature"),
    secret="whsec_..."
)
```

## License
MIT
