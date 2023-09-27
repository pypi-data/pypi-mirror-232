import pathlib
import re
from raga import *
import pandas as pd
import datetime

def get_timestamp_x_hours_ago(hours):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(days=90, hours=hours)
    past_time = current_time - delta
    timestamp = int(past_time.timestamp())
    return timestamp

def img_url(x):
    parts = x.split("-")
    parts.pop()
    video = "-".join(parts)
    return StringElement(f"https://ragamediatest.s3.ap-south-1.amazonaws.com/1/Hb%2Cjson/data_points/{video}/{x}")

def annotation_v1(row):
    AnnotationsV1 = ImageDetectionObject()
    for detection in row["AnnotationsV1"]:
        AnnotationsV1.add(ObjectDetection(Id=detection['Id'], ClassId=detection['ClassId'], ClassName=detection['ClassName'], Confidence=detection['Confidence'], BBox= detection['BBox'], Format="xywh_normalized"))
    return AnnotationsV1

def model_inferences(row):
    ModelInferences = ImageDetectionObject()
    for detection in row["ModelInferences"]:
        ModelInferences.add(ObjectDetection(Id=detection['Id'], ClassId=detection['ClassId'], ClassName=detection['ClassName'], Confidence=detection['Confidence'], BBox= detection['BBox'], Format="xywh_normalized"))
    return ModelInferences

def imag_vectors_m1(row):
    ImageVectorsM1 = ImageEmbedding()
    for embedding in row["ImageVectorsM1"]:
        ImageVectorsM1.add(Embedding(embedding))
    return ImageVectorsM1

def roi_vectors_m1(row):
    ROIVectorsM1 = ROIEmbedding()
    for embedding in row["ROIVectorsM1"]:
        ROIVectorsM1.add(id=embedding.get("Id"), embedding_values=embedding.get("embedding"))
    return ROIVectorsM1

def json_parser(json_file):
    df = pd.read_json(json_file).head(1000)
    print(df.columns.to_list())
    data_frame = pd.DataFrame()
    data_frame["ImageId"] = df["ImageId"].apply(lambda x: StringElement(x))
    data_frame["ImageUri"] = df["ImageId"].apply(lambda x: img_url(x))
    data_frame["SourceLink"] = df["ImageId"].apply(lambda x: StringElement(x))
    data_frame["TimeOfCapture"] = df.apply(lambda row: TimeStampElement(get_timestamp_x_hours_ago(row.name)), axis=1)
    data_frame["weather"] = df["weather"].apply(lambda x: StringElement(x))
    data_frame["time_of_day"] = df["time_of_day"].apply(lambda x: StringElement(x))
    data_frame["scene"] = df["scene"].apply(lambda x: StringElement(x))
    data_frame["ModelA"] = df.apply(annotation_v1, axis=1)
    data_frame["ModelB"] = df.apply(model_inferences, axis=1)
    data_frame["ImageVectorsM1"] = df.apply(imag_vectors_m1, axis=1)
    # data_frame["ROIVectorsM1"] = df.apply(roi_vectors_m1, axis=1)
    return data_frame

pd_data_frame = json_parser("./assets/resultframe.json")

#### Want to see in csv file uncomment line below ####
# data_frame_extractor(pd_data_frame).to_csv("./assets/resultframe_100.csv", index=False)

schema = RagaSchema()
schema.add("ImageId", PredictionSchemaElement())
schema.add("ImageUri", ImageUriSchemaElement())
schema.add("TimeOfCapture", TimeOfCaptureSchemaElement())
schema.add("SourceLink", FeatureSchemaElement())
schema.add("weather", AttributeSchemaElement())
schema.add("time_of_day", AttributeSchemaElement())
schema.add("scene", AttributeSchemaElement())
schema.add("ModelA", InferenceSchemaElement(model="ModelA"))
schema.add("ModelB", InferenceSchemaElement(model="ModelB"))
# schema.add("ROIVectorsM1", RoiEmbeddingSchemaElement(model="ROIModel"))
schema.add("ImageVectorsM1", ImageEmbeddingSchemaElement(model="imageModel"))

run_name = f"lm_image_loader_failure_mode_analysis-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

# create test_session object of TestSession instance
test_session = TestSession(project_name="testingProject", run_name= run_name, access_key="LGXJjQFD899MtVSrNHGH", secret_key="TC466Qu9PhpOjTuLu5aGkXyGbM7SSBeAzYH6HpcP", host="http://3.111.106.226:8080")

creds = DatasetCreds(arn="arn:aws:iam::596708924737:role/test-s3")
#create test_ds object of Dataset instance
test_ds = Dataset(test_session=test_session, 
                  name="lm-hb-image-ds-v3", 
                  type=DATASET_TYPE.IMAGE,
                  data=pd_data_frame, 
                  schema=schema, 
                  creds=creds, 
                  parent_dataset="lm-hb-video-ds-v3")

#load schema and pandas data frame
test_ds.load()