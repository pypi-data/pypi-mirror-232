"""Protocol for combinging a single model inference and a csv algorithm."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Optional, Sequence, Union, cast

import pandas as pd

from bitfount.federated.algorithms.csv_report_algorithm import (
    CSVReportAlgorithm,
    _ModellerSide as _CSVModellerSide,
    _WorkerSide as _CSVWorkerSide,
)
from bitfount.federated.algorithms.huggingface_algorithms.huggingface_image_classification import (  # noqa: B950
    HFImageClassification,
    _ModellerSide as _ImgClassificationModellerSide,
    _WorkerSide as _ImgClassificationWorkerSide,
)
from bitfount.federated.algorithms.huggingface_algorithms.huggingface_image_segmentation import (  # noqa: B950
    HFImageSegmentation,
    _ModellerSide as _ImgSegmentationModellerSide,
    _WorkerSide as _ImgSegmentationWorkerSide,
)
from bitfount.federated.algorithms.huggingface_algorithms.huggingface_perplexity import (  # noqa: B950
    HFPerplexity,
    _ModellerSide as _PerplexityModellerSide,
    _WorkerSide as _PerplexityWorkerSide,
)
from bitfount.federated.algorithms.huggingface_algorithms.huggingface_text_classification import (  # noqa: B950
    HFTextClassification,
    _ModellerSide as _TextClassificationModellerSide,
    _WorkerSide as _TextClassificationWorkerSide,
)
from bitfount.federated.algorithms.huggingface_algorithms.huggingface_text_generation import (  # noqa: B950
    HFTextGeneration,
    _ModellerSide as _TextGenerationModellerSide,
    _WorkerSide as _TextGenerationWorkerSide,
)
from bitfount.federated.algorithms.model_algorithms.base import (
    _BaseModellerModelAlgorithm,
    _BaseWorkerModelAlgorithm,
)
from bitfount.federated.algorithms.model_algorithms.inference import (
    ModelInference,
    _ModellerSide as _InferenceModellerSide,
    _WorkerSide as _InferenceWorkerSide,
)
from bitfount.federated.logging import _get_federated_logger
from bitfount.federated.pod_vitals import _PodVitals
from bitfount.federated.protocols.base import (
    BaseCompatibleAlgoFactory,
    BaseModellerProtocol,
    BaseProtocolFactory,
    BaseWorkerProtocol,
)
from bitfount.federated.transport.modeller_transport import (
    _ModellerMailbox,
    _send_model_parameters,
)
from bitfount.federated.transport.worker_transport import (
    _get_model_parameters,
    _WorkerMailbox,
)
from bitfount.types import _SerializedWeights, _Weights

if TYPE_CHECKING:
    from bitfount.hub.api import BitfountHub

logger = _get_federated_logger("bitfount.federated.protocols" + __name__)


class _ModellerSide(BaseModellerProtocol):
    """Modeller side of the protocol.

    Args:
        algorithm: A list of algorithms to be run by the protocol. This should be
            a list of two algorithms, the first being the model inference algorithm
            and the second being the csv report algorithm.
        mailbox: The mailbox to use for communication with the Workers.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[
        Union[
            _ImgClassificationModellerSide,
            _ImgSegmentationModellerSide,
            _InferenceModellerSide,
            _TextClassificationModellerSide,
            _TextGenerationModellerSide,
            _PerplexityModellerSide,
            _CSVModellerSide,
        ]
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _ImgClassificationModellerSide,
                _ImgSegmentationModellerSide,
                _InferenceModellerSide,
                _TextClassificationModellerSide,
                _TextGenerationModellerSide,
                _PerplexityModellerSide,
                _CSVModellerSide,
            ]
        ],
        mailbox: _ModellerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _send_parameters(self, new_parameters: _SerializedWeights) -> None:
        """Sends central model parameters to workers."""
        logger.debug("Sending global parameters to workers")
        await _send_model_parameters(new_parameters, self.mailbox)

    async def run(
        self,
        iteration: int = 0,
        **kwargs: Any,
    ) -> None:
        """Runs Modeller side of the protocol.

        This just sends the model parameters to the workers and then tells
        the workers when the protocol is finished.
        """
        for algo in self.algorithm:
            if isinstance(algo, _BaseModellerModelAlgorithm):
                initial_parameters: _Weights = algo.model.get_param_states()
                serialized_params = algo.model.serialize_params(initial_parameters)
                await self._send_parameters(serialized_params)
                break

        await self.mailbox.get_evaluation_results_from_workers()
        return None


class _WorkerSide(BaseWorkerProtocol):
    """Worker side of the protocol.

    Args:
        algorithm: A list of algorithms to be run by the protocol. This should be
            a list of two algorithms, the first being the model inference algorithm
            and the second being the csv report algorithm.
        mailbox: The mailbox to use for communication with the Modeller.
        **kwargs: Additional keyword arguments.
    """

    algorithm: Sequence[
        Union[
            _ImgClassificationWorkerSide,
            _ImgSegmentationWorkerSide,
            _InferenceWorkerSide,
            _PerplexityWorkerSide,
            _TextGenerationWorkerSide,
            _TextClassificationWorkerSide,
            _CSVWorkerSide,
        ]
    ]

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                _ImgClassificationWorkerSide,
                _ImgSegmentationWorkerSide,
                _InferenceWorkerSide,
                _PerplexityWorkerSide,
                _TextGenerationWorkerSide,
                _TextClassificationWorkerSide,
                _CSVWorkerSide,
            ]
        ],
        mailbox: _WorkerMailbox,
        **kwargs: Any,
    ):
        super().__init__(algorithm=algorithm, mailbox=mailbox, **kwargs)

    async def _receive_parameters(self) -> _SerializedWeights:
        """Receives new global model parameters."""
        logger.debug("Receiving global parameters")
        return await _get_model_parameters(self.mailbox)

    async def run(
        self,
        pod_vitals: Optional[_PodVitals] = None,
        **kwargs: Any,
    ) -> None:
        """Runs the algorithm on worker side."""
        # Unpack the algorithm into the two algorithms
        model_inference_algo, csv_report_algo = self.algorithm

        if pod_vitals:
            pod_vitals.last_task_execution_time = time.time()
        # Run Inference Algorithm
        if isinstance(model_inference_algo, _BaseWorkerModelAlgorithm):
            model_params = await self._receive_parameters()
            model_predictions = model_inference_algo.run(model_params=model_params)
        else:
            assert not isinstance(  # nosec[assert_used]
                model_inference_algo, _CSVWorkerSide
            )
            results = model_inference_algo.run()
            if not isinstance(results, pd.DataFrame):
                logger.error(
                    "The model output did not return "
                    "a dataframe, so we cannot output "
                    "the predictions to a csv file."
                )
            else:
                model_predictions = results
        model_predictions = cast(pd.DataFrame, model_predictions)

        csv_report_algo = cast(_CSVWorkerSide, csv_report_algo)
        csv_report_algo.run(
            results_df=model_predictions,
            task_id=self.mailbox._task_id,
        )
        # Sends empty results to modeller just to inform it to move on to the
        # next algorithm
        await self.mailbox.send_evaluation_results({})


class InferenceAndCSVReport(BaseProtocolFactory):
    """Protocol for running a model inference generating a csv report."""

    def __init__(
        self,
        *,
        algorithm: Sequence[
            Union[
                ModelInference,
                HFImageClassification,
                HFImageSegmentation,
                HFPerplexity,
                HFTextClassification,
                HFTextGeneration,
                CSVReportAlgorithm,
            ]
        ],
        **kwargs: Any,
    ) -> None:
        super().__init__(algorithm=algorithm, **kwargs)

    @classmethod
    def _validate_algorithm(cls, algorithm: BaseCompatibleAlgoFactory) -> None:
        """Validates the algorithm."""
        if algorithm.class_name not in (
            "bitfount.ModelInference",
            "bitfount.HFImageClassification",
            "bitfount.HFImageSegmentation",
            "bitfount.HFTextClassification",
            "bitfount.HFTextGeneration",
            "bitfount.HFPerplexity",
            "bitfount.CSVReportAlgorithm",
        ):
            raise TypeError(
                f"The {cls.__name__} protocol does not support "
                + f"the {type(algorithm).__name__} algorithm.",
            )

    def modeller(self, mailbox: _ModellerMailbox, **kwargs: Any) -> _ModellerSide:
        """Returns the Modeller side of the protocol."""
        algorithms = cast(
            Sequence[
                Union[
                    ModelInference,
                    HFImageClassification,
                    HFImageSegmentation,
                    HFTextGeneration,
                    HFTextClassification,
                    HFPerplexity,
                    CSVReportAlgorithm,
                ]
            ],
            self.algorithms,
        )
        modeller_algos = []
        for algo in algorithms:
            if hasattr(algo, "pretrained_file"):
                modeller_algos.append(
                    algo.modeller(pretrained_file=algo.pretrained_file)
                )
            else:
                modeller_algos.append(algo.modeller())
        return _ModellerSide(
            algorithm=modeller_algos,
            mailbox=mailbox,
            **kwargs,
        )

    def worker(
        self, mailbox: _WorkerMailbox, hub: BitfountHub, **kwargs: Any
    ) -> _WorkerSide:
        """Returns worker side of the protocol."""
        algorithms = cast(
            Sequence[
                Union[
                    ModelInference,
                    HFImageClassification,
                    HFImageSegmentation,
                    HFPerplexity,
                    HFTextGeneration,
                    HFTextClassification,
                    CSVReportAlgorithm,
                ]
            ],
            self.algorithms,
        )
        return _WorkerSide(
            algorithm=[algo.worker(hub=hub) for algo in algorithms],
            mailbox=mailbox,
            **kwargs,
        )
