import os
import unittest

from rokpyl.core.config import apply_env_overrides, apply_set_overrides


class ConfigPrecedenceTests(unittest.TestCase):
    def test_env_then_set_override(self):
        base = {"project": "Config"}
        os.environ["ROKPYL__PROJECT"] = "Env"
        try:
            env_config = apply_env_overrides(base)
        finally:
            os.environ.pop("ROKPYL__PROJECT", None)

        self.assertEqual(env_config["project"], "Env")

        final = apply_set_overrides(env_config, ["project=Cli"])
        self.assertEqual(final["project"], "Cli")


if __name__ == "__main__":
    unittest.main()
