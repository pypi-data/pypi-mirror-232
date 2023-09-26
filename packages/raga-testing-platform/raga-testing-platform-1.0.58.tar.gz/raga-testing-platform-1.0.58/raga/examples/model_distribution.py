import ast
import pandas as pd
import json

from raga import *

import datetime

def get_timestamp_x_hours_ago(hours):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(days=90, hours=hours)
    past_time = current_time - delta
    timestamp = int(past_time.timestamp())
    return timestamp

def img_url(x):
    return StringElement(f"https://raga-test-bucket.s3.ap-south-1.amazonaws.com/spoof/{x}")

def model_a_inference(row):
    classification = ImageClassificationElement()
    try:
        confidence = ast.literal_eval(row['ModelA Inference'])
        classification.add("live", confidence.get('live'))
    except Exception:
        classification.add("live", 0)
    return classification


def model_b_inference(row):
    classification = ImageClassificationElement()
    try:
        confidence = ast.literal_eval(row['ModelB Inference'])
        classification.add("live", confidence.get('live'))
    except Exception:
        classification.add("live", 0)
    return classification


def model_gt_inference(row):
    classification = ImageClassificationElement()
    try:
        confidence = ast.literal_eval(row['Ground Truth'])
        classification.add("live", confidence.get('live'))
    except Exception:
        classification.add("live", 0)
    return classification

def image_vectors_m1(row):
    image_vectors = ImageEmbedding()
    for embedding in json.loads(row['ImageVectorsM1']):
        image_vectors.add(Embedding(embedding))
    return image_vectors


def csv_parser(csv_file):
    df = pd.read_csv(csv_file).head(1)
    data_frame = pd.DataFrame()
    data_frame["ImageId"] = df["ImageId"].apply(lambda x: StringElement(x))
    data_frame["ImageUri"] = df["ImageId"].apply(lambda x: img_url(x))
    data_frame["TimeOfCapture"] = df.apply(lambda row: TimeStampElement(get_timestamp_x_hours_ago(row.name)), axis=1)
    data_frame["Reflection"] = df.apply(lambda row: StringElement("Yes"), axis=1)
    data_frame["Overlap"] = df.apply(lambda row: StringElement("No"), axis=1)
    data_frame["CameraAngle"] = df.apply(lambda row: StringElement("Yes"), axis=1)
    data_frame["SourceLink"] = df["SourceLink"].apply(lambda x: StringElement(f"/Users/manabroy/Downloads/retail dataset/spoof/{x.split('/')[-1]}"))
    data_frame["ModelA Inference"] = df.apply(model_a_inference, axis=1)
    data_frame["ModelB Inference"] = df.apply(model_b_inference, axis=1)
    data_frame["Ground Truth"] = df.apply(model_gt_inference, axis=1)
    data_frame["ImageVectorsM1"] =  df.apply(image_vectors_m1, axis=1)
    return data_frame


raga_data_frame = csv_parser("./assets/signzy_df.csv")


schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())

run_name = f"model_distribution-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"


test_session = TestSession(project_name="testingProject", run_name= run_name)

cred = DatasetCreds(arn="arn:aws:iam::527593518644:role/model-distribution")

raga_dataset = Dataset(test_session=test_session, 
                       name="md-fast-v2", 
                       data=raga_data_frame, 
                       schema=schema, 
                       creds=cred)
raga_dataset.load()


model_exe_fun = ModelExecutorFactory().get_model_executor(test_session=test_session, 
                                                          model_name="Signzy Embedding Model", 
                                                          version="0.1.9")

model_exe_fun.execute(init_args={"device": "cpu"}, 
                           execution_args={"input_columns":{"img_paths":"ImageUri"}, 
                                           "output_columns":{"embedding":"ImageEmbedding"},
                                           "column_schemas":{"embedding":ImageEmbeddingSchemaElement(model="Signzy Embedding Model")}}, 
                           data_frame=raga_dataset)

raga_dataset.load()