# Prepare a new release

## Update `CHANGELOG`

For each new release, the `CHANGELOG` needs to be updated in the following way:

1. Rename the `## Unreleased` section to the version and date of the upcoming release
2. Add a link to the upcoming release at the bottom of the document
3. If not already done: document any user-related changes for the upcoming release[^1]
4. Remove any empty sections for the upcoming release[^2]
5. Update the `[unreleased]` link to point to the changes made since the upcoming release

??? example "`CHANGELOG` update in preparation of upcoming minor release"

    ```md
    # Changelog

    The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
    and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

    {++## [Unreleased]++}

    {++### Added++}
    {++### Fixed++}
    {++### Changed++}
    {++### Removed++}

    {--## [Unreleased]--}{++## [0.1.0] - 2023-11-30++}

    {++Minor update to `foo`, deprecate `bar` in favor of `flux` and remove `baz`.++}

    {--### Added--}
    ### Fixed

    - Issue when calling `foo` twice in a row (#12)

    ### Changed

    - `bar` is deprecated and should no longer be used. Use `flux` instead.

    ### Removed

    - `baz` is removed (deprecated since [0.0.1])

    ## [0.0.2] - 2023-11-27

    ...

    [unreleased]: https://github.com/username/project-name/compare/{--v0.0.2--}{++v0.1.0++}...HEAD
    {++[0.1.0]: https://github.com/username/project-name/releases/tag/v0.1.0++}
    [0.0.2]: https://github.com/username/project-name/releases/tag/v0.0.2
    [0.0.1]: https://github.com/username/project-name/releases/tag/v0.0.1
    ```

!!! note "Commit Convention"

    When using [conventional commits], [gitmoji] or any other commit message convention that allows to parse the scope of commits based on their message, updating the changelog could be automated.

    However, [keep a changelog advises against][log-diffs] generating the changelog based on commit messages, as commit messages are written for developers, while the changelog should be written for end users.

[gitmoji]: https://gitmoji.dev/
[conventional commits]: https://www.conventionalcommits.org/
[keep a changelog]: https://keepachangelog.com
[log-diffs]: https://keepachangelog.com/en/1.1.0/#log-diffs
[^1]: Ideally, the CHANGELOG was already updated when each change was implemented
[^2]: For example, the `## Added` section should be omitted when nothing was added since the last release

!!! note "Bumpversion"

    If you chose to use `bumpversion`, the remaining steps are taken care of by the `bumpversion` command.

## Bump version number

With all changes for the upcoming release in place, you are ready to bump the version number.

Increase the version number according to your versioning schema (e.g. [semantic versioning]) and commit the new version to your project.

## Tag release commit

Now it is time to tag your most recent commit and push it to the remote. Make sure you committed everything that should be part of the upcoming release. Then

```sh
git tag -m "bump v0.0.2 -> v0.1.0" v0.1.0
git push --tags
```

## Optional: Create release on your remote platform

Both GitHub and GitLab provide ways to create releases based on git tags with additional metadata and artifacts, such as binaries or release notes.

=== "GitHub"

    [GitHubs][github] CLI [`gh`][gh] provides a nice interactive command to generate a release based on git tags:

    ```console
    $ gh release create
    ? Tag name {==v0.1.0==}
    ? Title (optional) (v0.1.0) {==v0.1.0==}
    ? Release notes {==Write using generated notes as template==}
    ? Is this a prerelease? {==No==}
    ? Submit? {==Publish release==}
    ```

=== "GitLab"

    [GitLabs][gitlab] CLI [`glab`][glab] also provides the option to create a release:

    ```console
    $ glab release create v0.1.0
    ? Release Title (optional) {==v0.1.0==}
    ? Release notes {==Write my own==}
    ✓ Release created
    ```

    `glab` will create the specified tag if it does not already exist.

[gh]: https://cli.github.com/
[glab]: https://gitlab.com/gitlab-org/cli
