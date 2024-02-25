import os
import heron
import dataclasses
import requests


POSSE_READONLY = True


def gh_headers() -> dict[str, str]:
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@dataclasses.dataclass(frozen=True)
class GitHubIssueRecipe(heron.core.Recipe[str | None]):
    @dataclasses.dataclass(frozen=True)
    class ListIssues(heron.core.Recipe[heron.util.Impurity[list]]):
        # because of GitHub's very low API ratelimit, it's much nicer to fetch
        # everything once and cache the results
        owner: str
        repo: str

        def build_impl(self, ctx: heron.core.BuildContext):
            # TODO pagination
            r = requests.get(
                f"https://api.github.com/repos/{self.owner}/{self.repo}/issues",
                headers=gh_headers(),
            )
            r.raise_for_status()

            # the returned result is mutable! since GitHubIssueRecipe may extend it when creating issues
            issues = [x for x in r.json() if "pull_request" not in x]
            return heron.util.Impurity(lambda: issues)

    owner: str
    repo: str
    title: str

    def build_impl(self, ctx: heron.core.BuildContext) -> str | None:
        repo_issues = ctx.build(self.ListIssues(self.owner, self.repo))()
        items = [x for x in repo_issues if x["title"] == self.title]

        if len(items) == 1:
            return items[0]["html_url"]
        elif len(items) > 1:
            raise RuntimeError(
                f"too many issues with title {self.title!r} in repo:{self.owner}/{self.repo}"
            )

        if POSSE_READONLY:
            return None

        # create issue
        r = requests.post(
            f"https://api.github.com/repos/{self.owner}/{self.repo}/issues",
            headers=gh_headers(),
            json={
                "title": self.title,
                "body": f"_This issue contains comments for {self.title}_.",
            },
        )
        r.raise_for_status()
        issue = r.json()
        repo_issues.append(issue)
        return issue["html_url"]
