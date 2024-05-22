"""THE PARTY CATALOG"""

import logging
from google.oauth2 import service_account
from google.cloud import bigquery

__all__ = ["ThePartyCatalog"]

_logger = logging.getLogger(__name__)


class ThePartyCatalog(object):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_the_instance"):
            cls._the_instance = super().__new__(cls, *args, **kwargs)
            cls._is_already_configured: bool = False

        return cls._the_instance

    def __init__(self):
        if not self._is_already_configured:
            # TODO: use the default credentials?
            credentials_file = "../.secrets/mock_credentials.json"
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file, scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            #
            self._project_id = credentials.project_id
            self._client = bigquery.Client(credentials=credentials, project=self._project_id)
            #
            self._cache = {}
            #
            self._is_already_configured = True

    def __getitem__(self, key: str):
        return self.lookup(key)

    def lookup(self, gln: str):

        item = self._cache.get(gln)

        if item is None:

            _logger.info(msg=f"Cache MISS:{gln}")

            query = f"""SELECT gln, cuit, id_tipo_agente, nombre_tipo_agente FROM `{self._project_id}.orange.catalogo_electronico_by_gln` WHERE gln = @gln LIMIT 1000;"""
            job_config = bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("gln", "STRING", gln)])
            results = self._client.query_and_wait(query, job_config=job_config)  # Make an API request.

            n = results.total_rows
            if n > 1:
                _logger.warning(msg=f"Query return {n} results.")

            row = next(results)

            item = {"gln": row.gln, "cuit": row.cuit, "idTipoAgente": row.id_tipo_agente, "nombreTipoAgente": row.nombre_tipo_agente}

            self._cache[gln] = item.copy()

            item["cached"] = False

            _logger.debug("Cache size:%i", len(self._cache))
        else:
            _logger.debug(msg=f"Cache HIT:{gln}")

        return item

    def purge(self):
        # self._cache = {}
        pass
