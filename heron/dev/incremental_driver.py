"""
Implementations of Driver
"""

import time
import logging
from pathlib import Path

from .. import core

logger = logging.getLogger(__name__)

logger_hit_miss = logger.getChild("hit_miss")


class IncrementalDriver(core.Driver):
    """
    Driver than can be used for multiple builds, and avoid
    unnecessary rebuilds of recipes.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # properties of last completed build
        self.old_cache: dict[core.Recipe, core.Manifest] = dict()
        self.old_readtimes: dict[Path, float] = dict()

        # properties of current build
        self.new_cache: dict[core.Recipe, core.Manifest] = dict()
        self.new_readtimes: dict[Path, float] = dict()

    def finish(self) -> None:
        """
        Mark a build run as completed.
        """

        # swap new -> old
        self.old_cache = self.new_cache
        self.old_readtimes = self.new_readtimes

        self.new_cache = dict()
        self.new_readtimes = dict()

    # override Driver

    def input(self, path: Path) -> Path:
        # save readtime so we know whether to rebuild
        path = super().input(path)
        self.new_readtimes.setdefault(path, time.time())
        return path

    def build(self, recipe: core.Recipe) -> core.Manifest:
        try:
            hash(recipe)
        except TypeError:
            # catch this early before we run into it later
            raise TypeError(f"unhashable recipe: {recipe!r}")

        mf = self.new_cache.get(recipe)
        if mf is not None:
            # already cached during current generation
            return mf

        super_build = super().build

        def do_fresh_build():
            mf = super_build(recipe)
            self.new_cache[recipe] = mf
            return mf

        # inter-generational caching

        mf = self.old_cache.get(recipe)
        if mf is None:
            logger_hit_miss.debug("miss (unseen): %s", recipe)
            return do_fresh_build()

        for ev in mf.log:
            if isinstance(ev, core.Manifest.Input):
                try:
                    mtime = ev.path.stat().st_mtime
                except FileNotFoundError:
                    # file got deleted
                    logger_hit_miss.debug("miss (input gone: %s): %s", ev.path, recipe)
                    return do_fresh_build()
                if mtime >= self.old_readtimes[ev.path]:
                    # input file changed
                    logger_hit_miss.debug("miss (input changed: %s): %s", ev.path, recipe)
                    return do_fresh_build()
            elif isinstance(ev, core.Manifest.SubRecipe):
                # since recipes should be "pure", it is safe to reuse
                # subrecipes if all preceeding subrecipes have the same output.
                new_mf = self.build(ev.recipe)
                if new_mf != ev.manifest:
                    logger_hit_miss.debug("miss (subrecipe manifest changed: %s): %s", ev.recipe, recipe)
                    return do_fresh_build()

        # we now know that all inputs (files or drv values) haven't changed, so
        # it's safe to reuse the old drv without rebuilding

        self.new_cache[recipe] = mf

        # we also need to copy over the readtimes
        for inp in mf.filter(core.Manifest.Input):
            self.new_readtimes[inp.path] = self.old_readtimes[inp.path]

        logger_hit_miss.debug("hit: %s", recipe)

        return mf
