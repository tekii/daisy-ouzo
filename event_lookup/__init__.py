"""EVENT LOOKUP"""

from tkerror import TkError
from .event import TYPE, EVENTS


def event_lookup(movimiento, file):

    if not movimiento:
        raise TkError(
            errorCode=TkError.MAR.SERVICIO_FALTAN_ARGUMENTOS,
            errorArgs={
                "origen": ["EventLookup"],
                "argumentos": ["actor", "file"],
                "valores": ["TUTEUR", file],
                "message": ["Some error message."],
            },
        )

    match int(movimiento):

        case 7 | 25:
            evento_id = TYPE.DISTRIBUCION_DEL_PRODUCTO_A_UN_ESLABON_POSTERIOR

        case 24:
            evento_id = TYPE.RECEPCION_DE_PRODUCTO_DESDE_UN_ESLABON_ANTERIOR

        case 13:
            evento_id = TYPE.ENVIO_TRASLADO_ENTRE_DEPOSITOS_PROPIOS

        case 31 | 99:
            evento_id = TYPE.ENVIO_DE_PRODUCTO_EN_CARACTER_DEVOLUCION

        case 65:
            evento_id = TYPE.ENVIO_DE_PRODUCTO_EN_CARACTER_DEVOLUCION_POR_VENCIMIENTO

        case 9 | 59:
            evento_id = TYPE.RECEPCION_DE_PRODUCTO_EN_CARACTER_DE_DEVOLUCION

        case 6:
            evento_id = TYPE.MUESTRA_MEDICA

        case 22:
            evento_id = TYPE.PRODUCTO_DESTINADO_A_EXPORTACION

        case 27 | 49:
            evento_id = TYPE.PRODUCTO_DESTINADO_A_ENSAYO_CLINICO

        case 35 | 42 | 43 | 44 | 45 | 46 | 47 | 48 | 40 | 5:
            evento_id = TYPE.PUESTA_EN_CONTRAMUESTRA_DE_RETENCION

        case 11:
            evento_id = TYPE.DESTRUCCION_DE_MEDICAMENTO_POR_VENCIMIENTO

        case 2:
            evento_id = TYPE.LEVANTAMIENTO_DE_CUARENTENA

        case 63:
            evento_id = TYPE.ENVIO_DE_MERCADERIA_EN_CARACTER_DE_CUARENTENA

        case 18:
            evento_id = TYPE.PRODUCTO_ROBADO_EXTRAVIADO

        case 20 | 4 | 16:
            evento_id = TYPE.CODIGO_DETERIORADO_DESTRUIDO

        case 64:
            evento_id = TYPE.RECEPCION_DE_PRODUCTO_EN_CARACTER_DE_DEVOLUCION_POR_VENCIMIENTO

        case 28:
            raise TkError(
                errorCode=TkError.MAR.EVENTO_NO_INFORMABLE,
                errorArgs={"origen": [__name__], "argumentos": ["actor", "motivo"], "valores": ["TUTEUR", movimiento]},
            )

        case _:
            raise TkError(
                errorCode=TkError.MAR.SERVICIO_RESULTADO_VACIO,
                errorArgs={
                    "origen": [__name__],
                    "argumentos": ["actor", "file"],
                    "valores": ["TUTEUR", file],
                    "mensaje": ["No se reconoce el movimiento"],
                },
            )

    try:
        e = EVENTS[evento_id]
        detalle = e["detalle"]
    except KeyError:
        detalle = "no detalle"

    return {"id": evento_id, "descripcion": detalle}
