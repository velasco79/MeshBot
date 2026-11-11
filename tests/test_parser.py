from meshbot.parser import parse_command


def test_comando_simples():
    assert parse_command("/teste") == ("teste", [])


def test_case_insensitive():
    assert parse_command("/TESTE") == ("teste", [])


def test_com_args():
    assert parse_command("/teste agora") == ("teste", ["agora"])


def test_barra_nua():
    assert parse_command("  /  ") is None


def test_sem_barra_e_ignorado():
    assert parse_command("bom dia") is None
    assert parse_command("teste") is None


def test_vazio_e_none():
    assert parse_command("") is None
    assert parse_command(None) is None
