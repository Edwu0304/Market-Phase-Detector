from pathlib import Path

from market_phase_detector import glm_cli


def test_load_env_file_reads_glm_settings(tmp_path: Path):
    env_file = tmp_path / ".env.glm.local"
    env_file.write_text(
        "\n".join(
            [
                "API_KEY=test-key",
                "BASE_URL=https://bigmodel.cn",
                "MODEL_NAME=glm-4-flash",
            ]
        ),
        encoding="utf-8",
    )

    config = glm_cli.load_env_file(env_file)

    assert config.api_key == "test-key"
    assert config.base_url == "https://bigmodel.cn"
    assert config.model == "glm-4-flash"


def test_build_chat_payload_uses_user_prompt_and_model():
    config = glm_cli.GLMConfig(
        api_key="test-key",
        base_url="https://bigmodel.cn",
        model="glm-4-flash",
    )

    payload = glm_cli.build_chat_payload(
        config,
        prompt="Reply with exactly: pong",
    )

    assert payload["model"] == "glm-4-flash"
    assert payload["messages"] == [{"role": "user", "content": "Reply with exactly: pong"}]
    assert payload["temperature"] == 0.1
