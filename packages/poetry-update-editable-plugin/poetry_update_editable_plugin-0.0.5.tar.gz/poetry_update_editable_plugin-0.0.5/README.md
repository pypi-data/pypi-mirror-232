# Poetry `update-editable` Plugin

Has this ever happened to you?


## Installation

The recommended way to install this plugin is via poetry plugin installation method:

```bash
poetry self add poetry-update-editable-plugin
```

## Usage

Install editable dependencies:

```bash
poetry update-editable
```

This will install any dpeendencies with `{ develop = true }`

### Available Options

* `--dry-run`: Output the operations but do not execute anything (implicitly enables --verbose).
* `--without`: The dependency groups to ignore when exporting (multiple values allowed).
* `--with`: The optional dependency groups to include when exporting (multiple values allowed).
* `--only`: The only dependency groups to include when exporting (multiple values allowed).
