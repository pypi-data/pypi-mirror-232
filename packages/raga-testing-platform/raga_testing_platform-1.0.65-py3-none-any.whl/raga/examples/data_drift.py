from raga import *
import datetime


rules = DriftDetectionRules()
rules.add(type="anomaly_detection", dist_metric="Mahalanobis", _class="ALL", threshold=0.6)

edge_case_detection = data_drift_detection(test_session=test_session,
                                           test_name="Drift-detection-test",
                                           train_dataset_name="automobile_dataset_train",
                                           field_dataset_name="automobile_dataset_field",
                                           train_embed_col_name="ImageEmbedding",
                                           field_embed_col_name = "ImageEmbedding" ,
                                           level = "image",
                                           aggregation_level=["location", "vehicle_no", "channel"],
                                           rules = rules)

# add payload into test_session object
test_session.add(edge_case_detection)
#run added test
test_session.run()