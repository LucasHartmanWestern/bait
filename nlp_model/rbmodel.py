import json
import re
import random
from model_utils import load_model, generate_text
import imghdr

# Load JSON data
def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}' successfully!")
        return json.load(bot_responses)

def is_image_content(filepath):
    image_type = imghdr.what(filepath)
    return image_type in ['jpeg', 'png']

def find_match(string):
    return True

# Store JSON data
response_data = load_json("responses.json")

model_load_path = "test_model.pt"
loaded_model = load_model(model_load_path)

def get_response(input_string, image_details,caption_details,):
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

    if image_details !="":
        return response_data[5]["bot_response"] + input_string + "}]}"
    # If there is no good response, return a gpt.
    if best_response != 0:
        if response_index <=2:
            return response_data[response_index]["bot_response"]
        else:
            return response_data[response_index]["bot_response"] + input_string + "}]}"
    
    #return generate_text(loaded_model, 500, input_string)
    
