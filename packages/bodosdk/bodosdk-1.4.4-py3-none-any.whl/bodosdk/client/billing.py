from bodosdk.api.billing import BillingApi
from bodosdk.models.cluster import ClusterPriceExportResponse
from bodosdk.models.job import JobRunPriceExportResponse


class BillingClient:
    def __init__(self, api: BillingApi):
        self._api = api

    def get_cluster_price_export(
        self,
        started_at: str = None,
        finished_at: str = None,
        workspace_uuid: str = None,
    ) -> ClusterPriceExportResponse:
        """
        Get cluster price export
        :param workspace_uuid:
        :param started_at:
        :param finished_at:
        :return:
        """
        try:
            return self._api.get_cluster_price_export(
                started_at, finished_at, workspace_uuid
            )
        except Exception as exception:
            raise exception

    def get_job_run_price_export(
        self,
        started_at: str = None,
        finished_at: str = None,
        workspace_uuid: str = None,
    ) -> JobRunPriceExportResponse:
        """
        Get job run price export

        :param workspace_uuid:
        :param started_at:
        :param finished_at:
        :return:
        """
        try:
            return self._api.get_cluster_price_export(
                started_at, finished_at, workspace_uuid
            )
        except Exception as exception:
            raise exception
