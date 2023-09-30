import openai
import json
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage

prompt_second_response = '''Tu papel como analista de texto es ser el
    asistente personal encargado de leer y analizar mensajes recibidos de una
    persona. Tu objetivo principal es proporcionar respuestas lógicas y
    coherentes basadas en los resultados generados por el function calling.
    En ningún caso debes inventar información ni agregar detalles
    adicionales lo recibido del function_calling.

    Por ejemplo, no inventes comentarios adicionales a la solicitud de las
    personas.

    El cuerpo de tu resumen debe de ser de la siguiente manera:

    e.g.
    - *Remitente*: Jorge.\n
    -------------------------------------------------------\n
    - *Ubicación*: Tapachula. \n
    -------------------------------------------------------\n
    - *Solicitud/Petición*: \n\n En su mensaje, se observa
    que está expresando su interés en apoyar al movimiento
    ya que busca abordar las irregularidades en el sistema
    educativo de su municipio y trabajar hacia una solución más justa e
    igualitaria. Manifiesta su deseo de participar en este proyecto y está
    dispuesto a discutir más formas de cómo podría contribuir a este cambio con
    usted.

    Recuerda que la Solicitud/Petición debe tener menos contenido que el
    mensaje original.

    No olvides que aunque no te proporcionen el nombre y el municipio, debes
     mencionar que no los proporcionó la persona que envía el mensaje o que
    los prefirió mantener de forma anónima/desconocida.
    '''

tools = [
            {
                "name": "get_message_info",
                "description": "Devuelve un resumen del texto recibido con una estructura definida.", # noqa
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre": {
                            "type": "string",
                            "description": "El nombre de la persona que envía el mensaje e.g. Juan, Pedro, Fernando.", # noqa
                        },
                        "ubicacion": {
                            "type": "string",
                            "description": "La ubicación donde vive la persona e.g. Tuxtla Gutierrez, San Cristobal, Tonalá, Tapachula", # noqa
                        },
                        "solicitud": {
                            "type": "string",
                            "description": "La solicitud/petición de la persona e.g necesito comentarle que quisiera unirme al apoyo del movimiento, quiero decirle que hay problemas en el municipio de inseguridad y etc.", # noqa
                        },
                    },
                    "required": ["solicitud"],
                },
            },
       ]


class SolicitudInfo:
    def __init__(self, openai_api_key, modelo="gpt-4"):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.modelo = modelo
        self.TOOLS = tools
        self.PROMPT_SECOND_RESPONSE = prompt_second_response

    def get_message_info(self, nombre, ubicacion, solicitud):

        output = f"El mensaje lo envía la persona: {nombre}.\
        La persona proviene de la ubicación de: {ubicacion}.\
        La solicitud/petición que realiza es la siguiente:\
        {solicitud}."

        return json.dumps(output)

    def answer(self, mensaje, chat_history=[]):

        msg_error = '''Como requisito mínimo se necesita que proporciones un
        mensaje lógico con una petición o solicitud. Vuelve a intentarlo, por
        favor. No tengo permitido responder nada fuera del contexto de análisis
        de mensajes.
        '''

        llm = ChatOpenAI(model=self.modelo, temperature=0, openai_api_key=self.openai_api_key) # noqa

        message = llm.predict_messages([ChatMessage(
            role="system",
            content=str(chat_history)
            ),
            HumanMessage(content=mensaje)],
            functions=self.TOOLS,
            )

        try:

            function_call = message.additional_kwargs["function_call"]

            if function_call["name"] == "get_message_info":
                nombre = json.loads(function_call["arguments"]).get("nombre")
                ubicacion = json.loads(function_call["arguments"]).get("ubicacion") # noqa
                solicitud = json.loads(function_call["arguments"]).get("solicitud") # noqa

                function_response = self.get_message_info(
                    nombre=nombre,
                    ubicacion=ubicacion,
                    solicitud=solicitud,
                  )

                second_response = llm.predict_messages(
                  [
                      HumanMessage(content=mensaje),
                      AIMessage(content=self.PROMPT_SECOND_RESPONSE),
                      AIMessage(content=str(message.additional_kwargs)),
                      ChatMessage(
                          role="function",
                          additional_kwargs={
                              "name": function_call["name"]
                          },
                          content=function_response
                      ),
                  ],
                  functions=self.TOOLS,
                )

                return second_response.content
            else:
                print(msg_error)
        except: # noqa
            print(msg_error)


if __name__ == '__main__':

    openai_api_key = "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"

    solicitudInfo = SolicitudInfo(openai_api_key)

    solicitud = '''Mi nombre es Roberto. Me gustaría discutir el tema de los programas sociales y su impacto en nuestras comunidades. ¿Qué opina sobre la efectividad de estos programas para mejorar la calidad de vida de nuestros compatriotas?''' # noqa

    answer = solicitudInfo.answer(solicitud)

    print(answer)
