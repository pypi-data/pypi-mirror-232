import string
import os
import json
import openai
import configparser
from concurrent.futures import ThreadPoolExecutor

MAX_WORKERS = 3
openai.api_key = os.environ["OPENAI_API_KEY"]


class SafetyChecker:
    @staticmethod
    def clean_text(text):
        text_to_check = text.replace("\n", " ").replace("\\n", " ")
        return text_to_check.translate(str.maketrans("", "", string.punctuation))

    @staticmethod
    def send_moderation_request(text_to_check):
        return openai.Moderation.create(
            model="text-moderation-latest", input=text_to_check
        )["results"][0]["flagged"]

    def check_is_violated(self, text):
        text_to_check = self.clean_text(text)

        threads = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for _ in range(3):
                threads.append(
                    executor.submit(self.send_moderation_request, text_to_check)
                )

        got_response = False
        while not got_response:
            for thread in threads:
                # if one of the threads is finished
                if thread.done():
                    # writing the result to the variable
                    is_violation = thread.result()
                    got_response = True
                    break

        return is_violation


class AIAssistantConfigHandler:
    def __init__(self, testing=False):
        self.ai_assistant_config = configparser.ConfigParser()
        if testing:
            path = os.path.join("predictors", "resource", "configs", "ai_assistant_subcategories_config.cfg")
        else:
            path = os.path.join("resource", "configs", "ai_assistant_subcategories_config.cfg")
        self.ai_assistant_config.read(path)


    def get_subcategory_from_config(self, intent_type, option):
        try:
            subcategory = self.ai_assistant_config.get(intent_type, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            # TO-DO: add logging for no section error
            return None
        return subcategory

    def get_prompt_subcategory(self, intent_type):
        return self.get_subcategory_from_config(intent_type, "prompt")

    def get_inbox_subcategory(self, inbox_category):
        return self.get_subcategory_from_config(inbox_category, "subcategories")

    def get_inbox_categories(self):
        return self.get_subcategory_from_config("inbox categories", "categories")

    def is_context_needed(self, intent_type):
        subcategory = self.get_subcategory_from_config(intent_type, "is_context_needed")
        if not subcategory:
            return False
        return eval(subcategory)


class PresetsHandler:
    def __init__(self):
        self.presets = None

    def load_presets(self, path_to_presets):
        with open(path_to_presets, "r") as f:
            self.presets = json.load(f)

    def get_bullets_presets(self):
        return self.presets["main_n_bullets"]

    def get_preset_for_one_email(self):
        return self.presets["one"]

    def get_preset_for_many_emails(self):
        return self.presets["many"]
