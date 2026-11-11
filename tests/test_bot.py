from meshbot.bot import MeshBot

MY_NUM = 0  # !XXXXXXXX


class FakeIface:
    def __init__(self):
        self.sent = []

        class _MyInfo:
            my_node_num = MY_NUM

        self.myInfo = _MyInfo()
        self.nodesByNum = {MY_NUM: {}}

    def sendText(self, text, destinationId=None, channelIndex=None, **kw):
        self.sent.append({"text": text, "dest": destinationId, "ch": channelIndex})


def packet(text, frm=999, from_id="!000003e7", to=None, channel=0):
    return {"from": frm, "fromId": from_id,
            "to": to if to is not None else 4294967295,  # broadcast
            "channel": channel,
            "decoded": {"portnum": "TEXT_MESSAGE_APP", "text": text}}


def test_teste_no_canal_responde_no_mesmo_canal():
    iface = FakeIface()
    MeshBot(iface).on_packet(packet("/teste"))
    assert iface.sent == [{"text": "Teste recebido com sucesso!",
                           "dest": None, "ch": 0}]


def test_teste_no_canal_2_responde_no_canal_2():
    iface = FakeIface()
    MeshBot(iface).on_packet(packet("/teste", channel=2))
    assert iface.sent[0]["ch"] == 2


def test_pm_responde_por_pm():
    iface = FakeIface()
    MeshBot(iface).on_packet(packet("/teste", to=MY_NUM))
    assert iface.sent[0]["dest"] == "!000003e7"
    assert iface.sent[0]["ch"] is None


def test_texto_sem_barra_ignorado():
    iface = FakeIface()
    MeshBot(iface).on_packet(packet("bom dia mesh"))
    assert iface.sent == []


def test_mensagem_do_proprio_node_ignorada():
    iface = FakeIface()
    MeshBot(iface).on_packet(packet("/teste", frm=MY_NUM))
    assert iface.sent == []


def test_portnum_diferente_ignorado():
    iface = FakeIface()
    p = packet("/teste")
    p["decoded"]["portnum"] = "POSITION_APP"
    MeshBot(iface).on_packet(p)
    assert iface.sent == []


def test_resposta_longa_quebrada_em_blocos_de_ate_228_bytes():
    longo = "\n".join(f"linha {i} com texto suficiente para estourar o limite " for i in range(8))
    iface = FakeIface()
    MeshBot(iface)._reply(packet(""), longo)  # a lib NAO fragmenta: quem quebra somos nos
    assert len(iface.sent) > 1
    for m in iface.sent:
        assert len(m["text"].encode("utf-8")) <= 228
    assert "\n".join(m["text"] for m in iface.sent) == longo


def test_comando_desconhecido_responde_dica():
    iface = FakeIface()
    MeshBot(iface).on_packet(packet("/xyz"))
    assert iface.sent[0]["text"] == "comando /xyz desconhecido (use /help)"


def test_rate_limit_duas_respostas_viram_uma():
    iface = FakeIface()
    bot = MeshBot(iface)
    bot.on_packet(packet("/teste"))
    bot.on_packet(packet("/teste"))
    assert len(iface.sent) == 1
