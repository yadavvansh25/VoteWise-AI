import logging
import os
from typing import Optional
from google.cloud import storage

logger = logging.getLogger("votewise.storage")

class GoogleStorageService:
    """Service to handle document storage with Google Cloud Storage."""
    
    def __init__(self):
        self.bucket_name = os.getenv("GCP_STORAGE_BUCKET")
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self._client: Optional[storage.Client] = None

    @property
    def client(self) -> storage.Client:
        if self._client is None:
            try:
                self._client = storage.Client(project=self.project_id)
            except Exception as e:
                logger.warning(f"Storage client initialization failed: {e}")
                raise e
        return self._client

    def get_form_url(self, form_id: str) -> str:
        """
        Returns a public or signed URL for an official election form.
        Helps citizens download Form 6, 8, etc.
        """
        if not self.bucket_name:
            # Fallback to public ECI links if bucket not configured
            fallback_map = {
                "form6": "https://voters.eci.gov.in/download-forms?form=form6",
                "form8": "https://voters.eci.gov.in/download-forms?form=form8"
            }
            return fallback_map.get(form_id, "https://voters.eci.gov.in/")
            
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(f"forms/{form_id}.pdf")
            if blob.exists():
                return blob.public_url
            return f"https://voters.eci.gov.in/download-forms?form={form_id}"
        except Exception as e:
            logger.error(f"GCS error: {e}")
            return "https://voters.eci.gov.in/"

storage_service = GoogleStorageService()
