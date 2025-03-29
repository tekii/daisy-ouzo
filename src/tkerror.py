""" """

from logging import INFO


class TkError(Exception):
    class MAR:
        ERROR_NULO = 0

        GLN_FORMATO_INVALIDO = 4002
        GTIN_FORMATO_INVALIDO = 4003
        CUIT_FORMATO_INVALIDO = 4004
        # services
        SERVICIO_FALTAN_ARGUMENTOS = 6001
        SERVICIO_RESULTADO_VACIO = 6002
        SERVICIO_METODO_INEXISTENTE = 6003
        TABLA_INEXISTENTE = 6004
        # no procesable
        EVENTO_NO_INFORMABLE = 7001
        SERIAL_PROCESSOR_PARSE_ERROR = 7003
        # business
        RESULTADOS_MULTIPLES = 9006

    def __init__(self, errorCode, errorArgs, code=400, level=INFO):
        self.errorCode = errorCode
        self.errorArgs = errorArgs
        self.code = code
        self.level = level
