import json
import re
import random
#from model_utils import load_model, generate_text
#from image_captioner.ImgCaptionTest.test import process_image


import importlib.util
import sys
#Paths for the folder of each model
sys.path.append("../image classifier")
sys.path.append("../image captioner")
sys.path.append("../documentation identifier")

#Required imports for image classifier model
spec = importlib.util.spec_from_file_location("app", "../image classifier/app.py")
spec2 = importlib.util.spec_from_file_location("model_generator", "../image classifier/model_generator.py")
classifier_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier_app)
model_generator = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(model_generator)

#Required Imports for Image Captioning model
spec3 = importlib.util.spec_from_file_location("test", "../image captioner/ImgCaptionTest/test.py")
captioner_app = importlib.util.module_from_spec(spec3)
spec3.loader.exec_module(captioner_app)


#Required Imports for Documentation Identifier
spec4 = importlib.util.spec_from_file_location("app", "../documentation identifier/app.py")
doc_app = importlib.util.module_from_spec(spec4)
spec4.loader.exec_module(doc_app)

#Required Imports for Billing parser
spec5 = importlib.util.spec_from_file_location("app", "../billing parser/app.py")
bill_app = importlib.util.module_from_spec(spec5)
#spec5.loader.exec_module(bill_app)


# Load JSON data
def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}' successfully!")
        return json.load(bot_responses)

# Store JSON data
response_data = load_json("../nlp_model/responses.json")

#model_load_path = "test_model.pt"
#loaded_model = load_model(model_load_path)

def get_response(input_string, image_details):
    split_message = re.split(r'\s+|[,;?!.-]\s*', input_string.lower())
    score_list = []

    # Check all the responses
    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response["required_words"]

        # Check if there are any required words
        if required_words:
            for word in split_message:
                if word in required_words:
                    required_score += 1

        # Amount of required words should match the required score
        if required_score == len(required_words):
            # Check each word the user has typed
            for word in split_message:
                # If the word is in the response, add to the score
                if word in response["user_input"]:
                    response_score += 1

        # Add score to list
        score_list.append(response_score)
        # Debugging: Find the best phrase
        # print(response_score, response["user_input"])

    # Find the best response and return it if they're not all 0
    best_response = max(score_list)
    response_index = score_list.index(best_response)

    # Check if input is empty
    if input_string == "":
        return "Please type something so we can chat :("

    #Check if input query matches a previous query
    doc_found = doc_app.find_best_match(input_string)
    if ".pdf" not in doc_found.lower():
        return doc_found
    
    #bill_details = bill_app.return_bills()
    #Check if input has image
    if image_details !="":
        img_cap = captioner_app.process_image(image_details)
        img_class = classifier_app.get_prediction(image_details)
        response_data[6]["bot_response"][1]["content"][0]["text"] = response_data[6]["bot_response"][1]["content"][0]["text"].replace("{input}", input_string)
        response_data[6]["bot_response"][1]["content"][0]["text"] = response_data[6]["bot_response"][1]["content"][0]["text"].replace("{doc}", doc_found)
        response_data[6]["bot_response"][1]["content"][0]["text"] = response_data[6]["bot_response"][1]["content"][0]["text"].replace("{classification}", img_class)
        response_data[6]["bot_response"][1]["content"][0]["text"] = response_data[6]["bot_response"][1]["content"][0]["text"].replace("{caption}", img_cap)
        return response_data[8]["bot_response"]
    
    #Check if the input has to do with issues or simple conversation
    if best_response != 0:
        if response_index <=2:
            return response_data[response_index]["bot_response"]
        else:
            response_data[response_index]["bot_response"][1]["content"][0]["text"] = response_data[response_index]["bot_response"][1]["content"][0]["text"].replace("{input}", input_string)
            response_data[response_index]["bot_response"][1]["content"][0]["text"] = response_data[response_index]["bot_response"][1]["content"][0]["text"].replace("{doc}", doc_found)
            return response_data[response_index]["bot_response"]
    
    # If there is no good response, return a gpt.
    response_data[8]["bot_response"][1]["content"][0]["text"] = response_data[8]["bot_response"][1]["content"][0]["text"].replace("{input}", input_string)
    response_data[8]["bot_response"][1]["content"][0]["text"] = response_data[8]["bot_response"][1]["content"][0]["text"].replace("{doc}", doc_found)
    return response_data[8]["bot_response"]
    #return generate_text(loaded_model, 500, input_string)
    
