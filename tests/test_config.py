#-jc basic configuration sanity checks

from common.config.config import Configuration


def test_config_defaults_load():
    cfg = Configuration()
    cfg.load_config(config_file_path=None)

    assert cfg.dispatcher_app_port is not None
    assert isinstance(cfg.dispatcher_allowed_extensions, set)

