import unittest
from types import SimpleNamespace

from rah_harness.deepseek_agent import DeepSeekSopAgent, create_deepseek_client


class _Tools:
    def get_tool_specs(self):
        return [{"toolSpec": {"name": "lookup", "description": "lookup a record", "inputSchema": {"json": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}}}}]

    def execute_tool(self, name, arguments):
        self.last_call = (name, arguments)
        return SimpleNamespace(success=True, result={"status": "found"}, error=None)


class _Client:
    def __init__(self):
        self.calls = 0
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            tool_call = SimpleNamespace(
                id="call-1",
                function=SimpleNamespace(name="lookup", arguments='{"id":"42"}'),
            )
            message = SimpleNamespace(content=None, tool_calls=[tool_call])
        else:
            message = SimpleNamespace(content="<final_decision>approve</final_decision>", tool_calls=[])
        return SimpleNamespace(choices=[SimpleNamespace(message=message)], usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5))


class _FailingClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        raise RuntimeError("Authentication Fails, Your api key: ****abcd is invalid")


class DeepSeekAgentTests(unittest.TestCase):
    def test_client_uses_verified_v1_endpoint_and_bounded_timeout(self):
        captured = {}

        def factory(**kwargs):
            captured.update(kwargs)
            return object()

        create_deepseek_client("test-key", client_factory=factory)

        self.assertEqual(captured["base_url"], "https://api.deepseek.com/v1")
        self.assertEqual(captured["timeout"], 30)
        self.assertEqual(captured["max_retries"], 0)

    def test_executes_tool_call_and_returns_final_decision_trace(self):
        client = _Client()
        tools = _Tools()
        agent = DeepSeekSopAgent(client=client, assembly="rah_full", max_steps=2)

        result = agent.execute("Use lookup before deciding.", {"case": "42"}, tools)

        self.assertTrue(result.success)
        self.assertEqual(tools.last_call, ("lookup", {"id": "42"}))
        self.assertIn("final_decision", result.output)
        self.assertEqual(len(result.tool_calls), 1)
        self.assertIn('"phase": "tool_result"', result.reasoning_trace)

    def test_sanitizes_provider_error_before_storing_trace(self):
        result = DeepSeekSopAgent(client=_FailingClient(), max_steps=1).execute(
            "SOP", {"case": "42"}, _Tools()
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error, "provider RuntimeError")
        self.assertNotIn("abcd", result.reasoning_trace)
