"""
Compose stages together into a pipeline
"""

import typing as t
import dataclasses

from .kernel import BuildContext, Recipe, current_ctx
from .recipes import permalink, OutputMixin, ConstRecipe

__all__ = [
    "StepFn",
    "Step",
    "Pipeline",
    "WriteStep",
    "jinja_filter_from_final_step",
    "STEP_FILTERS",
]


type StepFn[I, O] = t.Callable[[BuildContext, "Pipeline", I], O]


@dataclasses.dataclass(frozen=True)
class Step[I, O]:
    fn: StepFn[I, O]

    def __ror__(self, left: Recipe[I] | "Pipeline[I]") -> "Pipeline[O]":
        if isinstance(left, Pipeline):
            return left.extend(self)
        if isinstance(left, Recipe):
            return Pipeline[I](left).extend(self)
        return NotImplemented


@dataclasses.dataclass(frozen=True)
class Pipeline[T](Recipe[T]):
    source: Recipe
    stages: tuple[Step, ...] = tuple()

    @t.overload
    def __init__(self, source: Recipe[T]) -> None: ...

    @t.overload
    def __init__(self, source: Recipe, stages: tuple) -> None: ...

    def __init__(self, source: Recipe[T], stages: tuple[Step, ...] = tuple()):
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "stages", stages)

    def extend[U](self, stage: Step[T, U]):
        return dataclasses.replace(self, stages=(*self.stages, stage))

    def build_impl(self, ctx: BuildContext) -> t.Any:
        # TODO call build_impl directly to avoid caching intermediate value?
        content = self.source.build_impl(ctx)
        for stage in self.stages:
            content = stage.fn(ctx, self, content)
        return content


@dataclasses.dataclass(frozen=True)
class WriteStep(OutputMixin):
    def __call__(
        self,
        ctx: BuildContext,
        pipeline: Pipeline,
        content: str | bytes,
    ) -> str:
        mode = "wb" if isinstance(content, bytes) else "wt"
        with ctx.output(self.opath).open(mode) as f:
            f.write(mode)
        return permalink(self.opath)


def jinja_filter_from_final_step[I, R, **P](step: t.Callable[P, StepFn[I, R]]) -> t.Any:
    """
    Create a Jinja filter from a step that finalises the pipeline.
    """

    def filter(prev: I | Recipe[I] | Pipeline[I], *args: P.args, **kwargs: P.kwargs):
        if not isinstance(prev, Recipe):
            prev = ConstRecipe(prev)
        if not isinstance(prev, Pipeline):
            prev = Pipeline(prev)
        return current_ctx().build(prev.extend(Step(step(*args, **kwargs))))
    return filter


STEP_FILTERS = {
    "step.write": jinja_filter_from_final_step(WriteStep),
}
