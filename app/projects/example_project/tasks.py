# import json
#
# from app.machine_learning.decision_tree import DecisionTree
# from app.projects.example_project.example_project import ExampleProject
# from app.projects.example_project.example_model import ExampleModel
# from app import celery
#
# """Celery tasks for the example project."""
#
#
# @celery.task(name='example_project_predict')
# def make_prediction(doc_id, data):
#     """Celery task to calculate the prediction for the data from the
#     classifier and update the stored prediction for the document with
#     the given id.
#
#     :param doc_id: The ID of the MongoDB document.
#     :param data: Data to be used for classifying.
#
#     :type doc_id: str
#     :type data: dict
#     """
#     classifier = DecisionTree(
#         ExampleProject.PROJECT_NAME, ExampleModel,
#         ExampleModel.possible_labels)
#
#     prediction = classifier.predict(json.loads(data))
#
#     if prediction:
#         print("{} | Updating document '{}' with prediction: '{}'".format(
#             ExampleProject.PROJECT_NAME, doc_id, prediction))
#
#         ExampleModel.objects.get(id=doc_id).update(
#             set__t_species=prediction,
#         )
#
#
# @celery.task(name='example_project_train')
# def train_classifier():
#     """"Periodic Celery task for retraining the ML model if the data has
#     changed.
#     """
#     classifier = DecisionTree(
#         ExampleProject.PROJECT_NAME, ExampleModel,
#         ExampleModel.possible_labels)
#
#     classifier.train()