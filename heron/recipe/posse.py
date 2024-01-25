import heron
import dataclasses
import requests


@dataclasses.dataclass(frozen=True)
class GitHubIssueRecipe(heron.core.Recipe[str | None]):
    @dataclasses.dataclass(frozen=True)
    class ListIssues(heron.core.Recipe):
        # because of GitHub's very low API ratelimit, it's much nicer to fetch
        # everything once and cache the results
        owner: str
        repo: str

        def build_impl(self, ctx: heron.core.BuildContext):
            # TODO pagination
            r = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/issues",
                headers={
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )
            r.raise_for_status()
            return heron.util.freeze([x for x in r.json() if "pull_request" not in x])

    owner: str
    repo: str
    title: str

    def build_impl(self, ctx: heron.core.BuildContext) -> str | None:
        repo_issues = ctx.build(self.ListIssues(self.owner, self.repo))
        items = [x for x in repo_issues if x["title"] == self.title]
        if not items:
            return None
        elif len(items) == 1:
            return items[0]["html_url"]
        else:
            raise RuntimeError(
                f"too many issues with title {self.title!r} in repo:{self.owner}/{self.repo}"
            )
