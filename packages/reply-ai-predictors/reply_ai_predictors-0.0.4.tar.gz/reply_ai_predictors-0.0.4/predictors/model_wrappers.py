import os
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]


class ModelTemplate:
    def __init__(self, model_file: str, **kwargs):
        self.model_file = model_file
        self.__dict__.update(kwargs)

    def get_filtered_params_only(self, exclude_params: list):
        return {
            key: value
            for key, value in self.__dict__.items()
            if key not in exclude_params
        }

    def construct_completion_request(
        self, added_request_params: dict, exclude_params=["model_file"]
    ):
        model_params = self.get_filtered_params_only(exclude_params)
        model_params.update(added_request_params)
        return model_params

    def create_completion_request(self, request_params: dict):
        request_kwargs = self.construct_completion_request(request_params)
        result = openai.Completion.create(**request_kwargs)
        return result

    def create_chat_completion_request(self, request_params: dict):
        request_kwargs = self.construct_completion_request(request_params)
        result = openai.ChatCompletion.create(**request_kwargs)
        return result


class DaVinciModel(ModelTemplate):
    def __init__(
        self,
        model_file,
        max_tokens: int,
        temperature: float,
        frequency_penalty: float,
        stop: list,
        **kwargs
    ):
        super(DaVinciModel, self).__init__(
            model_file,
            max_tokens=max_tokens,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            stop=stop,
            **kwargs
        )
        self.model = None

    @property
    def engine(self):
        return "davinci"

    def create_completion_request(self, prompt, user_id):
        if not self.model:
            added_params = {"prompt": prompt, "user": user_id, "engine": self.engine}
        else:
            added_params = {"prompt": prompt, "user": user_id, "engine": self.model}
        return super().create_completion_request(added_params)


class TextDavinciZeroZeroThree(ModelTemplate):
    def __init__(self, model_file, max_tokens: int, **kwargs):
        super(TextDavinciZeroZeroThree, self).__init__(
            model_file, max_tokens=max_tokens, **kwargs
        )

    @property
    def model(self):
        return "text-davinci-003"

    @model.setter
    def model(self, value):
        self.model = value

    def create_completion_request(self, prompt, user_id):
        added_params = {"prompt": prompt, "user": user_id, "model": self.model}
        return super().create_completion_request(added_params)


class GPTThreeFiveTurbo(ModelTemplate):
    def __init__(self, model_file, max_tokens: int, temperature: float, **kwargs):
        super(GPTThreeFiveTurbo, self).__init__(
            model_file, max_tokens=max_tokens, temperature=temperature, **kwargs
        )

    @property
    def model(self):
        return "gpt-3.5-turbo"

    def create_completion_request(self, messages: list, user_id):
        added_params = {"messages": messages, "user": user_id, "model": self.model}
        return super().create_chat_completion_request(added_params)


class CurieModel(ModelTemplate):
    def __init__(self, model_file, max_tokens: int, model: str, **kwargs):
        super(CurieModel, self).__init__(
            model_file, max_tokens=max_tokens, model=model, **kwargs
        )

    def create_completion_request(self, prompt, user_id):
        added_params = {"prompt": prompt, "user": user_id, "model": self.model}
        return super().create_completion_request(added_params)
