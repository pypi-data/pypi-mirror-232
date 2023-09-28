import typing as t

from ellar.common.interfaces import IExecutionContext

from .base import NonParameterResolver


class ExecutionContextParameter(NonParameterResolver):
    async def resolve(
        self, ctx: IExecutionContext, **kwargs: t.Any
    ) -> t.Tuple[t.Dict, t.List]:
        return {self.parameter_name: ctx}, []
