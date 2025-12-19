from __future__ import annotations

from google.cloud import secretmanager


class SecretStore:
    """
    Minimal Secret Manager wrapper.

    - read(secret_id): reads latest secret value
    - write_new_version(secret_id, value): creates a new version (rotation-friendly)
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = secretmanager.SecretManagerServiceClient()

    def read(self, secret_id: str, version_id: str = "latest") -> str:
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        resp = self.client.access_secret_version(request={"name": name})
        return resp.payload.data.decode("utf-8")

    def write_new_version(self, secret_id: str, value: str) -> None:
        parent = f"projects/{self.project_id}/secrets/{secret_id}"
        self.client.add_secret_version(
            request={"parent": parent, "payload": {"data": value.encode("utf-8")}}
        )
