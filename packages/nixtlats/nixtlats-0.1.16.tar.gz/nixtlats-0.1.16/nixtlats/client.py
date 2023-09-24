# This file was auto-generated by Fern from our API Definition.

import typing
import urllib.parse
from json.decoder import JSONDecodeError

import httpx
import pydantic

from .core.api_error import ApiError
from .core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from .core.jsonable_encoder import jsonable_encoder
from .errors.unprocessable_entity_error import UnprocessableEntityError
from .types.http_validation_error import HttpValidationError
from .types.multi_series_input import MultiSeriesInput
from .types.single_series_forecast import SingleSeriesForecast

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class Nixtla:
    def __init__(
        self, *, base_url: str, token: typing.Union[str, typing.Callable[[], str]], timeout: typing.Optional[float] = 60
    ):
        self._client_wrapper = SyncClientWrapper(
            base_url=base_url, token=token, httpx_client=httpx.Client(timeout=timeout)
        )

    def timegpt(self, *, request: SingleSeriesForecast) -> typing.Any:
        """
        Parameters:
            - request: SingleSeriesForecast.
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt"),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def timegpt_historic(
        self,
        *,
        freq: typing.Optional[str] = OMIT,
        level: typing.Optional[typing.List[typing.Any]] = OMIT,
        y: typing.Optional[typing.Any] = OMIT,
        x: typing.Optional[typing.Any] = OMIT,
        clean_ex_first: typing.Optional[bool] = OMIT,
    ) -> typing.Any:
        """
        Parameters:
            - freq: typing.Optional[str]. The frequency of the data represented as a string. 'D' for daily, 'M' for monthly, 'H' for hourly, and 'W' for weekly frequencies are available.

            - level: typing.Optional[typing.List[typing.Any]]. A list of values representing the prediction intervals. Each value is a percentage that indicates the level of certainty for the corresponding prediction interval. For example, [80, 90] defines 80% and 90% prediction intervals.

            - y: typing.Optional[typing.Any].

            - x: typing.Optional[typing.Any].

            - clean_ex_first: typing.Optional[bool]. A boolean flag that indicates whether the API should preprocess (clean) the exogenous signal before applying the large time model. If True, the exogenous signal is cleaned; if False, the exogenous variables are applied after the large time model.
        """
        _request: typing.Dict[str, typing.Any] = {}
        if freq is not OMIT:
            _request["freq"] = freq
        if level is not OMIT:
            _request["level"] = level
        if y is not OMIT:
            _request["y"] = y
        if x is not OMIT:
            _request["x"] = x
        if clean_ex_first is not OMIT:
            _request["clean_ex_first"] = clean_ex_first
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_historic"),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def timegpt_multi_series(
        self,
        *,
        freq: typing.Optional[str] = OMIT,
        level: typing.Optional[typing.List[typing.Any]] = OMIT,
        fh: typing.Optional[int] = OMIT,
        y: typing.Optional[typing.Any] = OMIT,
        x: typing.Optional[MultiSeriesInput] = OMIT,
        clean_ex_first: typing.Optional[bool] = OMIT,
        finetune_steps: typing.Optional[int] = OMIT,
    ) -> typing.Any:
        """
        Parameters:
            - freq: typing.Optional[str]. The frequency of the data represented as a string. 'D' for daily, 'M' for monthly, 'H' for hourly, and 'W' for weekly frequencies are available.

            - level: typing.Optional[typing.List[typing.Any]]. A list of values representing the prediction intervals. Each value is a percentage that indicates the level of certainty for the corresponding prediction interval. For example, [80, 90] defines 80% and 90% prediction intervals.

            - fh: typing.Optional[int]. The forecasting horizon. This represents the number of time steps into the future that the forecast should predict.

            - y: typing.Optional[typing.Any].

            - x: typing.Optional[MultiSeriesInput]. The exogenous  variables provided as a dictionary of two colums: columns and data. The columns contains the columns of the dataframe and data contains eaach data point. For example: {"columns": ["unique_id", "ds", "ex_1", "ex_2"], "data": [["ts_0", "2021-01-01", 0.2, 0.67], ["ts_0", "2021-01-02", 0.4, 0.7]}. This should also include forecasting horizon (fh) additional timestamps for each unique_id to calculate the future values.

            - clean_ex_first: typing.Optional[bool]. A boolean flag that indicates whether the API should preprocess (clean) the exogenous signal before applying the large time model. If True, the exogenous signal is cleaned; if False, the exogenous variables are applied after the large time model.

            - finetune_steps: typing.Optional[int]. The number of tuning steps used to train the large time model on the data. Set this value to 0 for zero-shot inference, i.e., to make predictions without any further model tuning.
        """
        _request: typing.Dict[str, typing.Any] = {}
        if freq is not OMIT:
            _request["freq"] = freq
        if level is not OMIT:
            _request["level"] = level
        if fh is not OMIT:
            _request["fh"] = fh
        if y is not OMIT:
            _request["y"] = y
        if x is not OMIT:
            _request["x"] = x
        if clean_ex_first is not OMIT:
            _request["clean_ex_first"] = clean_ex_first
        if finetune_steps is not OMIT:
            _request["finetune_steps"] = finetune_steps
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_multi_series"),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def timegpt_multi_series_historic(
        self,
        *,
        freq: typing.Optional[str] = OMIT,
        level: typing.Optional[typing.List[typing.Any]] = OMIT,
        y: typing.Optional[typing.Any] = OMIT,
        x: typing.Optional[MultiSeriesInput] = OMIT,
        clean_ex_first: typing.Optional[bool] = OMIT,
    ) -> typing.Any:
        """
        Parameters:
            - freq: typing.Optional[str]. The frequency of the data represented as a string. 'D' for daily, 'M' for monthly, 'H' for hourly, and 'W' for weekly frequencies are available.

            - level: typing.Optional[typing.List[typing.Any]]. A list of values representing the prediction intervals. Each value is a percentage that indicates the level of certainty for the corresponding prediction interval. For example, [80, 90] defines 80% and 90% prediction intervals.

            - y: typing.Optional[typing.Any].

            - x: typing.Optional[MultiSeriesInput]. The exogenous  variables provided as a dictionary of two colums: columns and data. The columns contains the columns of the dataframe and data contains eaach data point. For example: {"columns": ["unique_id", "ds", "ex_1", "ex_2"], "data": [["ts_0", "2021-01-01", 0.2, 0.67], ["ts_0", "2021-01-02", 0.4, 0.7]}. This should also include forecasting horizon (fh) additional timestamps for each unique_id to calculate the future values.

            - clean_ex_first: typing.Optional[bool]. A boolean flag that indicates whether the API should preprocess (clean) the exogenous signal before applying the large time model. If True, the exogenous signal is cleaned; if False, the exogenous variables are applied after the large time model.
        """
        _request: typing.Dict[str, typing.Any] = {}
        if freq is not OMIT:
            _request["freq"] = freq
        if level is not OMIT:
            _request["level"] = level
        if y is not OMIT:
            _request["y"] = y
        if x is not OMIT:
            _request["x"] = x
        if clean_ex_first is not OMIT:
            _request["clean_ex_first"] = clean_ex_first
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_multi_series_historic"),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def timegpt_multi_series_anomalies(
        self,
        *,
        freq: typing.Optional[str] = OMIT,
        level: typing.Optional[typing.List[typing.Any]] = OMIT,
        y: typing.Optional[typing.Any] = OMIT,
        x: typing.Optional[MultiSeriesInput] = OMIT,
        clean_ex_first: typing.Optional[bool] = OMIT,
    ) -> typing.Any:
        """
        Parameters:
            - freq: typing.Optional[str]. The frequency of the data represented as a string. 'D' for daily, 'M' for monthly, 'H' for hourly, and 'W' for weekly frequencies are available.

            - level: typing.Optional[typing.List[typing.Any]]. Specifies the confidence level for the prediction interval used in anomaly detection. It is represented as a percentage between 0 and 100. For instance, a level of 95 indicates that the generated prediction interval captures the true future observation 95% of the time. Any observed values outside of this interval would be considered anomalies. A higher level leads to wider prediction intervals and potentially fewer detected anomalies, whereas a lower level results in narrower intervals and potentially more detected anomalies. Default: 99.

            - y: typing.Optional[typing.Any].

            - x: typing.Optional[MultiSeriesInput]. The exogenous  variables provided as a dictionary of two colums: columns and data. The columns contains the columns of the dataframe and data contains eaach data point. For example: {"columns": ["unique_id", "ds", "ex_1", "ex_2"], "data": [["ts_0", "2021-01-01", 0.2, 0.67], ["ts_0", "2021-01-02", 0.4, 0.7]}. This should also include forecasting horizon (fh) additional timestamps for each unique_id to calculate the future values.

            - clean_ex_first: typing.Optional[bool]. A boolean flag that indicates whether the API should preprocess (clean) the exogenous signal before applying the large time model. If True, the exogenous signal is cleaned; if False, the exogenous variables are applied after the large time model.
        """
        _request: typing.Dict[str, typing.Any] = {}
        if freq is not OMIT:
            _request["freq"] = freq
        if level is not OMIT:
            _request["level"] = level
        if y is not OMIT:
            _request["y"] = y
        if x is not OMIT:
            _request["x"] = x
        if clean_ex_first is not OMIT:
            _request["clean_ex_first"] = clean_ex_first
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_multi_series_anomalies"),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def timegpt_input_size(self, *, request: SingleSeriesForecast) -> typing.Any:
        """
        Parameters:
            - request: SingleSeriesForecast.
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_input_size"),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def timegpt_model_params(self, *, request: SingleSeriesForecast) -> typing.Any:
        """
        Parameters:
            - request: SingleSeriesForecast.
        """
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_model_params"),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def validate_token(self) -> typing.Any:
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "validate_token"),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    def validate_token_front(self) -> typing.Any:
        _response = self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "validate_token_front"),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)


class AsyncNixtla:
    def __init__(
        self, *, base_url: str, token: typing.Union[str, typing.Callable[[], str]], timeout: typing.Optional[float] = 60
    ):
        self._client_wrapper = AsyncClientWrapper(
            base_url=base_url, token=token, httpx_client=httpx.AsyncClient(timeout=timeout)
        )

    async def timegpt(self, *, request: SingleSeriesForecast) -> typing.Any:
        """
        Parameters:
            - request: SingleSeriesForecast.
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt"),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def timegpt_historic(
        self,
        *,
        freq: typing.Optional[str] = OMIT,
        level: typing.Optional[typing.List[typing.Any]] = OMIT,
        y: typing.Optional[typing.Any] = OMIT,
        x: typing.Optional[typing.Any] = OMIT,
        clean_ex_first: typing.Optional[bool] = OMIT,
    ) -> typing.Any:
        """
        Parameters:
            - freq: typing.Optional[str]. The frequency of the data represented as a string. 'D' for daily, 'M' for monthly, 'H' for hourly, and 'W' for weekly frequencies are available.

            - level: typing.Optional[typing.List[typing.Any]]. A list of values representing the prediction intervals. Each value is a percentage that indicates the level of certainty for the corresponding prediction interval. For example, [80, 90] defines 80% and 90% prediction intervals.

            - y: typing.Optional[typing.Any].

            - x: typing.Optional[typing.Any].

            - clean_ex_first: typing.Optional[bool]. A boolean flag that indicates whether the API should preprocess (clean) the exogenous signal before applying the large time model. If True, the exogenous signal is cleaned; if False, the exogenous variables are applied after the large time model.
        """
        _request: typing.Dict[str, typing.Any] = {}
        if freq is not OMIT:
            _request["freq"] = freq
        if level is not OMIT:
            _request["level"] = level
        if y is not OMIT:
            _request["y"] = y
        if x is not OMIT:
            _request["x"] = x
        if clean_ex_first is not OMIT:
            _request["clean_ex_first"] = clean_ex_first
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_historic"),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def timegpt_multi_series(
        self,
        *,
        freq: typing.Optional[str] = OMIT,
        level: typing.Optional[typing.List[typing.Any]] = OMIT,
        fh: typing.Optional[int] = OMIT,
        y: typing.Optional[typing.Any] = OMIT,
        x: typing.Optional[MultiSeriesInput] = OMIT,
        clean_ex_first: typing.Optional[bool] = OMIT,
        finetune_steps: typing.Optional[int] = OMIT,
    ) -> typing.Any:
        """
        Parameters:
            - freq: typing.Optional[str]. The frequency of the data represented as a string. 'D' for daily, 'M' for monthly, 'H' for hourly, and 'W' for weekly frequencies are available.

            - level: typing.Optional[typing.List[typing.Any]]. A list of values representing the prediction intervals. Each value is a percentage that indicates the level of certainty for the corresponding prediction interval. For example, [80, 90] defines 80% and 90% prediction intervals.

            - fh: typing.Optional[int]. The forecasting horizon. This represents the number of time steps into the future that the forecast should predict.

            - y: typing.Optional[typing.Any].

            - x: typing.Optional[MultiSeriesInput]. The exogenous  variables provided as a dictionary of two colums: columns and data. The columns contains the columns of the dataframe and data contains eaach data point. For example: {"columns": ["unique_id", "ds", "ex_1", "ex_2"], "data": [["ts_0", "2021-01-01", 0.2, 0.67], ["ts_0", "2021-01-02", 0.4, 0.7]}. This should also include forecasting horizon (fh) additional timestamps for each unique_id to calculate the future values.

            - clean_ex_first: typing.Optional[bool]. A boolean flag that indicates whether the API should preprocess (clean) the exogenous signal before applying the large time model. If True, the exogenous signal is cleaned; if False, the exogenous variables are applied after the large time model.

            - finetune_steps: typing.Optional[int]. The number of tuning steps used to train the large time model on the data. Set this value to 0 for zero-shot inference, i.e., to make predictions without any further model tuning.
        """
        _request: typing.Dict[str, typing.Any] = {}
        if freq is not OMIT:
            _request["freq"] = freq
        if level is not OMIT:
            _request["level"] = level
        if fh is not OMIT:
            _request["fh"] = fh
        if y is not OMIT:
            _request["y"] = y
        if x is not OMIT:
            _request["x"] = x
        if clean_ex_first is not OMIT:
            _request["clean_ex_first"] = clean_ex_first
        if finetune_steps is not OMIT:
            _request["finetune_steps"] = finetune_steps
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_multi_series"),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def timegpt_multi_series_historic(
        self,
        *,
        freq: typing.Optional[str] = OMIT,
        level: typing.Optional[typing.List[typing.Any]] = OMIT,
        y: typing.Optional[typing.Any] = OMIT,
        x: typing.Optional[MultiSeriesInput] = OMIT,
        clean_ex_first: typing.Optional[bool] = OMIT,
    ) -> typing.Any:
        """
        Parameters:
            - freq: typing.Optional[str]. The frequency of the data represented as a string. 'D' for daily, 'M' for monthly, 'H' for hourly, and 'W' for weekly frequencies are available.

            - level: typing.Optional[typing.List[typing.Any]]. A list of values representing the prediction intervals. Each value is a percentage that indicates the level of certainty for the corresponding prediction interval. For example, [80, 90] defines 80% and 90% prediction intervals.

            - y: typing.Optional[typing.Any].

            - x: typing.Optional[MultiSeriesInput]. The exogenous  variables provided as a dictionary of two colums: columns and data. The columns contains the columns of the dataframe and data contains eaach data point. For example: {"columns": ["unique_id", "ds", "ex_1", "ex_2"], "data": [["ts_0", "2021-01-01", 0.2, 0.67], ["ts_0", "2021-01-02", 0.4, 0.7]}. This should also include forecasting horizon (fh) additional timestamps for each unique_id to calculate the future values.

            - clean_ex_first: typing.Optional[bool]. A boolean flag that indicates whether the API should preprocess (clean) the exogenous signal before applying the large time model. If True, the exogenous signal is cleaned; if False, the exogenous variables are applied after the large time model.
        """
        _request: typing.Dict[str, typing.Any] = {}
        if freq is not OMIT:
            _request["freq"] = freq
        if level is not OMIT:
            _request["level"] = level
        if y is not OMIT:
            _request["y"] = y
        if x is not OMIT:
            _request["x"] = x
        if clean_ex_first is not OMIT:
            _request["clean_ex_first"] = clean_ex_first
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_multi_series_historic"),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def timegpt_multi_series_anomalies(
        self,
        *,
        freq: typing.Optional[str] = OMIT,
        level: typing.Optional[typing.List[typing.Any]] = OMIT,
        y: typing.Optional[typing.Any] = OMIT,
        x: typing.Optional[MultiSeriesInput] = OMIT,
        clean_ex_first: typing.Optional[bool] = OMIT,
    ) -> typing.Any:
        """
        Parameters:
            - freq: typing.Optional[str]. The frequency of the data represented as a string. 'D' for daily, 'M' for monthly, 'H' for hourly, and 'W' for weekly frequencies are available.

            - level: typing.Optional[typing.List[typing.Any]]. Specifies the confidence level for the prediction interval used in anomaly detection. It is represented as a percentage between 0 and 100. For instance, a level of 95 indicates that the generated prediction interval captures the true future observation 95% of the time. Any observed values outside of this interval would be considered anomalies. A higher level leads to wider prediction intervals and potentially fewer detected anomalies, whereas a lower level results in narrower intervals and potentially more detected anomalies. Default: 99.

            - y: typing.Optional[typing.Any].

            - x: typing.Optional[MultiSeriesInput]. The exogenous  variables provided as a dictionary of two colums: columns and data. The columns contains the columns of the dataframe and data contains eaach data point. For example: {"columns": ["unique_id", "ds", "ex_1", "ex_2"], "data": [["ts_0", "2021-01-01", 0.2, 0.67], ["ts_0", "2021-01-02", 0.4, 0.7]}. This should also include forecasting horizon (fh) additional timestamps for each unique_id to calculate the future values.

            - clean_ex_first: typing.Optional[bool]. A boolean flag that indicates whether the API should preprocess (clean) the exogenous signal before applying the large time model. If True, the exogenous signal is cleaned; if False, the exogenous variables are applied after the large time model.
        """
        _request: typing.Dict[str, typing.Any] = {}
        if freq is not OMIT:
            _request["freq"] = freq
        if level is not OMIT:
            _request["level"] = level
        if y is not OMIT:
            _request["y"] = y
        if x is not OMIT:
            _request["x"] = x
        if clean_ex_first is not OMIT:
            _request["clean_ex_first"] = clean_ex_first
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_multi_series_anomalies"),
            json=jsonable_encoder(_request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def timegpt_input_size(self, *, request: SingleSeriesForecast) -> typing.Any:
        """
        Parameters:
            - request: SingleSeriesForecast.
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_input_size"),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def timegpt_model_params(self, *, request: SingleSeriesForecast) -> typing.Any:
        """
        Parameters:
            - request: SingleSeriesForecast.
        """
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "timegpt_model_params"),
            json=jsonable_encoder(request),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        if _response.status_code == 422:
            raise UnprocessableEntityError(pydantic.parse_obj_as(HttpValidationError, _response.json()))  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def validate_token(self) -> typing.Any:
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "validate_token"),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)

    async def validate_token_front(self) -> typing.Any:
        _response = await self._client_wrapper.httpx_client.request(
            "POST",
            urllib.parse.urljoin(f"{self._client_wrapper.get_base_url()}/", "validate_token_front"),
            headers=self._client_wrapper.get_headers(),
            timeout=60,
        )
        if 200 <= _response.status_code < 300:
            return pydantic.parse_obj_as(typing.Any, _response.json())  # type: ignore
        try:
            _response_json = _response.json()
        except JSONDecodeError:
            raise ApiError(status_code=_response.status_code, body=_response.text)
        raise ApiError(status_code=_response.status_code, body=_response_json)
