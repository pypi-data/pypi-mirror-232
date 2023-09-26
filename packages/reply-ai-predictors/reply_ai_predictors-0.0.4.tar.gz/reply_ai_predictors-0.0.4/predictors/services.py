import os
import openai
import time
from concurrent.futures import ThreadPoolExecutor
from predictors.helpers import SafetyChecker
from predictors.model_wrappers import ModelTemplate

MAX_WORKERS = 3
openai.api_key = os.environ["OPENAI_API_KEY"]


class Predictor:
    def __init__(self, request_id, input_data, is_chat_completion):
        self.request_id = request_id
        self.user_id = str(input_data.get("user_id", ""))
        self.safety_checker = SafetyChecker()
        self.is_chat_completion = is_chat_completion

    @property
    def model_request(self):
        return {"model_file": None}

    @property
    def model(self):
        return ModelTemplate(**self.model_request)

    @property
    def alternative_model(self):
        return ModelTemplate(**self.model_request)

    def preprocess_input_data(self):
        pass

    def run_pipeline(self):
        pass

    def get_safety_check(self, text):
        check_is_violated = self.safety_checker.check_is_violated(text)
        if check_is_violated:
            return False
        return True

    @staticmethod
    def get_chat_completion_thread_result(thread_result):
        return thread_result["choices"][0]["message"]["content"]

    @staticmethod
    def get_completion_thread_result(thread_result):
        return thread_result["choices"][0]["text"]

    def handle_timeout_request(
        self,
        original_request_args,
        alternative_request_kwargs,
        time_to_wait_for_response,
    ):
        start_request_time = time.time()
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            if self.is_chat_completion:
                thread = executor.submit(
                    openai.ChatCompletion.create, **original_request_args
                )
            else:
                thread = executor.submit(
                    openai.Completion.create, **original_request_args
                )
        thread_result = None
        got_response = False
        while (
            not got_response
            and (time.time() - start_request_time) < time_to_wait_for_response
        ):
            if thread.done():
                if self.is_chat_completion:
                    thread_result = Predictor.get_chat_completion_thread_result(
                        thread.result()
                    )
                else:
                    thread_result = Predictor.get_completion_thread_result(
                        thread.result()
                    )
                got_response = True
                break

        if not got_response:
            while (time.time() - start_request_time) < time_to_wait_for_response:
                thread = openai.Completion.create(**alternative_request_kwargs)
                thread_result = Predictor.get_completion_thread_result(thread)
                got_response = True

        if not got_response:
            raise openai.error.Timeout

        return thread_result
