
import pytest
from adock.openai_api import translate_to_docker_command

def test_translate_to_docker_command():
    # This is a placeholder test and should be further refined
    result = translate_to_docker_command("What's the Docker command to list containers?")
    assert "command" in result
