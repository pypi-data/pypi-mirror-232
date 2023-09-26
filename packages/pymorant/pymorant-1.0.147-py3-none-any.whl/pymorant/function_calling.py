import openai
import json
from .llm import resumir_texto

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
                "municipio": {
                    "type": "string",
                    "description": "El municipio donde vive la persona e.g. Tuxtla Gutierrez, San Cristobal, Tonalá, Tapachula", # noqa
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

prompt_second_response = '''

    Tu papel como analista de texto es ser el asistente personal encargado de leer y analizar 
    mensajes recibidos de una persona. Tu objetivo principal es proporcionar respuestas lógicas y 
    coherentes basadas en los resultados generados por el function calling. En ningún caso debes inventar 
    información ni agregar detalles adicionales lo recibido del function_calling.

    Por ejemplo, no inventes comentarios adicionales a la solicitud de las personas.

    El cuerpo de tu resumen debe de ser de la siguiente manera:

        e.g.
        - *Remitente*: Jorge.\n
        -------------------------------------------------------\n
        - *Municipio*: Tapachula. \n
        -------------------------------------------------------\n
        - *Solicitud/Petición*: \n\n En su mensaje, se puede observar
        que está expresando su interés en apoyar al movimiento
        ya que busca abordar las irregularidades en el sistema
        educativo de su municipio y trabajar hacia una solución más justa e
        igualitaria. Subraya la importancia de la colaboración y un enfoque inclusivo
        para lograr este objetivo. Además, manifiesta su deseo de participar
        activamente en este proyecto. 
        Se observa que Jorge está dispuesto a discutir más formas de cómo podría
        contribuir a este cambio positivo con usted.

    No olvides que aunque no te proporcionen el nombre y el municipio, debes mencionar
    que no los proporcionó la persona que envía el mensaje o que los prefirió mantener
    de forma anónima/desconocida.
''' # noqa


class SolicitudInfo:
    def __init__(self, openai_api_key, modelo="gpt-4"):
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        self.modelo = modelo
        self.TOOLS = tools
        self.PROMPT_SECOND_RESPONSE = prompt_second_response

    def get_message_info(self, nombre, municipio, solicitud):

        instrucciones = "Eres el mejor analista de textos, se te comparte una \
        conversación que cuenta con una solicitud o petición de una persona y \
        tu objetivo es realizar un resumen lógico y conciso de la petición o \
        solicitud de la persona."

        solicitud = resumir_texto(
            lista_resumir=solicitud,
            openai_api_key=self.openai_api_key,
            instrucciones=instrucciones
        )

        output = f"El mensaje lo envía la persona: {nombre}.\
        La persona proviene del municipio de: {municipio}.\
        La solicitud/petición que realiza es la siguiente:\
        {solicitud}."

        return json.dumps(output)

    def answer(self, mensaje):

        response = openai.ChatCompletion.create(
            temperature=0,
            model=self.modelo,
            messages=[{"role": "user", "content": mensaje}],
            functions=self.TOOLS,
        )

        message = response["choices"][0]["message"]

        function_call = message.get("function_call")

        if function_call["arguments"] != "{}":
            function_name = function_call["name"]
            nombre = json.loads(function_call["arguments"]).get("nombre")
            municipio = json.loads(function_call["arguments"]).get("municipio") # noqa
            solicitud = json.loads(function_call["arguments"]).get("solicitud") # noqa
            function_response = self.get_message_info(
                nombre=nombre,
                municipio=municipio,
                solicitud=solicitud,
            )

            second_response = openai.ChatCompletion.create(
                temperature=0,
                model=self.modelo,
                messages=[
                    {
                        "role": "system",
                        "content": self.PROMPT_SECOND_RESPONSE
                    },
                    {
                        "role": "user", "content": mensaje
                    },
                    message,
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    },
                ],
            )

            ans = second_response["choices"][0]["message"].content

            return ans
        return '''Como requisito mínimo se necesita que proporciones
un mensaje lógico con una petición o solicitud. Vuelve a intentarlo, por favor.
No tengo permitido responder nada fuera del contexto de análisis de mensajes.
'''
