from inspect import getsource
from pathlib import Path
from types import FunctionType
from typing import Tuple, List, Dict, Literal, Union

from cerebrium.models.base import ModelType

CerebriumModel = Tuple[
    ModelType,
    Union[str, dict],
    Dict[Union[Literal["pre"], Literal["post"]], Union[FunctionType, str]],
]
CerebriumFlow = List[CerebriumModel]


def _flow_string(flow: CerebriumFlow):
    """
    Convert a flow to a string.

    Args:
        flow (CerebriumFlow): The flow to convert.

    Returns:
        str: The flow as a string.
    """
    string = ""
    for i, component in enumerate(flow):
        val: str = component[0].value
        string += val
        if i != len(flow) - 1:
            string += "->"
    return string


def _get_function_arg(def_string: str) -> List[str]:
    """
    Return the arguments of a string function definition as a list of strings.

    Args:
        def_string: The string function definition line.

    Returns:
        A list of strings containing the arguments of the function.
    """
    argument_bracket_1 = def_string.find("(")
    argument_bracket_2 = def_string.find(")")
    argument_str = def_string[argument_bracket_1 + 1 : argument_bracket_2]
    return argument_str.split(",")


def _check_input_tuple(
    model_flow: Union[CerebriumFlow, CerebriumModel]
) -> CerebriumFlow:
    # if a CerebriumModel is passed, wrap it in a list
    wrapped_flow = model_flow  # type: ignore
    if len(model_flow) == 2:
        if (
            not isinstance(model_flow[0], list)
            and not isinstance(model_flow[0], tuple)
            and not isinstance(model_flow[1], list)
            and not isinstance(model_flow[1], tuple)
        ):
            wrapped_flow: CerebriumFlow = [model_flow]  # type: ignore
    elif len(model_flow) == 3:
        if (
            not isinstance(model_flow[0], list)
            and not isinstance(model_flow[0], tuple)
            and not isinstance(model_flow[1], list)
            and not isinstance(model_flow[1], tuple)
            and not isinstance(model_flow[2], list)
            and not isinstance(model_flow[2], tuple)
        ):
            wrapped_flow: CerebriumFlow = [model_flow]  # type: ignore

    return wrapped_flow


def _check_valid_model(
    model_type: ModelType,
    model_initialization: Union[str, dict],
    pipeline_position: int,
):
    """
    Check that the model is valid, raising an error if not.

    Args:
        model_type: The type of the model.
        model_initialization: The initialization values needed for the Cerebrium model. For most models, this is a string filepath to the model.
        pipeline_position: The position of the model in the pipeline.
    """
    # Check typing
    if not isinstance(model_type, ModelType):
        raise TypeError(
            f"Model {pipeline_position}: model_type must be of type ModelType, but is {type(model_type)}. Please ensure you use a valid Cerebrium typing."
        )

    # Check valid model params
    if (
        model_type == ModelType.HUGGINGFACE_PIPELINE
        and not isinstance(model_initialization, dict)
        and ("task" not in model_initialization or "model" not in model_initialization)
    ):
        raise TypeError(
            f"Model {pipeline_position}: For {model_type}, `model_initialization` must be a dictionary and contain at least one of the keys 'task' or 'model', but is {model_initialization}"
        )
    elif model_type == ModelType.ONNX:
        assert isinstance(model_initialization, str)
        if not model_initialization.endswith(".onnx"):
            raise TypeError(
                f"Model {pipeline_position}: {model_type} `model_initialization` file type must be `.onnx`, but is {model_initialization.split('.')[-1]}"
            )
    elif model_type != ModelType.HUGGINGFACE_PIPELINE and not isinstance(
        model_initialization, str
    ):
        raise TypeError(
            f"Model {pipeline_position}: For {model_type}, model_initialization must be a file path of type `str`, but is {type(model_initialization)}"
        )
    elif model_type != ModelType.HUGGINGFACE_PIPELINE:
        assert isinstance(model_initialization, str)
        if not Path(model_initialization).exists():
            raise TypeError(
                f"Model {pipeline_position}: For {model_type}, `model_initialization` must be be a valid file path, but is {model_initialization}"
            )
    elif model_type in [
        ModelType.SKLEARN_CLASSIFIER,
        ModelType.SKLEARN,
    ]:
        assert isinstance(model_initialization, str)
        if not model_initialization.endswith(".pkl"):
            raise TypeError(
                f"Model {pipeline_position}: {model_type} `model_initialization` file type must be `.pkl`, but is {model_initialization.split('.')[-1]}"
            )
    elif model_type in [ModelType.XGBOOST_CLASSIFIER, ModelType.XGBOOST_REGRESSOR]:
        assert isinstance(model_initialization, str)
        if not model_initialization.endswith(
            ".pkl"
        ) and not model_initialization.endswith(".json"):
            raise TypeError(
                f"Model {pipeline_position}: {model_type} `model_initialization` file type must be either `.pkl` or `.json`, but is {model_initialization.split('.')[-1]}"
            )
    return model_type, model_initialization


def _check_processor(
    processor: Union[FunctionType, str], pipeline_position: int, stage: str
):
    """
    Check that the postprocessor is valid, raising an error if not.

    Args:
        processor: The processor function.
        pipeline_position: The position of the post-processor in the pipeline.
    """
    if not isinstance(processor, FunctionType) and processor is not None:
        raise TypeError(
            f"Model {pipeline_position}: The post-processing function must be of type FunctionType, but is {type(processor)}"
        )
    if processor is not None:
        processor_str = getsource(processor).replace("\t", "    ").split("\n")
        processor_args = _get_function_arg(processor_str[0])
        if processor_args[0] == "":
            processor_args = []
        if len(processor_args) == 0 or len(processor_args) >= 4:
            raise NotImplementedError(
                f"Model {processor}: The {stage}-processing function must have between 1 and 3 arguments, but has {len(processor_args)}"
            )

        contains_return = [s.strip()[:6] == "return" for s in processor_str]
        if not any(contains_return):
            raise NotImplementedError(
                f"Model {processor}: The {stage}-processing function must return a value, but does not."
            )


def _check_flow_type(model_flow: Union[CerebriumFlow, CerebriumModel]) -> CerebriumFlow:
    """
    Check if the given model_flow is a valid CerebriumFlow.

    Args:
        model_flow: The model_flow to check.

    Returns:
        CerebriumFlow: The model_flow if it is valid. Adds post-process and outer list of necessary.

    Raises:
        TypeError: If the model_flow is not a valid CerebriumFlow.
    """

    # Raise error if model_flow is not a list or tuple
    if not isinstance(model_flow, list) and not isinstance(model_flow, tuple):
        raise TypeError(
            f"model_flow must be a tuple or list, but is {type(model_flow)}"
        )

    # If the model_flow is a list or tuple, check if all elements are tuples for single model flow
    model_flow = _check_input_tuple(model_flow)

    # Check if the model_flow is a valid model flow
    for i, flow_component in enumerate(model_flow):
        model_type, model_initialization = _check_valid_model(
            flow_component[0], flow_component[1], i
        )
        if len(flow_component) == 3:
            if not isinstance(flow_component[2], dict):
                # Assume a post-process function, backwards compatibility
                _check_processor(flow_component[2], i, "post")
                model_flow[i] = (  # type: ignore
                    model_type,
                    model_initialization,
                    {"post": flow_component[2]},
                )
            else:
                # Check if the processing functions are valid
                keys = set(flow_component[2].keys())
                remaining_keys = keys - {"post", "pre"}  # type: ignore
                if remaining_keys != set():
                    raise TypeError(
                        f"Model {i}: The processing functions contains invalid keys {str(remaining_keys)}. Please use only 'post' and 'pre'."
                    )
                if "post" in flow_component[2]:
                    post = flow_component[2]["post"]
                    _check_processor(post, i, "post")
                if "pre" in flow_component[2]:
                    pre = flow_component[2]["pre"]
                    _check_processor(pre, i, "pre")
        else:
            model_flow[i] = (model_type, model_initialization, {})
    return model_flow
