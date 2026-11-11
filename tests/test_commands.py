from meshbot.commands import BotContext, COMMANDS, HELP


def test_teste_responde_exato():
    assert COMMANDS["teste"](BotContext(), []) == "Teste recebido com sucesso!"


def test_args_aceitos_mas_ignorados():
    assert COMMANDS["teste"](BotContext(), ["agora"]) == "Teste recebido com sucesso!"


def test_resposta_cabe_em_1_pacote():
    # teto de airtime: 1 pacote Meshtastic = 228 bytes
    # (regra de estilo: mono-linha ate 60 chars; multi-linha ate 228)
    for nome, handler in COMMANDS.items():
        assert len(handler(BotContext(), [])) <= 228, nome


def test_tel_seis_linhas():
    linhas = COMMANDS["tel"](BotContext(), []).splitlines()
    assert len(linhas) == 6
    for numero in ("190", "192", "193", "199", "180", "188"):
        assert any(l.startswith(numero + " - ") for l in linhas), numero


def test_tel_descricoes_obrigatorias():
    out = COMMANDS["tel"](BotContext(), [])
    for servico in ("Polícia Militar", "SAMU", "Corpo de Bombeiros",
                    "Defesa Civil", "Atendimento à Mulher", "Valorização da Vida"):
        assert servico in out, servico


def test_rpt_quatro_repetidoras():
    linhas = COMMANDS["rpt"](BotContext(), []).splitlines()
    assert len(linhas) == 4
    assert linhas[0].startswith("Mirassol - 147.390")
    assert linhas[1].startswith("SJRP - 439.125")
    assert linhas[2].startswith("Cedral - 439.725")
    assert linhas[3].startswith("SJRP 2 - 439.275")


def test_rpt_tons_e_offsets():
    out = COMMANDS["rpt"](BotContext(), [])
    for token in ("+600", "-5000", "Sub 71.9", "Sub 100", "Sub 123"):
        assert token in out, token


def test_help_lista_todos_os_comandos():
    linhas = COMMANDS["help"](BotContext(), []).splitlines()
    assert "/teste - teste de recebimento" in linhas
    assert "/alerta - avisos INMET p/ SJRP" in linhas
    assert "/clima - agora + previsao 2 dias" in linhas


def test_help_nao_se_lista():
    linhas = COMMANDS["help"](BotContext(), []).splitlines()
    assert not any(l.startswith("/help") for l in linhas)


def test_help_ordenado_por_nome():
    linhas = COMMANDS["help"](BotContext(), []).splitlines()
    assert linhas == sorted(linhas)


def test_toda_command_tem_descricao():
    # guarda DRY: comando novo sem linha em HELP quebra aqui
    for nome in COMMANDS:
        if nome != "help":
            assert nome in HELP, f"falta descricao de /{nome} em HELP"
