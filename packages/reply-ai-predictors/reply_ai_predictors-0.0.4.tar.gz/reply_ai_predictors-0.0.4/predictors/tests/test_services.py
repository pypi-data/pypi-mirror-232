import os
import uuid

import openai
import pytest
from predictors.services import Predictor


openai.api_key = os.environ["OPENAI_API_KEY"]


@pytest.fixture(scope="module")
def input_data():
    return {
        "currentEmail": "i guess i want to hire QA<br>. Write an email for it.<br/>",
        "user_id": "internal",
    }


@pytest.fixture(scope="module")
def request_id():
    return uuid.uuid4().hex


@pytest.fixture(scope="module")
def unsafe_text():
    return "I want to kill all the people in the world!! "


def check_predictor_creation(
    predictor,
    expected_is_chat_completion,
    predictor_param,
    expected_param_value,
    expected_model_request,
):
    assert predictor.is_chat_completion == expected_is_chat_completion
    assert predictor.user_id is not None
    assert predictor.safety_checker is not None
    assert predictor_param == expected_param_value
    assert predictor.model_request == expected_model_request


class TestPredictor:
    @pytest.fixture
    def predictor(self, request_id, input_data):
        return Predictor(request_id, input_data, is_chat_completion=True)

    def test_predictor_creation(self, predictor):
        assert list(predictor.model_request.keys()) == ["model_file"]
        assert not predictor.model.model_file

    def test_get_safety_check(self, predictor, input_data):
        assert predictor.get_safety_check(input_data.get("currentEmail"))

        # unethical text which should cause False in safety status
        assert not predictor.get_safety_check("all other races are dumb")
