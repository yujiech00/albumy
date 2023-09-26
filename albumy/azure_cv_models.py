from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from azure.cognitiveservices.vision.computervision.operations import ComputerVisionClientOperationsMixin

from array import array
import os

from albumy.extensions import db
from albumy.models import User, Photo, Tag, Follow, Collect, Comment, Notification

import credentials


'''
Authenticate
Authenticates your credentials and creates a client.
'''
# subscription_key = os.environ["VISION_KEY"]
# endpoint = os.environ["VISION_ENDPOINT"]

subscription_key = credentials.VISION_KEY
endpoint = credentials.VISION_ENDPOINT

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
computervision_client_local_support = ComputerVisionClientOperationsMixin()
'''
END - Authenticate
'''


def generate_tags_for_local_image(file_path):
    # Open the local image file
    local_image = open(file_path, "rb")
    
    # Call Azure CV model API with local image - generate tags
    tags_result_local = computervision_client.tag_image_in_stream(local_image)
    tags_with_high_confidence = []
    if (len(tags_result_local.tags) == 0):
        print("No tags detected for the local image uploaded.")
    else:
        for tag in tags_result_local.tags:
            print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))
            if tag.confidence*100 >= 50:
                tags_with_high_confidence.append(tag.name)
    print("Tags in the local image uploaded with high confidence:")
    print(tags_with_high_confidence)
    
    # print(db.session.query(Tag.name).distinct().count())
    existing_tags_in_db = db.session.query(Tag.name).distinct().all()
    existing_tags_in_db = [tag[0] for tag in existing_tags_in_db]      
    tags_to_be_attached_to_photo = []
    for tag in tags_with_high_confidence:
        # if the Tag (by name) does not exist in the database, create and add a new Tag object, and then commit to the database
        if tag not in existing_tags_in_db:
            new_tag = Tag(name=tag)
            db.session.add(new_tag)
            db.session.commit()
            tags_to_be_attached_to_photo.append(new_tag)
        # if the Tag (by name) already exists in the database, query to get this Tag object
        else:
            existing_tag_in_db_to_be_attached_to_photo = db.session.query(Tag).filter(Tag.name==tag).first()
            tags_to_be_attached_to_photo.append(existing_tag_in_db_to_be_attached_to_photo)
    # print(tags_to_be_attached_to_photo)
    # print(db.session.query(Tag.name).distinct().count())
    
    return tags_to_be_attached_to_photo


def generate_alt_text_or_description_for_local_image(file_path):
    # Open local image file
    local_image = open(file_path, "rb")
    
    # Call model API with local image - generate descriptions/captions
    description_result_local = computervision_client.describe_image_in_stream(local_image)
    # Get the captions/descriptions from the response, with confidence level
    print("Description of local image: ")
    if (len(description_result_local.captions) == 0):
        caption_with_highest_confidence_text = "No description detected."
    else:
        # the first caption in the description_result_local.captions is the one with highest confidence
        caption_with_highest_confidence = description_result_local.captions[0]
        if caption_with_highest_confidence.confidence*100 >= 50:
            caption_with_highest_confidence_text = caption_with_highest_confidence.text
        else:
            caption_with_highest_confidence_text = "No default description is recommended"
    
    return caption_with_highest_confidence_text
