#-jc dispatcher app smoke test

import io

from dispatcher.src.app import app


def test_categorize_endpoint_exists():
    client = app.test_client()

    resp = client.post(
        "/categorize",
        data={"file": (io.BytesIO(b"fake"), "test.jpg")},
        content_type="multipart/form-data",
    )

    # We only assert the contract shape, not async completion
    assert resp.status_code in (200, 400)

