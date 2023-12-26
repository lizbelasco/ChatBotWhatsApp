import requests
import sett
import json
import time
import mysql.connector

pedido = ""
comida = ""
precio = 0
total = 0


def replace_start(s):
    if s.startswith("521"):
        return "52" + s[3:]
    else:
        return s


def anadir_pedido(pedido, comida):
    if not pedido:
        pedido = comida
    else:
        pedido = pedido + ", " + comida

    return pedido


def obtener_Mensaje_whatsapp(message):
    if "type" not in message:
        text = "mensaje no reconocido"
        return text

    typeMessage = message["type"]
    if typeMessage == "text":
        text = message["text"]["body"]
    elif typeMessage == "button":
        text = message["button"]["text"]
    elif (
        typeMessage == "interactive" and message["interactive"]["type"] == "list_reply"
    ):
        text = message["interactive"]["list_reply"]["title"]
    elif (
        typeMessage == "interactive"
        and message["interactive"]["type"] == "button_reply"
    ):
        text = message["interactive"]["button_reply"]["title"]
    elif (
        typeMessage == "interactive"
        and message["interactive"]["type"] == "location_request_message"
    ):
        text = message["interactive"]["location_request_message"]["title"]
    else:
        text = "mensaje no procesado"

    return text


def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        whatsapp_url = sett.whatsapp_url
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + whatsapp_token,
        }
        print("se envia ", data)
        response = requests.post(whatsapp_url, headers=headers, data=data)

        if response.status_code == 200:
            return "mensaje enviado", 200
        else:
            return "error al enviar mensaje", response.status_code
    except Exception as e:
        return e, 403


def text_Message(number, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {"body": text},
        }
    )
    return data


def buttonReply_Message(number, image_id, options, body, footer, sedd, messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append(
            {
                "type": "reply",
                "reply": {"id": sedd + "_btn_" + str(i + 1), "title": option},
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "image",
                    "image": {"id": image_id},
                },
                "body": {"text": body},
                "footer": {"text": footer},
                "action": {"buttons": buttons},
            },
        }
    )
    return data


def listReply_Message(number, options, descriptions, body, footer, sedd, messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append(
            {
                "id": sedd + "_row_" + str(i + 1),
                "title": option,
                "description": descriptions[i],
            }
        )

    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body},
                "footer": {"text": footer},
                "action": {
                    "button": "Ver Opciones",
                    "sections": [{"title": "Secciones", "rows": rows}],
                },
            },
        }
    )
    return data


def locationReply_Message(number, messageId):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "20.59279258300968",
                "longitude": "-100.4043440880425",
                "name": "Aurelia Lunch & Café.",
                "address": "Calle Mariano Escobedo 241-B, Centro, 76000 Santiago de Querétaro, Qro.",
            },
        }
    )
    return data


def document_Message(number, url, caption, filename):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "document",
            "document": {"link": url, "caption": caption, "filename": filename},
        }
    )
    return data


def sticker_Message(number, sticker_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "sticker",
            "sticker": {"id": sticker_id},
        }
    )
    return data


def image_Message(number, image_id):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "image",
            "image": {"id": image_id},
        }
    )
    return data


def get_media_id(media_name, media_type):
    media_id = ""
    if media_type == "sticker":
        media_id = sett.stickers.get(media_name, None)
    elif media_type == "image":
        media_id = sett.images.get(media_name, None)
    # elif media_type == "video":
    #    media_id = sett.videos.get(media_name, None)
    # elif media_type == "audio":
    #    media_id = sett.audio.get(media_name, None)
    return media_id


def replyReaction_Message(number, messageId, emoji):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "reaction",
            "reaction": {"message_id": messageId, "emoji": emoji},
        }
    )
    return data


def replyText_Message(number, messageId, text):
    data = json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "context": {"message_id": messageId},
            "type": "text",
            "text": {"body": text},
        }
    )
    return data


def markRead_Message(messageId):
    data = json.dumps(
        {"messaging_product": "whatsapp", "status": "read", "message_id": messageId}
    )
    return data


def administrar_chatbot(text, number, messageId, name):
    global pedido
    global comida
    global total
    global precio

    final = ""

    text = text.lower()  # mensaje que envio el usuario
    list = []

    print("mensaje del usuario: ", text)
    print("Pedido del usuario: ", pedido)
    print("Total del usuario: ", total)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a Aurelia. ¿Cómo podemos ayudarte hoy?"
        footer = "Aurelia"
        options = ["📖 Menu", "📅 Horarios"]

        imagen = get_media_id("logo", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "👋")
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "menu" in text:
        body = "Tenemos varias áreas de consulta para elegir. ¿Cuál de estas secciones te gustaría explorar?"
        footer = "Aurelia"
        options = ["Chapatas", "Sándwiches", "Pastas", "Especiales", "Ensaladas"]
        descriptions = ["uno", "dos", "tres", "cuatro", "cinco"]

        listReply = listReply_Message(
            number, options, descriptions, body, footer, "sed2", messageId
        )
        list.append(listReply)

    elif "horarios" in text:
        data = text_Message(
            number,
            "Los horarios son: \nLunes a Viernes de 9 am a 5:30 p.m \nSábado y Domingo cerrado",
        )
        list.append(data)

    elif "chapatas" in text:
        body = "Aqui esta el menu para la seccion chapatas"
        footer = "Aurelia"
        options = [
            "Chapata 1",
            "Chapata 2",
            "Chapata 3",
            "Chapata 4",
            "Chapata 5",
            "Chapata 6",
            "Chapata 7",
        ]
        descriptions = [
            "Pollo con tocino y queso $100",
            "Cecina con Vegetales $100",
            "Jamón Serrano $120",
            "Pollo con Chipotle $100",
            "Arrachera con guacamole $125",
            "De Pollo con Pesto y Feta $120",
            "Vegetariana $90",
        ]

        listReply = listReply_Message(
            number, options, descriptions, body, footer, "sed3", messageId
        )
        list.append(listReply)

    elif "sándwiches" in text:
        body = "Sándwiches."
        footer = "Aurelia"
        options = ["Sándwich 1", "Sándwich 2"]
        descriptions = ["Club Sandwich $95", "Panela con Jamón $55"]

        listReply = listReply_Message(
            number, options, descriptions, body, footer, "sed3", messageId
        )
        list.append(listReply)

    elif "pastas" in text:
        body = "Pastas"
        footer = "Aurelia"
        options = ["Pasta 1", "Pasta 2", "Pasta 3", "Pasta 4", "Pasta 5", "Pasta 6"]
        descriptions = [
            "Spaghetti boloñesa $110",
            "Vegetales con salsa de tomate $95",
            "Pechuga de pollo al pesto $105",
            "Camarones arrabiata $125",
            "Camarones a la crema con pimientos $125",
            "Alfredo con pollo y champiñones $105",
        ]

        listReply = listReply_Message(
            number, options, descriptions, body, footer, "sed3", messageId
        )
        list.append(listReply)

    elif "especiales" in text:
        body = "Especiales"
        footer = "Aurelia"
        options = ["Especial 1", "Especial 2", "Especial 3", "Especial 4"]
        descriptions = [
            "Alambre de arrachera $125",
            "Parrillada de cecina $115",
            "Arroz frito vegetariano $85",
            "Arroz frito con res o pollo $95",
        ]

        listReply = listReply_Message(
            number, options, descriptions, body, footer, "sed3", messageId
        )
        list.append(listReply)

    elif "ensaladas" in text:
        body = "Ensaladas"
        footer = "Aurelia"
        options = [
            "Ensalada 1",
            "Ensalada 2",
            "Ensalada 3",
            "Ensalada 4",
            "Ensalada 5",
            "Ensalada 6",
            "Ensalada 7",
        ]
        descriptions = [
            "César con pollo $95",
            "Jitomate, Panela y Aguacate $90",
            "Vegetariana $85",
            "Arándano, almendra y queso cabra $95",
            "Manzana, almendra y pimientos $95",
            "Peras con nuez y queso azul $95",
            "Griega con queso feta $90",
        ]

        listReply = listReply_Message(
            number, options, descriptions, body, footer, "sed3", messageId
        )
        list.append(listReply)

    elif "chapata 1" in text:
        body = "Le gustaría agregar *Pollo con tocino y queso* por _$100_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("chapatas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Chapatas: Pollo con tocino y queso"
        precio = 100
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "chapata 2" in text:
        body = "Le gustaría agregar *Cecina con Vegetales* por _$100_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("chapatas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Chapatas: Cecina con Vegetales"
        precio = 100
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "chapata 3" in text:
        body = "Le gustaría agregar *Jamón Serrano* por _$120_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("chapatas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Chapatas: Jamón Serrano"
        precio = 120
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "chapata 4" in text:
        body = "Le gustaría agregar *Pollo con Chipotle* por _$100_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("chapatas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Chapatas: Pollo con Chipotle"
        precio = 100
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "chapata 5" in text:
        body = "Le gustaría agregar *Arrachera con guacamole* por _$125_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("chapatas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Chapatas: Arrachera con guacamole"
        precio = 125
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "chapata 6" in text:
        body = "Le gustaría agregar *De Pollo con Pesto y Feta* por _$120_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("chapatas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Chapatas: De Pollo con Pesto y Feta"
        precio = 120
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "chapata 7" in text:
        body = "Le gustaría agregar *Vegetariana* por _$90_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("chapatas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Chapatas: Vegetariana"
        precio = 90
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "sándwich 1" in text:
        body = "Le gustaría agregar *Club Sandwich* por _$95_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("sandwiches", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Sándwiches: Club Sandwich"
        precio = 95
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "sándwich 2" in text:
        body = "Le gustaría agregar *Panela con Jamón* por _$55_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("sandwiches", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Sándwiches: Panela con Jamón"
        precio = 55
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "pasta 1" in text:
        body = "Le gustaría agregar *Spaghetti boloñesa* por _$110_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("pastas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Pastas: Spaghetti boloñesa"
        precio = 110
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "pasta 2" in text:
        body = (
            "Le gustaría agregar *Vegetales con salsa de tomate* por _$95_ a su orden?"
        )
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("pastas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Pastas: Vegetales con salsa de tomate"
        precio = 95
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "pasta 3" in text:
        body = "Le gustaría agregar *Pechuga de pollo al pesto* por _$105_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("pastas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Pastas: Pechuga de pollo al pesto"
        precio = 105
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "pasta 4" in text:
        body = "Le gustaría agregar *Camarones arrabiata* por _$125_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("pastas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Pastas: Camarones arrabiata"
        precio = 125
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "pasta 5" in text:
        body = "Le gustaría agregar *Camarones a la crema con pimientos* por _$125_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("pastas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Pastas: Camarones a la crema con pimientos"
        precio = 125
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "pasta 6" in text:
        body = "Le gustaría agregar *Alfredo con pollo y champiñones* por _$105_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("pastas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Pastas: Alfredo con pollo y champiñones"
        precio = 105
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "especial 1" in text:
        body = "Le gustaría agregar *Alambre de arrachera* por _$125_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("especiales", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Especiales: Alambre de arrachera"
        precio = 125
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "especial 2" in text:
        body = "Le gustaría agregar *Parrillada de cecina* por _$115_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("especiales", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Especiales: Parrillada de cecina"
        precio = 115
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "especial 3" in text:
        body = "Le gustaría agregar *Arroz frito vegetariano* por _$85_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("especiales", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Especiales: Arroz frito vegetariano"
        precio = 85
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "especial 4" in text:
        body = "Le gustaría agregar *Arroz frito con res o pollo* por _$95_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("especiales", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Especiales: Arroz frito con res o pollo"
        precio = 95
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "ensalada 1" in text:
        body = "Le gustaría agregar *César con pollo* por _$95_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("ensaladas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Ensaladas: César con pollo"
        precio = 95
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "ensalada 2" in text:
        body = "Le gustaría agregar *Jitomate, Panela y Aguacate* por _$90_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("ensaladas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Ensaladas: Jitomate, Panela y Aguacate"
        precio = 90
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "ensalada 3" in text:
        body = "Le gustaría agregar *Vegetariana* por _$85_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("ensaladas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Ensaladas: Vegetariana"
        precio = 85
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "ensalada 4" in text:
        body = "Le gustaría agregar *Arándano, almendra y queso cabra* por _$95_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("ensaladas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Ensaladas: Arándano, almendra y queso cabra"
        precio = 95
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "ensalada 5" in text:
        body = (
            "Le gustaría agregar *Manzana, almendra y pimientos* por _$95_ a su orden?"
        )
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("ensaladas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Ensaladas: Manzana, almendra y pimientos"
        precio = 95
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "ensalada 6" in text:
        body = "Le gustaría agregar *Peras con nuez y queso azul* por _$95_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("ensaladas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Ensaladas: Peras con nuez y queso azul"
        precio = 95
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "ensalada 7" in text:
        body = "Le gustaría agregar *Griega con queso feta* por _$90_ a su orden?"
        footer = "Aurelia"
        options = ["✅ Si", "🚫 No"]

        imagen = get_media_id("ensaladas", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "😋")
        comida = "Ensaladas: Griega con queso feta"
        precio = 90
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "si" in text:
        body = "Le gustaría hacerlo *combo* por _+$30_? Esto incluye: Platillo + Agua + Papas o Ensalada"
        footer = "Aurelia"
        options = ["✅ Combo", "🚫 NOcombo"]

        imagen = get_media_id("combo", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "✅")
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "nocombo" in text:
        body = "Producto *sin* combo agregado, le gustaría agregar algo más?"
        footer = "Aurelia"
        options = ["✅ Volver al menu", "🚫 Terminar pedido"]

        imagen = get_media_id("agregado", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "🚫")
        pedido = anadir_pedido(pedido, comida)
        total = total + precio
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "combo" in text:
        body = "Producto *y combo* agregado, le gustaría agregar algo más?"
        footer = "Aurelia"
        options = ["✅ Volver al menu", "🚫 Terminar pedido"]

        imagen = get_media_id("agregado", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "✅")
        comida = comida + " + Combo"
        total = precio + 30
        pedido = anadir_pedido(pedido, comida)
        list.append(replyReaction)
        list.append(replyButtonData)

    elif "volver al menu" in text:
        body = "Tenemos varias áreas de consulta para elegir. ¿Cuál de estas secciones te gustaría explorar?"
        footer = "Aurelia"
        options = ["Chapatas", "Sándwiches", "Pastas", "Especiales", "Ensaladas"]
        descriptions = ["uno", "dos", "tres", "cuatro", "cinco"]

        listReply = listReply_Message(
            number, options, descriptions, body, footer, "sed2", messageId
        )
        list.append(listReply)

    elif "terminar pedido" in text:
        mydb = mysql.connector.connect(
            host="mysql-aurelia.alwaysdata.net",
            user="aurelia",
            password="",
            database="aurelia_chat",
        )

        mycursor = mydb.cursor()

        insert_query = "INSERT INTO registro (mensaje_recibido, id_wa, telefono_wa) VALUES (%s, %s, %s)"
        insert_data = (pedido, messageId, number)
        mycursor.execute(insert_query, insert_data)
        mydb.commit()
        print(mycursor.rowcount, "registro insertado")

        final = (
            "Te confirmo tu pedido:\n*"
            + pedido
            + "*\nCon un total de _$"
            + str(total)
            + "_"
        )
        data = text_Message(number, final)
        data2 = text_Message(number, "Te recordamos nuestra dirección:")
        direccion = locationReply_Message(number, messageId)
        list.append(data)
        list.append(data2)
        list.append(direccion)
        pedido = ""
        total = 0

    elif "no" in text:
        body = "No se ha agregado a su orden, ¿Qué quisiera revisar?"
        footer = "Aurelia"
        options = ["📖 Menu", "📅 Horarios"]

        imagen = get_media_id("noagregado", "image")
        replyButtonData = buttonReply_Message(
            number, imagen, options, body, footer, "sed1", messageId
        )
        replyReaction = replyReaction_Message(number, messageId, "🚫")
        list.append(replyReaction)
        list.append(replyButtonData)
        pedido = ""
        total = 0

    else:
        data = text_Message(
            number,
            "Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?",
        )
        list.append(data)

    for item in list:
        enviar_Mensaje_whatsapp(item)
