import pytest
from predictors.model_wrappers import (
    ModelTemplate,
    DaVinciModel,
    TextDavinciZeroZeroThree,
    GPTThreeFiveTurbo,
    CurieModel,
)


def get_dict_keys_as_sorted_list(test_dict):
    return sorted(list(test_dict.keys()))


def get_class_params(class_object):
    return get_dict_keys_as_sorted_list(class_object.__dict__)


@pytest.fixture(scope="module")
def user_id():
    return "internal"


@pytest.fixture(scope="module")
def prompt():
    return "Hello, I want to hire more people."


class TestModelTemplate:
    @pytest.fixture
    def test_mdl_template_1(self):
        return ModelTemplate("some_file_name")

    @pytest.fixture
    def mdl_template_args(self):
        return {
            "max_tokens": 200,
            "temperature": 0.7,
            "best_of": 2,
            "engine": "davinci",
        }

    @pytest.fixture
    def test_mdl_template_2(self, mdl_template_args):
        return ModelTemplate("another_file_name", **mdl_template_args)

    def test_create_model_templates(
        self, test_mdl_template_1, test_mdl_template_2, mdl_template_args
    ):
        assert get_class_params(test_mdl_template_1) == ["model_file"]
        expected_params = sorted(
            get_dict_keys_as_sorted_list(mdl_template_args) + ["model_file"]
        )
        assert get_class_params(test_mdl_template_2) == expected_params

    def test_get_filtered_params_only(self, test_mdl_template_2, mdl_template_args):
        exclude_params = ["model_file"]
        actual_params = test_mdl_template_2.get_filtered_params_only(
            exclude_params=exclude_params
        )
        expected_params = [
            param
            for param in get_dict_keys_as_sorted_list(mdl_template_args)
            if param not in exclude_params
        ]
        assert get_dict_keys_as_sorted_list(actual_params) == expected_params

    def test_construct_completion_request(self, test_mdl_template_2):
        actual_params = test_mdl_template_2.construct_completion_request(
            {"animal": "racoon"}, ["best_of", "model_file"]
        )
        expected_params = {
            "max_tokens": 200,
            "temperature": 0.7,
            "engine": "davinci",
            "animal": "racoon",
        }
        assert actual_params == expected_params

    def test_create_completion_request(self, test_mdl_template_2, user_id, prompt):
        test_request_params = {
            "prompt": prompt,
            "user": user_id,
            "engine": test_mdl_template_2.engine,
        }

        request_result = test_mdl_template_2.create_completion_request(
            test_request_params
        )
        assert request_result["created"] is not None
        assert request_result["model"] == test_mdl_template_2.engine

    def test_create_chat_completion_request(self, user_id):
        test_request_params = {
            "model": "gpt-3.5-turbo",
            "user": user_id,
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
        }
        model = ModelTemplate("some_file_name", **test_request_params)

        request_result = model.create_chat_completion_request(test_request_params)
        assert request_result["created"] is not None
        assert request_result["object"] == "chat.completion"


class TestDaVinciModel:
    @pytest.fixture
    def class_args(self):
        return {
            "model_file": "",
            "max_tokens": 512,
            "temperature": 0.6,
            "frequency_penalty": 0.02,
            "stop": ["[[", "###"],
        }

    def test_class_creation(self, class_args):
        def _test_class_creation(args):
            davinci_mdl = DaVinciModel(**args)
            assert davinci_mdl.engine == "davinci"
            # we add 1 to length because there's also model argument defined in class constructor
            assert len(get_class_params(davinci_mdl)) == len(args) + 1
            assert "best_of" not in get_class_params(davinci_mdl)

        _test_class_creation(class_args)

        class_args["best_of"] = 2
        with pytest.raises(AssertionError):
            _test_class_creation(class_args)

    def test_create_completion_request(self, class_args, user_id, prompt):
        davinci_mdl_1 = DaVinciModel(**class_args)
        request_result = davinci_mdl_1.create_completion_request(prompt, user_id)
        assert request_result["created"] is not None
        assert request_result["model"] == davinci_mdl_1.engine


class TestTextDavinciZeroZeroThree:
    @pytest.fixture
    def class_args(self):
        return {
            "model_file": "",
            "max_tokens": 512,
            "temperature": 0.7,
        }

    @pytest.fixture
    def test_prompt(self):
        return "I want to hire QA. Write an email for it."

    def test_class_creation(self, class_args):
        test_mdl = TextDavinciZeroZeroThree(**class_args)
        assert test_mdl.model == "text-davinci-003"
        assert len(get_class_params(test_mdl)) == len(class_args)

    def test_create_completion_request_da_vinci(self, class_args, test_prompt, user_id):
        test_mdl = TextDavinciZeroZeroThree(**class_args)
        request_result = test_mdl.create_completion_request(test_prompt, user_id)
        assert request_result["created"] is not None
        assert request_result["model"] == test_mdl.model


class TestGPTThreeFiveTurbo:
    @pytest.fixture
    def class_args(self):
        return {"model_file": "", "max_tokens": 512, "temperature": 0.7}

    @pytest.fixture
    def messages(self):
        return [
            {
                "role": "system",
                "content": f"You are a SDR and you need to reply to the user.",
            },
            {
                "role": "user",
                "content": f"Your previous email:\nI just wanted to let you know we've discussed it last time.\n\n",
            },
        ]

    def test_class_creation(self, class_args):
        gpt3_mdl = GPTThreeFiveTurbo(**class_args)
        assert len(get_class_params(gpt3_mdl)) == len(class_args)
        assert gpt3_mdl.model == "gpt-3.5-turbo"

    def test_create_completion_request(self, class_args, user_id, messages):
        model = GPTThreeFiveTurbo(**class_args)
        request_result = model.create_completion_request(messages, user_id)
        assert request_result["created"] is not None
        assert request_result["object"] == "chat.completion"


class TestCurieModel:
    @pytest.fixture
    def class_args(self):
        return {
            "model_file": "",
            "max_tokens": 1,
            "model": "curie:ft-reply:intent-type-categorizer-2-2023-02-09-12-14-43",
        }

    def test_class_creation(self, class_args):
        curie_mdl_1 = CurieModel(**class_args)
        assert len(get_class_params(curie_mdl_1)) == len(class_args)

        class_args_2 = {
            "model_file": "",
            "max_tokens": 128,
            "model": "curie:ft-reply-2022-10-12-14-28-52",
            "temperature": 0,
            "stop": ["###"],
        }
        curie_mdl_2 = CurieModel(**class_args_2)
        assert len(get_class_params(curie_mdl_2)) == len(class_args_2)

    def test_create_completion_request(self, class_args, user_id, prompt):
        curie_mdl = CurieModel(**class_args)
        request_result = curie_mdl.create_completion_request(prompt, user_id)
        assert request_result["created"] is not None
