import pytest
import unittest

from promptflow.connections import CustomConnection
from jieting_try_tools.tools.jieting_try_tool_1 import jieting_try_tool_1_function


@pytest.fixture
def my_custom_connection() -> CustomConnection:
    my_custom_connection = CustomConnection(
        {
            "api-key" : "my-api-key",
            "api-secret" : "my-api-secret",
            "api-url" : "my-api-url"
        }
    )
    return my_custom_connection


class TestTool:
    def test_jieting_try_tool_1_function(self, my_custom_connection):
        result = jieting_try_tool_1_function(my_custom_connection, input_text="Microsoft")
        assert result == "Hello Microsoft"


# Run the unit tests
if __name__ == "__main__":
    unittest.main()