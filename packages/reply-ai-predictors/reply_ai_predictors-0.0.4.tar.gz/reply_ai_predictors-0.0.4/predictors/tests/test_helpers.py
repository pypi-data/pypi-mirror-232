import pytest
import os
import openai
import configparser
from predictors.helpers import SafetyChecker, AIAssistantConfigHandler, PresetsHandler


openai.api_key = os.environ["OPENAI_API_KEY"]


@pytest.fixture(scope="module")
def unsafe_text():
    return "I want to kill all the people in the world!! "


class TestSafetyChecker:
    def test_clean_text(self):
        test_text = (
            "Dear Mr,\nHope you are doing well,\\nI'd like to discuss a few issues we touched last "
            "time.\\nLooking forwards to hearing back from you."
        )
        expected_text = (
            "Dear Mr Hope you are doing well Id like to discuss a few issues we touched last time "
            "Looking forwards to hearing back from you"
        )
        assert SafetyChecker.clean_text(test_text) == expected_text

        test_text = "I want to hire a DevOps."
        expected_text = "I want to hire a DevOps"
        assert SafetyChecker.clean_text(test_text) == expected_text

    def test_send_moderation_request(self, unsafe_text):
        response = SafetyChecker.send_moderation_request(unsafe_text)
        assert response is not None
        assert response

        test_text = "I want to hire an HR"
        response = SafetyChecker.send_moderation_request(test_text)
        assert response is not None
        assert not response

    def test_check_is_violated(self, unsafe_text):
        is_violated = SafetyChecker().check_is_violated(unsafe_text)
        assert is_violated

        check_text = "I want to hire an HR"
        is_violated = SafetyChecker().check_is_violated(check_text)
        assert not is_violated


class TestAIAssistantConfigHandler:
    @pytest.fixture
    def config_handler(self):
        return AIAssistantConfigHandler(testing=True)

    def test_created_config(self, config_handler):
        assert config_handler.ai_assistant_config is not None
        assert isinstance(config_handler.ai_assistant_config, configparser.ConfigParser)
        assert (
            config_handler.ai_assistant_config.get("interested", "subcategories")
            is not None
        )

    def test_get_subcategory_from_config(self, config_handler):
        # happy path
        subcategory = config_handler.get_subcategory_from_config(
            "general prompt", "prompt"
        )
        assert (
            subcategory
            == "Reply to your_customer_answer in manner of your_previous_email."
        )
        subcategory = config_handler.get_subcategory_from_config(
            "link request", "is_context_needed"
        )
        assert subcategory == "False"

        # the case when we don't have a section we're looking for
        subcategory = config_handler.get_subcategory_from_config("some_case", "other")
        assert subcategory is None

        # the case when we have an option but no section for such an option
        subcategory = config_handler.get_subcategory_from_config(
            "general prompt", "other"
        )
        assert subcategory is None

    def test_get_prompt_subcategory(self, config_handler):
        expected_prompt_subcategory = (
            "Reply to your_customer_answer given that the person suggested time in manner "
            "of your_previous_email."
        )
        assert (
            config_handler.get_prompt_subcategory("time suggestion")
            == expected_prompt_subcategory
        )

        # test for subcategory which doesn't have prompt option
        assert config_handler.get_prompt_subcategory("interested") is None

    def test_get_inbox_subcategory(self, config_handler):
        expected_prompt_subcategory = (
            "not interested for no reason,not interested for some reason"
        )
        assert (
            config_handler.get_inbox_subcategory("not interested")
            == expected_prompt_subcategory
        )

        # test for subcategory which doesn't have subcategories option
        assert config_handler.get_inbox_subcategory("general prompt") is None

    def test_get_inbox_categories(self, config_handler):
        expected_categories = "interested,not interested,not now,forwarded,"
        assert config_handler.get_inbox_categories() == expected_categories

    def test_is_context_needed(self, config_handler):
        assert config_handler.is_context_needed("general prompt") is False
        assert (
            config_handler.is_context_needed("question about pricing or discount")
            is True
        )

        # case when there is no such section as is_context_needed
        assert config_handler.is_context_needed("general prompt") is False

        # error cases
        assert config_handler.is_context_needed("") is False
        assert config_handler.is_context_needed("interested") is False


class TestPresetsHandler:
    @pytest.fixture
    def presets_handler(self):
        return PresetsHandler()

    @pytest.fixture
    def path_to_first_email_presets(self):
        return os.path.join("predictors", "resource", "preset_inputs", "first_email.json")

    @pytest.fixture
    def path_to_followup_presets(self):
        return os.path.join("predictors", "resource", "preset_inputs", "followup.json")

    def test_presets_creation(self, presets_handler):
        assert presets_handler.presets is None

    def test_load_presets(self, presets_handler, path_to_first_email_presets):
        presets_handler.load_presets(path_to_first_email_presets)
        assert presets_handler.presets is not None
        assert isinstance(presets_handler.presets, dict)

        incorrect_path_to_presets = os.path.join("some_preset.json")
        test_presets_handler = PresetsHandler()
        with pytest.raises(FileNotFoundError):
            test_presets_handler.load_presets(incorrect_path_to_presets)
        assert test_presets_handler.presets is None

    # noinspection PyMethodMayBeStatic
    def check_presets_indexing(
        self, path_to_presets, indexing_method_response, error_preset
    ):
        def _check_presets_indexing_happy_path(method_name):
            presets_handler = PresetsHandler()
            presets_handler.load_presets(path_to_presets)
            indexed_presets = getattr(presets_handler, method_name)()
            assert indexed_presets is not None
            assert isinstance(indexed_presets, str)

        def _check_presets_indexing_error_case(method_name, preset):
            presets_handler = PresetsHandler()
            presets_handler.presets = preset
            with pytest.raises(TypeError):
                _ = getattr(presets_handler, method_name)()

        _check_presets_indexing_happy_path(indexing_method_response)
        _check_presets_indexing_error_case(indexing_method_response, error_preset)

    def test_get_bullets_presets(self, presets_handler, path_to_first_email_presets):
        self.check_presets_indexing(
            path_to_first_email_presets, "get_bullets_presets", ""
        )

    def test_get_preset_for_one_email(self, path_to_followup_presets):
        self.check_presets_indexing(
            path_to_followup_presets, "get_preset_for_one_email", ""
        )

    def test_get_preset_for_many_emails(
        self, presets_handler, path_to_followup_presets
    ):
        self.check_presets_indexing(
            path_to_followup_presets, "get_preset_for_many_emails", ""
        )
