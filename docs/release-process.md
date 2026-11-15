# Git workflow and release process

**English** | [Français](release-process.fr.md)

## Branches

- `main` holds only stable releases or validated candidates.
- `dev` is the integration branch. It is created from `main` and receives
  verified changes before any promotion proposal.
- Isolated work may use a short-lived branch created from `dev` and merged back
  into `dev` after review.

History must never be rewritten. Force-pushes, deletion of stable branches, and
protection bypasses are forbidden.

## Commits

New commits follow Conventional Commits: `feat`, `fix`, `docs`, `test`,
`refactor`, `perf`, `build`, `ci`, `chore`, or `revert`, with an optional
scope. Each commit must represent a coherent unit of work and must contain no
secrets, temporary files, or results claimed as verified without evidence.

## Preparing a release

1. Start from a clean `dev` branch and identify the candidate commit.
2. Derive the version from verified public behavior and update the canonical
   changelog.
3. Run the adapter sync checks, bootstrap validator, structural tests, and
   installer test suite.
4. Have significant changes reviewed by an independent reviewer.
5. Open a pull request from `dev` to `main` and wait for required checks and
   approvals.
6. After authorization, merge without rewriting history and re-verify the exact
   commit on `main`.
7. After separate authorization, create the annotated tag `vX.Y.Z` on that
   commit, push the tag, and publish the GitHub Release from `main`.

Successful preparation does not authorize merging, tagging, publishing, or
deploying. Any failing critical check blocks the release.

## Recommended GitHub protections

Configure a ruleset for `main` requiring a pull request, at least one
independent review, conversation resolution, and required automated status
checks. Disallow force-pushes and deletion of `main`. Also protect `v*` tags
against unauthorized modification or deletion.

ForgeOS documents these controls but does not enable them implicitly: applying
them on GitHub requires appropriate repository permissions and explicit
authorization.

## Recovery

If an incorrect local tag is detected, do not push it: pause the release,
document the discrepancy, and ask for explicit authorization before fixing it.
After publication, never silently move a tag; agree with the repository owner
on an explicit correction or a new version. Published defects are fixed by a
subsequent commit and version without rewriting history.
