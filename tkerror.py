""" """


class TkError(Exception):
    class MAR:
        ERROR_NULO = 0

        SERVICIO_FALTAN_ARGUMENTOS = 6001
        SERVICIO_RESULTADO_VACIO = 6002
        SERVICIO_METODO_INEXISTENTE = 6003
        TABLA_INEXISTENTE = 6004
        # no procesable
        EVENTO_NO_INFORMABLE = 7001

    def __init__(self, errorCode, errorArgs):
        self.errorCode = errorCode
        self.erroArgs = errorArgs
