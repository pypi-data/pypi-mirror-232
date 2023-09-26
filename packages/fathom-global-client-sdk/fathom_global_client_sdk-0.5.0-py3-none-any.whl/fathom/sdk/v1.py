import dataclasses
import logging
import os
from typing import List, Optional

import requests
from protoc_gen_validate.validator import validate_all

from proto.fathom import fathom_pb2, fathom_pb2_grpc
from proto.geo import geo_pb2
from proto.portfolio import portfolio_pb2, portfolio_pb2_grpc

from .client import BaseClient
from .common import (
    FathomException,
    PathOrString,
    TaskNotCompleteException,
    write_tiff_data_to_file,
)

log = logging.getLogger(__name__)


class Client(BaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.geo: "GeoClient" = GeoClient(self)
        self.get_points = self.geo.get_points
        self.get_polygon = self.geo.get_polygon
        self.get_with_shapefile = self.geo.get_with_shapefile

        self.portfolio: "PortfolioClient" = PortfolioClient(self)


@dataclasses.dataclass
class PortfolioClient:
    """Sub-client for interacting with portfolios

    Example:
        ```python
        import time

        import fathom
        from fathom import portfolio_pb2

        client = fathom.Client(...)
        layer_ids = [...]

        create_resp = client.portfolio.create_task(layer_ids)

        client.portfolio.upload_portfolio_csv(create_resp.upload_url, "/path/to/input.csv")

        for i in range(100):
            time.sleep(10)

            status = client.portfolio.task_status(create_resp.task_id)
            if status.task_status == portfolio_pb2.TASK_STATUS_COMPLETE:
                break
            elif status.task_status == portfolio_pb2.TASK_STATUS_ERROR:
                raise Exception(f"task failed: {status}")
        else:
            raise Exception("task was not ready in time")

        bytes_read = client.portfolio.attempt_task_result_download(
            create_resp.task_id, "/path/to/output.csv"
        )
        ```
    """

    base_client: "BaseClient"

    def _service_stub(self) -> portfolio_pb2_grpc.PortfolioServiceStub:
        return self.base_client._get_stub(portfolio_pb2_grpc.PortfolioServiceStub)

    def create_task(
        self, layer_ids: List[str], project_id: Optional[str] = None
    ) -> portfolio_pb2.CreatePortfolioTaskResponse:
        """Create a new portfolio task

        Args:
            layer_ids: Layer IDs to use for task
        """

        metadata = _metadata_from_project_id(project_id)
        request = portfolio_pb2.CreatePortfolioTaskRequest(
            layer_ids=layer_ids, metadata=metadata
        )

        validate_all(request)

        log.debug("Creating new portfolio task")

        return self._service_stub().CreatePortfolioTask(request)

    def task_status(self, task_id: str) -> portfolio_pb2.PortfolioStatusResponse:
        """Gets the status of an existing portfolio task

        Args:
            task_id: ID of previously create portfolio task
        """

        request = portfolio_pb2.PortfolioStatusRequest(
            task_id=task_id,
        )

        validate_all(request)

        log.debug(f"Getting status of task '{task_id}")

        return self._service_stub().GetPortfolioTaskStatus(request)

    def attempt_task_result_download(
        self, task_id: str, output_path: PathOrString, chunk_size: int = 1000
    ) -> int:
        """Attempts to download the result of a given task. Should only be called after a call to
        `task_status` has indicated that the task completed without errors, otherwise an
        exception will be raised.

        Args:
            task_id: ID of previously create portfolio task
            output_path: Name of file to download output in to. Will be OVERWRITTEN if it already exists.
            chunk_size: Override chunk size when downloading CSV

        Returns:
            Number of bytes downloaded

        Raises:
            FathomException: Task was not ready or there were errors during processing
        """

        task_status = self.task_status(task_id)
        if not task_status.task_status == portfolio_pb2.TASK_STATUS_COMPLETE:
            raise TaskNotCompleteException(
                f"Expected task {task_id} to be COMPLETE, but was {task_status.task_status}"
            )

        log.debug(f"Downloading results of portfolio task to {output_path}")

        bytes_read = 0

        # stream response to avoid having to download hundreds of MB into memory first
        with open(output_path, "wb") as output_file:
            streaming_resp = requests.api.get(task_status.download_url, stream=True)

            for chunk in streaming_resp.iter_content(chunk_size):
                output_file.write(chunk)
                bytes_read += len(chunk)

        return bytes_read

    @staticmethod
    def upload_portfolio_csv(upload_url: str, input_path: PathOrString):
        """Uploads the given portfolio CSV file for the portfolio task

        Args:
            upload_url: upload url from a previous CreatePortfolioTaskResponse
            input_path: path to CSV file to upload
        """

        log.debug(f"Uploading portfolio input from {input_path}")

        with open(input_path, "rb") as csv_file:
            size = os.path.getsize(input_path)
            extra_headers = {
                "content-length": str(size),
                "content-type": "text/csv",
                "x-goog-content-length-range": "0,524288000",
            }
            resp = requests.api.put(
                url=upload_url, data=csv_file, headers=extra_headers, timeout=1
            )

        if resp.status_code != 200:
            raise FathomException(f"Error uploading CSV: {resp}")


@dataclasses.dataclass
class GeoClient:
    """A sub-client for synchronously fetching data for points or polygons."""

    base_client: "BaseClient"

    def _service_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        return self.base_client._get_stub(fathom_pb2_grpc.FathomServiceStub)

    def get_points(
        self,
        points: geo_pb2.MultiPoint,
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetDataResponse:
        """Returns data pertaining to a list of lat-lng coordinates.

        Args:
            points: A list of points.

            layer_ids: The identifiers of the types of data being requested.

            project_id: string
        """

        request = fathom_pb2.GetDataRequest(
            points=points,
            layers=fathom_pb2.Layers(
                layer_ids=fathom_pb2.Layers.Identifiers(
                    ids=layer_ids,
                ),
            ),
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetData(request)

    def get_polygon(
        self,
        polygon: geo_pb2.Polygon,
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetDataResponse:
        """Returns data pertaining to a polygon coordinates.

        Args:
            polygon: The bounding points of an area for which data are requested.
                The first and last point MUST be the same, and the loop MUST be in a
                counterclockwise direction (i.e. on the left-hand side of an observer
                walking along the boundary).
            layer_ids: The identifiers of the types of data being requested.
            project_id: string
        """
        request = fathom_pb2.GetDataRequest(
            polygon=polygon,
            layers=fathom_pb2.Layers(
                layer_ids=fathom_pb2.Layers.Identifiers(
                    ids=layer_ids,
                ),
            ),
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetData(request)

    def polygon_stats(
        self,
        polygon: geo_pb2.Polygon,
        layer_ids: List[str],
        project_id: Optional[str] = None,
    ) -> fathom_pb2.GetPolygonStatsResponse:
        """Returns statistics about polygons using the given layer_ids

        This is similar to the get_polygons method, but will only return statistics about the polygon,
        not the polygon itself. to see what statistics are returned, see [the gRPC documentation](
        ../compile_proto_docs.md#polygonstats_1)

        Args:
            polygon: The bounding points of an area for which data are requested.
                The first and last point MUST be the same, and the loop MUST be in a
                counterclockwise direction (i.e. on the left-hand side of an observer
                walking along the boundary).
            layer_ids: The identifiers of the types of data being requested.
            project_id: string
        """

        request = fathom_pb2.GetPolygonStatsRequest(
            polygon=polygon,
            layers=fathom_pb2.Layers(
                layer_ids=fathom_pb2.Layers.Identifiers(
                    ids=layer_ids,
                ),
            ),
            metadata=_metadata_from_project_id(project_id),
        )

        validate_all(request)

        return self._service_stub().GetPolygonStats(request)

    def get_with_shapefile(
        self, file: str, layer_ids: List[str], project_id: Optional[str] = None
    ) -> fathom_pb2.GetDataResponse:
        """Returns data pertaining to a polygon coordinates from a shapefile.

        Args:
            file: The shapefile containing geometries requested. Only Point,
                MultiPoint, and Polygon are supported.
            layer_ids: The identifiers of the types of data being requested.
            project_id: string
        """
        with open(file, "rb") as f:
            request = fathom_pb2.GetDataRequest(
                shp_file=f.read(),
                layers=fathom_pb2.Layers(
                    layer_ids=fathom_pb2.Layers.Identifiers(
                        ids=layer_ids,
                    ),
                ),
                metadata=_metadata_from_project_id(project_id),
            )

        validate_all(request)

        return self._service_stub().GetData(request)


def _metadata_from_project_id(
    project_id: Optional[str],
) -> Optional[dict[str, str]]:
    return {"project_id": project_id} if project_id else None


def point(lat: float, lng: float) -> geo_pb2.Point:
    """Returns a Point object for use with Client.get_point()."""
    return geo_pb2.Point(
        latitude=lat,
        longitude=lng,
    )


def points(points: List[geo_pb2.Point]) -> geo_pb2.MultiPoint:
    """Returns a MultiPoint object for use with Client.get_points()."""
    return geo_pb2.MultiPoint(points=points)


def line_string(points: List[geo_pb2.Point]) -> geo_pb2.LineString:
    """Returns a LineString object for use with polygon()."""
    return geo_pb2.LineString(points=points)


def simple_polygon(points: List[geo_pb2.Point]) -> geo_pb2.Polygon:
    """Returns a Polygon object for use with Client.get_polygon()."""
    return geo_pb2.Polygon(
        lines=[
            line_string(points),
        ]
    )


def write_tiffs(
    response: fathom_pb2.GetDataResponse,
    output_dir: PathOrString,
    *,
    pattern: str = "{layer_id}-{tiff_num}.tif",
):
    """Given a data response, write any polygon tiffs in the response to the output directory.

    Args:
        response: A response from a `get_polygon` request
        output_dir: the directory to write the tiff data to
        pattern: The pattern to save the file as. Formatted using normal Python string formatting,
            with the only available key being :
                - 'layer_id': the layer id
                - 'tiff_num': The index of the tiff in the get data response for the layer
                - 'sep': The os-specific directory separator
    """

    data: fathom_pb2.Data
    for layer_id, data in response.results.items():
        if data.code or data.values or (not data.polygons.geo_tiffs):
            raise FathomException(
                "Tried to write tiffs from a response that contained no polygons"
            )

        for tiff_num, geotiff in enumerate(data.polygons.geo_tiffs):
            write_tiff_data_to_file(geotiff, layer_id, output_dir, pattern, tiff_num)
