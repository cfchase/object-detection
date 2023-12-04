import kfp
from kfp.components import create_component_from_func

from kubernetes.client.models import *
import os

from data_ingestion import ingest_data
from preprocessing import preprocess_data
from model_training import train_model
from model_conversion import convert_model
from model_upload import upload_model


data_ingestion_component = create_component_from_func(
    ingest_data,
    base_image="quay.io/modh/runtime-images:runtime-pytorch-ubi9-python-3.9-2023b-20231116",
    packages_to_install=[]
)

preprocessing_component = create_component_from_func(
    preprocess_data,
    base_image="quay.io/modh/runtime-images:runtime-pytorch-ubi9-python-3.9-2023b-20231116",
    packages_to_install=[]
)

model_training_component = create_component_from_func(
    train_model,
    base_image="quay.io/modh/runtime-images:runtime-pytorch-ubi9-python-3.9-2023b-20231116",
    packages_to_install=[]
)

model_conversion_component = create_component_from_func(
    convert_model,
    base_image="quay.io/modh/runtime-images:runtime-pytorch-ubi9-python-3.9-2023b-20231116",
    packages_to_install=[]
)

model_upload_component = create_component_from_func(
    upload_model,
    base_image="quay.io/modh/runtime-images:runtime-pytorch-ubi9-python-3.9-2023b-20231116",
    packages_to_install=["boto3", "botocore"]
)


@kfp.dsl.pipeline(name="model_training_pipeline_kfp")
def sdk_pipeline():
    data_ingestion_component_task = data_ingestion_component()
    preprocessing_task = preprocessing_component()
    model_training_task = model_training_component()
    model_conversion_task = model_conversion_component()
    model_upload_task = model_upload_component()

    preprocessing_task.after(data_ingestion_component_task)
    model_training_task.after(preprocessing_task)
    model_conversion_task.after(model_training_task)
    model_upload_task.after(model_conversion_task)

    # model_upload_task.add_env_variable(V1EnvVar(
    #     name="S3_KEY",
    #     value="models/object-detection/model.onnx"))
    #
    # model_upload_task.container.add_env_from(
    #     V1EnvFromSource(
    #         secret_ref=V1SecretReference(
    #             name="aws-connection-my-storage"
    #         )
    #     )
    # )

from kfp_tekton.compiler import TektonCompiler


# DEFAULT_STORAGE_CLASS needs to be filled out with the correct storage class, or else it will default to kfp-csi-s3
os.environ["DEFAULT_STORAGE_CLASS"] = os.environ.get(
    "DEFAULT_STORAGE_CLASS", "gp3"
)
os.environ["DEFAULT_ACCESSMODES"] = os.environ.get(
    "DEFAULT_ACCESSMODES", "ReadWriteOnce"
)
TektonCompiler().compile(sdk_pipeline, __file__.replace(".py", ".yaml"))
