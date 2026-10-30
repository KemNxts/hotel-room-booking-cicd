# Task 4 - viva questions and answers

**Task 4 - Git and GitHub Repository Initialization**

Source: section G of [task-04-git-and-github-initialization.md](../../task-04-git-and-github-initialization.md) - answers checked against the
repository and the evidence in this project.

1. **Git vs GitHub?** Git records history locally; GitHub hosts a copy online and adds issues, PRs and a web view.
2. **What is a commit?** A saved snapshot of the files with an ID, author, date and message.
3. **Branch vs tag?** A branch moves forward as you commit; a tag is fixed to one commit forever (we use tags for releases).
4. **Why `.gitignore`?** To keep secrets (`.env`), local databases and generated files out of the repository.
5. **What does `.gitattributes` do here?** Forces LF line endings so shell
   scripts and configs work in Linux containers even when edited on Windows.
6. **Explain your branch policy.** `main` = released code, `develop` =
   integration, `feature/<name>` per change, `fix/<name>` for fixes,
   `experiment/<name>` never merged. Features merge into develop with `--no-ff`.
7. **(Project-specific) What is in your first commit?** `541dad5`: README,
   CONTRIBUTING, `.gitignore`, `.gitattributes`, issue and PR templates and empty folders.
8. **(Project-specific) Why do commit IDs in your evidence differ from GitHub?**
   Messages were edited once before publishing; IDs are hashes that include
   the message, so all IDs changed. `docs/evidence/git/commit-id-map.md` maps them.
9. **What is a Conventional Commit?** A message format `type: summary`, e.g.
   `fix: reject check-out before check-in`, making history easy to read.
10. **Is your `main` branch protected?** Only by policy in `CONTRIBUTING.md`;
    GitHub protection rules were not configured (needs the owner's settings).
11. **Why have both `main` and `develop`?** `develop` can be tested on
    staging while `main` only receives releases that passed the pipeline.

## Extra questions that match this demonstration

1. **The project document says it was not pushed to GitHub. Is that still true?**
   No. That note in docs/04-git-workflow.md was written before the push and is out of date. The repository was pushed on 12 October 2026 (all branches and both tags) and the live check in this video confirms it: public repository, 19 branches, tags v1.0.0 and v1.1.0. What still does not exist on GitHub are issues and pull requests; the PR texts are prepared in docs/pull-requests/.
