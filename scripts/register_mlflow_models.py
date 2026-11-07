import os

import mlflow
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException


TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/abdul-raheem-fast/23L-0588_A2_Ops.mlflow")
MODEL_NAME = os.getenv("MLFLOW_REGISTERED_MODEL", "visionguard-model")
CHAMPION_RUN_ID = os.getenv("MLFLOW_CHAMPION_RUN_ID", "584d945083d141ef8292008a367041f7")
SECOND_RUN_ID = os.getenv("MLFLOW_SECOND_RUN_ID", "f0e134a389aa410f891c4ce190f74988")


def register_version(client, run_id):
    source = f"runs:/{run_id}/model"
    return client.create_model_version(name=MODEL_NAME, source=source, run_id=run_id)


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    client = MlflowClient(TRACKING_URI)
    try:
        client.get_registered_model(MODEL_NAME)
    except MlflowException as error:
        if error.error_code != "RESOURCE_DOES_NOT_EXIST":
            raise
        client.create_registered_model(MODEL_NAME)

    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    if not any(version.run_id == SECOND_RUN_ID for version in versions):
        register_version(client, SECOND_RUN_ID)
    versions = client.search_model_versions(f"name='{MODEL_NAME}'")
    champion = next((version for version in versions if version.run_id == CHAMPION_RUN_ID), None)
    if champion is None:
        champion = register_version(client, CHAMPION_RUN_ID)
    client.set_registered_model_alias(MODEL_NAME, "champion", champion.version)
    print(f"{MODEL_NAME}: champion -> version {champion.version}")


if __name__ == "__main__":
    main()
