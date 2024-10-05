"""
Implementation of Driver that has dynamic caching for use when live-previewing a
site.
"""

import typing as t
import logging
from pathlib import Path, PurePosixPath
import warnings

from .. import core

logger = logging.getLogger(__name__)

logger_hit_miss = logger.getChild("hit_miss")


class IncrementalDriver(core.Driver):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # general cache of recipes
        self.cache: dict[core.Recipe, core.Manifest] = dict()

        # recipes in cache that are run this generation i.e. we can shortcircuit
        # the expired check
        self.gen_cached: set[core.Recipe] = set()

        # map from output files to the recipe that made them, so we can know
        # when recipes get invalidated because their outputs are overwritten
        #
        # Note: this may contain entries which refer to invalidated recipes!
        self.output_files: dict[Path, core.Recipe] = dict()

    def finish(self, flush: bool = False) -> None:
        """
        Mark a generation as complete.

        If `flush` is True, all recipes not built after the previous `finish`
        are dropped from the cache.
        """

        if flush:
            self.cache = {k: v for k, v in self.cache.items() if k in self.gen_cached}

        self.gen_cached.clear()

    @t.overload
    def is_cache_hit(self, recipe: core.Recipe, mf: None) -> t.Literal[False]:
        ...

    @t.overload
    def is_cache_hit(self, recipe: core.Recipe, mf: core.Manifest) -> bool:
        ...

    def is_cache_hit(self, recipe: core.Recipe, mf: t.Optional[core.Manifest]) -> bool:
        """
        Check if a recipe must be rebuilt, or if we can simply reuse the cached
        version.
        """

        if mf is None:
            logger_hit_miss.debug("miss (unseen): %s", recipe)
            return False

        for ev in mf.log:
            if isinstance(ev, core.Manifest.Input):
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
            elif isinstance(ev, core.Manifest.Output):
                if self.output_files.get(ev.path) not in (None, recipe):
                    # another recipe overwrote the output path so we gotta recreate it
                    logger_hit_miss.debug(
                        "miss (output overwritten: %s): %s", ev.path, recipe
                    )
                    return False
            elif isinstance(ev, core.Manifest.SubRecipe):
                # since recipes should be "pure", it is safe to reuse
                # subrecipes if all preceeding subrecipes have the same output.
                new_mf = self.build(ev.recipe)
                if new_mf != ev.manifest:
                    logger_hit_miss.debug(
                        "miss (subrecipe manifest changed: %s): %s", ev.recipe, recipe
                    )
                    return False
            elif isinstance(ev, core.Manifest.Trace):
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

    def build(self, recipe: core.Recipe) -> core.Manifest:
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
            for output in mf.filter(core.Manifest.Output):
                assert output.path not in self.output_files
                self.output_files[output.path] = recipe

        self.gen_cached.add(recipe)
        return t.cast(core.Manifest, mf)
