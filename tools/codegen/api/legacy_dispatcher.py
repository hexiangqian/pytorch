from tools.codegen.model import *

from tools.codegen.api.types import TensorOptionsArguments, LegacyDispatcherArgument
import tools.codegen.api.cpp as cpp

from typing import Union

# This file describes the translation of JIT schema to the legacy
# dispatcher API.  This looks a lot like the C++ API (which
# makes historical sense, because historically the dispatcher API
# and the C++ API exactly matched), but over time we have
# evolved the C++ API without actually changing our native::
# kernels.  To be deleted eventually.  Dispatcher calls use
# this when you are not use_c10_dispatcher_full.

def name(func: FunctionSchema) -> str:
    name = str(func.name.name)
    # TODO: delete this!
    if func.is_out_fn():
        name += '_out'
    if func.name.overload_name:
        name += f'_{func.name.overload_name}'
    return name

def argumenttype_type(t: Type, *, mutable: bool) -> str:
    if str(t) == 'Tensor?':
        if mutable:
            return 'Tensor &'
        else:
            return 'const Tensor &'
    elif str(t) == 'Tensor?[]':
            return 'TensorList'
    return cpp.argumenttype_type(t, mutable=mutable)

def returns_type(rs: Sequence[Return]) -> str:
    return cpp.returns_type(rs)

def argument_type(a: Argument) -> str:
    return argumenttype_type(a.type, mutable=a.is_write)

def argument(a: Union[Argument, TensorOptionsArguments]) -> LegacyDispatcherArgument:
    if isinstance(a, Argument):
        return LegacyDispatcherArgument(
            type=argument_type(a),
            name=a.name,
            argument=a,
        )
    elif isinstance(a, TensorOptionsArguments):
        return LegacyDispatcherArgument(
            type='const TensorOptions &',
            name='options',
            argument=a,
        )
    else:
        assert_never(a)

def arguments(func: FunctionSchema) -> Sequence[LegacyDispatcherArgument]:
    return list(map(argument, cpp.group_arguments(func)))
