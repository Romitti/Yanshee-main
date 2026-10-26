import time

import YanAPI

ROBOT_IP = "127.0.0.1"

VOLUME = 100
LIMIAR_ROSTOS = 1
COOLDOWN = 8.0
INTERVALO = 0.5
MAX_ACENOS = 0
DEBUG = False
TIPO_RECONHECIMENTO = "quantity"

RAISE_HAND_STOP = True
VELOCIDADE_MOVIMENTO = "slow"
VELOCIDADE_HIPHOP = "fast"
PAUSA_FALA = 0.7
PAUSA_SEQUENCIA = 0.5
REPETIR_HIPHOP = 1

MUSICA_HIPHOP = "hiphop.mp3"

LETRA_HIPHOP = ["Yeah!", "Uh! Vai, vai!", "Boom, boom!", "Bate, bate, bate!"]
DANCA_HIPHOP = ["rightmovestep", "H_RBox", "leftmovestep", "GangnamStyle",
                "H_Wave_R", "H_Wave_L", "LittleApple", "Victory"]


def com_seguranca(funcao):
    try:
        funcao()
    except Exception:
        pass


def conectar():
    print("Conectando ao robo em {} ...".format(ROBOT_IP))
    YanAPI.yan_api_init(ROBOT_IP)
    time.sleep(1)


def checar_bateria():
    bateria = YanAPI.get_robot_battery_value()
    if bateria < 20:
        print("Bateria baixa: {}%".format(bateria))
    else:
        print("Bateria OK: {}%".format(bateria))


def acenar_falando():
    com_seguranca(lambda: YanAPI.start_voice_tts(tts="Ola...", interrupt=False))
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="wave", direction="right", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    time.sleep(PAUSA_FALA)
    com_seguranca(lambda: YanAPI.start_voice_tts(tts="mestre!", interrupt=False))
    time.sleep(PAUSA_SEQUENCIA)


def abaixar_e_levantar_bracos():
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="crouch", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    time.sleep(PAUSA_SEQUENCIA)
    com_seguranca(lambda: YanAPI.start_voice_tts(tts="E hora...", interrupt=False))
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="raise", direction="both", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    time.sleep(PAUSA_FALA)
    com_seguranca(lambda: YanAPI.sync_do_tts(tts="do show...", interrupt=False))
    time.sleep(PAUSA_FALA)
    com_seguranca(lambda: YanAPI.sync_do_tts(tts="porra!", interrupt=False))


def pedir_desculpas():
    led("red", "blink")
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="bend", direction="both", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    com_seguranca(lambda: YanAPI.sync_do_tts(tts="Desculpa...", interrupt=False))
    time.sleep(PAUSA_FALA)
    com_seguranca(lambda: YanAPI.sync_do_tts(tts="nao vou mais interromper!", interrupt=False))
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="reset", direction="both", speed=VELOCIDADE_MOVIMENTO, repeat=1))
    led("blue", "off")


def voltar_a_pose():
    com_seguranca(lambda: YanAPI.sync_play_motion(
        name="reset", direction="both", speed=VELOCIDADE_MOVIMENTO, repeat=1))


def led(cor, modo):
    com_seguranca(lambda: YanAPI.set_robot_led(type="button", color=cor, mode=modo))


def contar_rostos_em(dado):
    if isinstance(dado, list):
        return len(dado)
    if not isinstance(dado, dict):
        return 0
    total = 0
    for chave, valor in dado.items():
        chave_l = str(chave).lower()
        if isinstance(valor, int) and any(
                p in chave_l for p in ("num", "count", "quantity", "total")):
            total = max(total, valor)
        elif isinstance(valor, list) and "face" in chave_l:
            total = max(total, len(valor))
        elif isinstance(valor, dict):
            total = max(total, contar_rostos_em(valor))
    return total


def detectar_rostos():
    try:
        retorno = YanAPI.sync_do_face_recognition(type=TIPO_RECONHECIMENTO)
        if DEBUG:
            print(retorno)
        if not isinstance(retorno, dict):
            return 0
        if retorno.get("code", 0) not in (0, "0"):
            return 0
        return contar_rostos_em(retorno.get("data", retorno))
    except Exception:
        return 0


def mao_levantada():
    try:
        retorno = YanAPI.sync_do_gesture_recognition()
        if DEBUG:
            print(retorno)
    except Exception:
        return False
    if not isinstance(retorno, dict) or retorno.get("code", 0) not in (0, "0"):
        return False
    data = retorno.get("data", retorno)
    valores = []
    if isinstance(data, dict):
        valores = list(data.values())
    elif isinstance(data, list):
        valores = data
    for valor in valores:
        if isinstance(valor, str) and valor.strip().lower() == "good":
            return True
    return False


def tocar_musica(nome_procurado):
    try:
        retorno = YanAPI.get_media_music_list()
    except Exception:
        retorno = None
    nome = None
    if isinstance(retorno, dict) and retorno.get("code", 0) in (0, "0"):
        data = retorno.get("data", retorno)
        itens = []
        if isinstance(data, list):
            itens = data
        elif isinstance(data, dict):
            if isinstance(data.get("music"), list):
                itens = data["music"]
            else:
                for valor in data.values():
                    if isinstance(valor, list):
                        itens = valor
                        break
        if isinstance(itens, list):
            alvo_base = nome_procurado.rsplit(".", 1)[0].lower()
            for item in itens:
                if isinstance(item, dict):
                    nome_item = str(item.get("name", item.get("fileName", "")))
                else:
                    nome_item = str(item)
                if nome_item.rsplit(".", 1)[0].lower() == alvo_base:
                    nome = nome_item
                    break
    if nome:
        print("Musica encontrada: {}".format(nome))
        com_seguranca(lambda: YanAPI.start_play_music(name=nome))
        return True
    print("Arquivo {} nao encontrado no robo; cantando pelo TTS.".format(nome_procurado))
    return False


def dancar_hiphop():
    led("cyan", "blink")
    tocando = tocar_musica(MUSICA_HIPHOP)
    for _ in range(REPETIR_HIPHOP):
        for movimento in DANCA_HIPHOP:
            if RAISE_HAND_STOP and mao_levantada():
                if tocando:
                    com_seguranca(lambda: YanAPI.stop_play_music())
                com_seguranca(lambda: YanAPI.stop_play_motion(name=""))
                com_seguranca(lambda: YanAPI.stop_voice_tts())
                print("Mao levantada! Parando o show e pedindo desculpas.")
                pedir_desculpas()
                return "parado"
            if not tocando:
                pedaco = LETRA_HIPHOP[DANCA_HIPHOP.index(movimento) % len(LETRA_HIPHOP)]
                com_seguranca(lambda: YanAPI.start_voice_tts(tts=pedaco, interrupt=False))
            com_seguranca(lambda: YanAPI.sync_play_motion(
                name=movimento, direction="both", speed=VELOCIDADE_HIPHOP, repeat=1))
    if tocando:
        com_seguranca(lambda: YanAPI.stop_play_music())
    return "concluido"


def apresentar():
    if RAISE_HAND_STOP and mao_levantada():
        print("Ja comecou com mao levantada! Pedindo desculpas antes de comecar.")
        pedir_desculpas()
        return
    acenar_falando()
    if RAISE_HAND_STOP and mao_levantada():
        print("Mao levantada no meio do aceno! Parando.")
        com_seguranca(lambda: YanAPI.stop_voice_tts())
        com_seguranca(lambda: YanAPI.stop_play_motion(name=""))
        pedir_desculpas()
        return
    abaixar_e_levantar_bracos()
    if dancar_hiphop() == "parado":
        return
    voltar_a_pose()


def main():
    try:
        conectar()
    except Exception:
        print("Nao foi possivel conectar ao robo. Confira o IP.")
        return

    checar_bateria()
    com_seguranca(lambda: YanAPI.set_robot_volume_value(VOLUME))

    acenos = 0
    ultimo_aceno = 0.0
    try:
        while MAX_ACENOS == 0 or acenos < MAX_ACENOS:
            led("blue", "blink")
            n_rostos = detectar_rostos()
            agora = time.time()
            if n_rostos >= LIMIAR_ROSTOS and (agora - ultimo_aceno) >= COOLDOWN:
                led("green", "on")
                print("Rosto detectado! Show (mao levantada = para tudo).")
                apresentar()
                acenos += 1
                ultimo_aceno = time.time()
            else:
                time.sleep(INTERVALO)
    except KeyboardInterrupt:
        pass
    finally:
        com_seguranca(lambda: YanAPI.stop_face_recognition(type=TIPO_RECONHECIMENTO))
        com_seguranca(lambda: YanAPI.stop_play_music())
        led("blue", "off")
        voltar_a_pose()


if __name__ == "__main__":
    main()
