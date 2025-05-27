"""
Implementations of Driver with additional functionality.
"""

import logging
import typing as t
import warnings
from pathlib import Path, PurePosixPath

from .kernel import Driver, DriverWrapper, Manifest, Recipe

__all__ = [
    "CachingDriver",
    "GenerationalDriver",
    "LoggingDriver",
]

logger = logging.getLogger(__name__)

logger_hit_miss = logger.getChild("hit_miss")


class CachingDriver(DriverWrapper):
    """
    Driver with basic caching of repeated recipes.
    """

    def __init__(self, driver: Driver):
        super().__init__(driver)

        # general cache of recipes
        self.cache: dict[Recipe, Manifest] = dict()

    def build(self, recipe):
        mf = self.cache.get(recipe)
        if mf is not None:
            return mf
        self.cache[recipe] = mf = super().build(recipe)
        return mf


class GenerationalDriver(DriverWrapper):
    """
    Driver with a clearable cache, for use when live-previewing a recipe.
    """

    def __init__(self, driver: Driver):
        super().__init__(driver)

        # general cache of recipes
        self.cache: dict[Recipe, Manifest] = dict()

        # recipes in cache that are run this generation i.e. we can shortcircuit
        # the expired check
        self.gen_cached: set[Recipe] = set()

        # map from output files to the recipe that made them, so we can know
        # when recipes get invalidated because their outputs are overwritten
        #
        # Note: this may contain entries which refer to invalidated recipes!
        self.output_files: dict[Path, Recipe] = dict()

    def finish(self, flush: bool = False) -> None:
        """
        Mark a generation as complete.

        If `flush` is True, all recipes not built since the previous `finish`
        are dropped from the cache.
        """
        # TODO explain how to use this

        if flush:
            self.cache = {k: v for k, v in self.cache.items() if k in self.gen_cached}

        self.gen_cached.clear()

    @t.overload
    def is_cache_hit(self, recipe: Recipe, mf: None) -> t.Literal[False]: ...

    @t.overload
    def is_cache_hit(self, recipe: Recipe, mf: Manifest) -> bool: ...

    def is_cache_hit(self, recipe: Recipe, mf: t.Optional[Manifest]) -> bool:
        """
        Check if a recipe must be rebuilt, or if we can simply reuse the cached
        version.
        """

        if mf is None:
            logger_hit_miss.debug("miss (unseen): %s", recipe)
            return False

        for ev in mf.log:
            if isinstance(ev, Manifest.Input):
                try:
                    mtime = ev.path.stat().st_mtime
                except FileNotFoundError:
                    # file got deleted
                    logger_hit_miss.debug("miss (input gone: %s): %s", ev.path, recipe)
                    return False

                if mtime >= ev.time:
                    # input file changed
                    logger_hit_miss.debug(
                        "miss (input changed: %s): %s", ev.path, recipe
                    )
                    return False
            elif isinstance(ev, Manifest.Output):
                if self.output_files.get(ev.path) not in (None, recipe):
                    # another recipe overwrote the output path so we gotta recreate it
                    logger_hit_miss.debug(
                        "miss (output overwritten: %s): %s", ev.path, recipe
                    )
                    return False
            elif isinstance(ev, Manifest.SubRecipe):
                # since recipes should be "pure", it is safe to reuse
                # subrecipes if all preceeding subrecipes have the same output.
                new_mf = self.build(ev.recipe)
                if new_mf != ev.manifest:
                    logger_hit_miss.debug(
                        "miss (subrecipe manifest changed: %s): %s", ev.recipe, recipe
                    )
                    return False
            elif isinstance(ev, Manifest.Trace):
                # debug output doesn't matter
                pass
            else:
                t.assert_never(ev)

        # cache hit :)

        return True

    # override Driver

    def output(self, opath: PurePosixPath) -> Path:
        path = super().output(opath)

        # may need to expire recipes
        recipe = self.output_files.pop(path, None)
        if recipe is not None:
            # invalidate cache entry if it exists
            self.cache.pop(recipe, None)

            if recipe in self.gen_cached:
                warnings.warn(f"duplicate output: {opath}", RuntimeWarning, 3)
                self.gen_cached.discard(recipe)

        return path

    def build(self, recipe: Recipe) -> Manifest:
        try:
            hash(recipe)
        except TypeError:
            # catch this early before we run into it later
            raise TypeError(f"unhashable recipe: {recipe!r}")

        mf = self.cache.get(recipe)
        if recipe in self.gen_cached:
            assert mf is not None
            # already cached during current generation
            return mf

        if not self.is_cache_hit(recipe, mf):
            mf = super().build(recipe)
            self.cache[recipe] = mf
            for output in mf.filter(Manifest.Output):
                assert output.path not in self.output_files
                self.output_files[output.path] = recipe

        self.gen_cached.add(recipe)
        return t.cast(Manifest, mf)


class LoggingDriver(DriverWrapper):
    """
    Configurable logging driver

    Arguments:

    * `outputs`:
        True: log files being written to (i.e. Output manifest entries)

    * `recipes`:
        "type": log type of recipes being built
    """

    def __init__(
        self,
        driver: Driver,
        *,
        logger: logging.Logger = logger,
        outputs: t.Literal[False, True] = False,
        recipes: t.Literal[False, "type"] = False,
    ):
        super().__init__(driver)

        self.logger = logger

        self.log_outputs = outputs
        self.log_recipes = recipes

    def build(self, recipe):
        if self.log_recipes:
            if self.log_recipes == "type":
                self.logger.info("building %s", recipe.__class__.__name__)

        mf = super().build(recipe)
        for e in mf.log:
            if self.log_outputs and isinstance(e, Manifest.Output):
                self.logger.info("wrote %s", e.path.relative_to(self.builddir))

        return mf
