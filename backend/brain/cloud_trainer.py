import os
import logging
from google.cloud import aiplatform
from typing import Dict, Any

logger = logging.getLogger(__name__)

class VertexTrainer:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.staging_bucket = f"gs://{project_id}-omnitrade-staging"
        
        try:
            aiplatform.init(project=project_id, location=location, staging_bucket=self.staging_bucket)
            logger.info(f"Vertex AI initialized for project {project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")

    def submit_job(self, model_id: str, config: Dict[str, Any]) -> str:
        """
        Submits a Custom Training Job to Vertex AI.
        """
        try:
            job_name = f"omnitrade-train-{model_id}"
            
            # Define the Custom Training Job
            job = aiplatform.CustomTrainingJob(
                display_name=job_name,
                script_path="backend/brain/models/lstm_price.py", # The training script
                container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-13:latest",
                requirements=["pandas", "numpy", "google-cloud-storage"],
                model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-13:latest",
            )

            # Run the job
            # Note: In a real async app, we might want to run this in a background thread or use the async client
            # For this 'God-Tier' architecture, we'll assume this is triggered via an API endpoint
            logger.info(f"Submitting job {job_name} to Vertex AI...")
            
            model = job.run(
                machine_type="n1-standard-4",
                accelerator_type="NVIDIA_TESLA_T4",
                accelerator_count=1,
                args=[f"--epochs={config.get('epochs', 10)}", f"--batch_size={config.get('batch_size', 32)}"],
                sync=False # Return immediately
            )
            
            return job.resource_name
            
        except Exception as e:
            logger.error(f"Failed to submit Vertex AI job: {e}")
            return "ERROR"

    def get_job_status(self, job_id: str) -> str:
        try:
            job = aiplatform.CustomTrainingJob.get(resource_name=job_id)
            return job.state.name
        except Exception as e:
            logger.error(f"Failed to get job status: {e}")
            return "UNKNOWN"
