"""THE PARTY CATALOG"""

import logging

from google.auth import default as default_credentials
from google.cloud import bigquery

from tkerror import TkError

__all__ = ["ThePartyCatalog"]


class ThePartyCatalog(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_the_instance"):
            cls._the_instance = super().__new__(cls, *args, **kwargs)
            cls._is_already_configured: bool = False

        return cls._the_instance

    def __init__(self):
        if not self._is_already_configured:
            #
            credentials, self._project_id = default_credentials(
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            self._client = bigquery.Client(credentials=credentials, project=self._project_id)
            #
            self._cache = {}
            #
            self._is_already_configured = True

    def __getitem__(self, key: str):
        return self.lookup(key)

    def lookup(self, gln: str, cuit: str):

        item = self._cache.get(gln)

        if item is None:

            logging.info(msg=f"PartyLookup - Cache MISS -{gln}-{cuit}-")

            query = f"""
            SELECT gln, cuit, id_tipo_agente, nombre_tipo_agente FROM
              `{self._project_id}.orange.catalogo_electronico_by_gln` WHERE
            CASE
              WHEN @gln IS NOT NULL AND @cuit IS NOT NULL THEN gln = @gln AND cuit = @cuit
              WHEN @gln IS NOT NULL AND @cuit IS NULL THEN gln = @gln
              WHEN @gln IS NULL AND @cuit IS NOT NULL THEN cuit = @cuit
              ELSE FALSE
            END LIMIT 10;"""
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("gln", "STRING", gln),
                    bigquery.ScalarQueryParameter("cuit", "STRING", cuit),
                ]
            )
            results = self._client.query_and_wait(
                query, job_config=job_config
            )  # Make an API request.

            n = results.total_rows

            if n == 0:
                return None

            if n > 1:
                raise TkError(
                    errorCode=TkError.MAR.RESULTADOS_MULTIPLES,
                    errorArgs={
                        "origen": ["PartyLookup"],
                        "message": [f"PartyLookup -{gln}-{cuit}- returns multiple ({n}) results"],
                    },
                )

            row = next(results)

            item = {
                "gln": row.gln,
                "cuit": row.cuit,
                "idTipoAgente": row.id_tipo_agente,
                "nombreTipoAgente": row.nombre_tipo_agente,
            }

            self._cache[gln] = item.copy()

            item["cached"] = False

            logging.debug(msg=f"PartyLookup - Cache SIZE -{len(self._cache)}")
        else:
            logging.debug(msg=f"PartyLookup - Cache HIT -{gln}-")

        return item

    def purge(self):
        # self._cache = {}
        pass
