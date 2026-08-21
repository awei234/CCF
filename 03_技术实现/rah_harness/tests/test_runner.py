import os
import tempfile
import unittest
from pathlib import Path

from rah_harness.runner import (
    resolve_api_key,
    resolve_configured_deepseek_key,
    resolve_runtime_deepseek_key,
    validate_real_run_environment,
)


class RunnerTests(unittest.TestCase):
    def test_requires_checkout_and_model_key(self):
        with tempfile.TemporaryDirectory() as temp:
            old = os.environ.pop("DEEPSEEK_API_KEY", None)
            self.addCleanup(lambda: old and os.environ.setdefault("DEEPSEEK_API_KEY", old))
            issues = validate_real_run_environment(Path(temp))
        self.assertIn("missing DEEPSEEK_API_KEY", issues)
        self.assertIn("missing SOP-Bench checkout marker: pyproject.toml", issues)

    def test_resolves_deepseek_key_from_runtime_dotenv_without_logging_value(self):
        with tempfile.TemporaryDirectory() as temp:
            dotenv = Path(temp) / ".env"
            dotenv.write_text("DEEPSEEK_API_KEY=runtime-secret\n", encoding="utf-8")
            old = os.environ.pop("DEEPSEEK_API_KEY", None)
            self.addCleanup(lambda: old and os.environ.setdefault("DEEPSEEK_API_KEY", old))
            self.assertEqual(resolve_api_key(dotenv), "runtime-secret")

    def test_environment_key_takes_priority_over_runtime_dotenv(self):
        with tempfile.TemporaryDirectory() as temp:
            dotenv = Path(temp) / ".env"
            dotenv.write_text("DEEPSEEK_API_KEY=runtime-secret\n", encoding="utf-8")
            old = os.environ.get("DEEPSEEK_API_KEY")
            os.environ["DEEPSEEK_API_KEY"] = "environment-secret"
            self.addCleanup(
                lambda: os.environ.__setitem__("DEEPSEEK_API_KEY", old)
                if old is not None else os.environ.pop("DEEPSEEK_API_KEY", None)
            )
            self.assertEqual(resolve_api_key(dotenv), "environment-secret")

    def test_resolves_generic_runtime_key_only_for_explicit_deepseek_endpoint(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dotenv = root / ".env"
            config = root / "config.yaml"
            dotenv.write_text("API_KEY=runtime-secret\n", encoding="utf-8")
            config.write_text("base_url: https://api.deepseek.com\n", encoding="utf-8")
            old = os.environ.pop("DEEPSEEK_API_KEY", None)
            self.addCleanup(lambda: old and os.environ.setdefault("DEEPSEEK_API_KEY", old))
            self.assertEqual(resolve_runtime_deepseek_key(dotenv, config), "runtime-secret")

    def test_resolves_dedicated_key_from_deepseek_model_configuration(self):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / "config.yaml"
            config.write_text(
                "models:\n  defaults:\n    - model_client_config:\n"
                "        model_name: deepseek-v4-flash\n"
                "        api_base: https://api.deepseek.com/v1\n"
                "        client_provider: DeepSeek\n"
                "        api_key: dedicated-secret\n",
                encoding="utf-8",
            )
            self.assertEqual(resolve_configured_deepseek_key(config), "dedicated-secret")
