#!/usr/bin/env python3
"""The repository checks, run locally and on every pull request.

    python tools/validate.py

Checks:
  - every SKILL.md starts with valid YAML frontmatter holding `name` (equal to its folder) and `description`, and no
    two skills share a name, even in different plugins;
  - .claude-plugin/marketplace.json and every plugin.json parse, and they agree: every listed plugin exists, has a
    plugin.json with the same name, and names are unique; every .mcp.json parses;
  - no absolute personal paths, no email addresses, no tokens or keys (simple patterns);
  - text files are UTF-8, end with a newline and have no trailing spaces;
  - Markdown lines are at most 120 characters outside tables, code blocks and frontmatter.

Exits 1 with one message per problem, 0 when everything passes. Needs Python 3.9+ and PyYAML.
"""

import json
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("validate.py: PyYAML is required: run  python -m pip install pyyaml  (macOS/Linux: python3 -m pip "
             "install --user pyyaml, or your system's python3-yaml package), or use tools/validate.ps1 instead")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_MD_LINE = 120
MAX_DESCRIPTION = 1536
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
TEXT_EXTENSIONS = {".md", ".json", ".py", ".yml", ".yaml", ".asm", ".txt", ".lua", ".sh", ".ps1", ".toml", ".c", ".h",
                   ".inc", ".bas"}
TEXT_SUFFIXES = ("_bas", "_asm", "_c", "_h", "_txt")   # QDOS names: the QL writes program_bas, not program.bas
TEXT_NAMES = {"LICENSE", "CODEOWNERS", ".gitignore", ".gitattributes"}
SKIP_DIRS = {".git", "__pycache__", "node_modules"}

# Patterns are assembled from pieces so this file does not match itself.
SLASH = "/"
BACKSLASH = "\\"
PERSONAL_PATHS = [
    ("a Windows user folder", re.compile(r"[A-Za-z]:" + re.escape(BACKSLASH) + "Users" + re.escape(BACKSLASH),
                                         re.IGNORECASE)),
    ("a Windows user folder", re.compile(r"[A-Za-z]:" + SLASH + "Users" + SLASH, re.IGNORECASE)),
    ("a Linux home folder", re.compile(SLASH + "home" + SLASH)),
    ("a macOS user folder", re.compile(r"(?<![\w.~])" + SLASH + "Users" + SLASH)),
]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+" + "@" + r"[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
SECRETS = [
    ("a GitHub token", re.compile(r"\b(gh" + "[pousr]_[A-Za-z0-9]{30,}|github" + "_pat_[A-Za-z0-9_]{20,})")),
    ("an Anthropic key", re.compile(r"\bsk-" + r"ant-[A-Za-z0-9_-]{20,}")),
    ("an OpenAI-style key", re.compile(r"\bsk-" + r"[A-Za-z0-9]{32,}")),
    ("an AWS access key", re.compile(r"\bAKIA" + r"[0-9A-Z]{16}\b")),
    ("a Google API key", re.compile(r"\bAIza" + r"[0-9A-Za-z_-]{35}")),
    ("a Slack token", re.compile(r"\bxox" + r"[abprs]-[A-Za-z0-9-]{10,}")),
    ("a private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE " + "KEY-----")),
    ("a bearer token", re.compile(r"Bearer\s+[A-Za-z0-9._~+/-]{24,}")),
]

problems = []


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def problem(path, message, line=None):
    where = rel(path) + (f":{line}" if line else "")
    problems.append(f"{where}: {message}")


def walk_files():
    for directory, subdirs, files in os.walk(ROOT):
        subdirs[:] = sorted(d for d in subdirs if d not in SKIP_DIRS)
        for name in sorted(files):
            yield os.path.join(directory, name)


def is_text(path):
    name = os.path.basename(path)
    return (name in TEXT_NAMES or os.path.splitext(name)[1].lower() in TEXT_EXTENSIONS
            or name.lower().endswith(TEXT_SUFFIXES))


def read_text(path):
    with open(path, "rb") as handle:
        data = handle.read()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        problem(path, f"not UTF-8 ({error})")
        return None


def load_json(path):
    text = read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        problem(path, f"invalid JSON: {error}")
        return None


def split_frontmatter(text):
    """Return (frontmatter text, number of lines it spans including both markers) or (None, 0)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), index + 1
    return None, 0


# ---------------------------------------------------------------- text hygiene and privacy

def check_text_file(path, text):
    if text and not text.endswith("\n"):
        problem(path, "no final newline")
    lines = text.split("\n")
    is_markdown = path.endswith(".md")
    _, frontmatter_lines = split_frontmatter(text) if is_markdown else (None, 0)
    in_code = False
    for number, raw in enumerate(lines, start=1):
        line = raw[:-1] if raw.endswith("\r") else raw
        if line != line.rstrip(" \t"):
            problem(path, "trailing spaces", number)
        for label, pattern in PERSONAL_PATHS:
            if pattern.search(line):
                problem(path, f"looks like {label} (personal absolute path)", number)
        if EMAIL.search(line):
            problem(path, f"looks like an email address: {EMAIL.search(line).group(0)}", number)
        for label, pattern in SECRETS:
            if pattern.search(line):
                problem(path, f"looks like {label}", number)
        if not is_markdown:
            continue
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code = not in_code
            continue
        if in_code or number <= frontmatter_lines or stripped.startswith("|"):
            continue
        if len(line) > MAX_MD_LINE:
            problem(path, f"Markdown line of {len(line)} characters (at most {MAX_MD_LINE} outside tables "
                          "and code blocks)", number)
    if is_markdown and in_code:
        problem(path, "unclosed code block")


# ---------------------------------------------------------------- skills

SKILL_NAMES = {}


def check_skill(path, text):
    folder = os.path.basename(os.path.dirname(path))
    if folder in SKILL_NAMES:
        problem(path, f"skill name `{folder}` is already used by {rel(SKILL_NAMES[folder])}: "
                      "improve that skill or choose another name")
    else:
        SKILL_NAMES[folder] = path
    frontmatter, _ = split_frontmatter(text)
    if frontmatter is None:
        problem(path, "SKILL.md must start with YAML frontmatter between --- lines")
        return
    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as error:
        problem(path, f"invalid YAML frontmatter: {error}")
        return
    if not isinstance(data, dict):
        problem(path, "frontmatter must be a YAML mapping")
        return
    name = data.get("name")
    description = data.get("description")
    if not isinstance(name, str) or not name.strip():
        problem(path, "frontmatter needs a `name`")
    elif name != folder:
        problem(path, f"frontmatter name `{name}` differs from its folder `{folder}`")
    elif not NAME_RE.match(name):
        problem(path, f"skill name `{name}` must be lowercase letters, digits and hyphens")
    if not isinstance(description, str) or not description.strip():
        problem(path, "frontmatter needs a `description`")
    else:
        combined = description + str(data.get("when_to_use") or "")
        if len(combined) > MAX_DESCRIPTION:
            problem(path, f"description is {len(combined)} characters; Claude Code truncates at {MAX_DESCRIPTION}")
    if text.count("\n") > 500:
        problem(path, "SKILL.md is over 500 lines: move detail into references/")


# ---------------------------------------------------------------- plugins and the marketplace

def check_plugin_manifest(plugin_dir, expected_name=None):
    manifest_path = os.path.join(plugin_dir, ".claude-plugin", "plugin.json")
    if not os.path.isfile(manifest_path):
        problem(plugin_dir, "no .claude-plugin/plugin.json")
        return None
    manifest = load_json(manifest_path)
    if manifest is None:
        return None
    if not isinstance(manifest, dict):
        problem(manifest_path, "plugin.json must be a JSON object")
        return None
    name = manifest.get("name")
    if not isinstance(name, str) or not NAME_RE.match(name or ""):
        problem(manifest_path, "`name` must be kebab-case (lowercase letters, digits and hyphens)")
    elif expected_name and name != expected_name:
        problem(manifest_path, f"name `{name}` differs from the marketplace entry `{expected_name}`")
    for field in ("description", "version"):
        if not isinstance(manifest.get(field), str) or not manifest.get(field).strip():
            problem(manifest_path, f"`{field}` is missing")
    author = manifest.get("author")
    if not isinstance(author, dict) or not str(author.get("name", "")).strip():
        problem(manifest_path, "`author.name` is missing")
    if not os.path.isfile(os.path.join(plugin_dir, "README.md")):
        problem(plugin_dir, "every plugin needs a README.md (what it does, what it was tested on)")
    if os.path.isfile(os.path.join(plugin_dir, "CLAUDE.md")):
        problem(plugin_dir, "a CLAUDE.md at a plugin root is not loaded by Claude Code: use a skill")
    return manifest


def check_marketplace():
    path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    if not os.path.isfile(path):
        problem(ROOT, "no .claude-plugin/marketplace.json")
        return set()
    market = load_json(path)
    if not isinstance(market, dict):
        if market is not None:
            problem(path, "marketplace.json must be a JSON object")
        return set()
    if not isinstance(market.get("name"), str) or not NAME_RE.match(market.get("name") or ""):
        problem(path, "`name` must be kebab-case")
    owner = market.get("owner")
    if not isinstance(owner, dict) or not str(owner.get("name", "")).strip():
        problem(path, "`owner.name` is required")
    plugins = market.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        problem(path, "`plugins` must be a non-empty list")
        return set()
    seen, listed_dirs = set(), set()
    for index, entry in enumerate(plugins):
        label = f"plugins[{index}]"
        if not isinstance(entry, dict):
            problem(path, f"{label} must be an object")
            continue
        name, source = entry.get("name"), entry.get("source")
        if not isinstance(name, str) or not NAME_RE.match(name or ""):
            problem(path, f"{label}: `name` must be kebab-case")
            continue
        if name in seen:
            problem(path, f"{label}: duplicate plugin name `{name}`")
        seen.add(name)
        if not isinstance(entry.get("description"), str) or not entry["description"].strip():
            problem(path, f"{label} ({name}): `description` is missing")
        if not isinstance(source, str) or not source.startswith("./") or ".." in source.split("/"):
            problem(path, f"{label} ({name}): `source` must be a relative path starting with ./ and without ..")
            continue
        plugin_dir = os.path.normpath(os.path.join(ROOT, source))
        if not os.path.isdir(plugin_dir):
            problem(path, f"{label} ({name}): source folder {source} does not exist")
            continue
        listed_dirs.add(plugin_dir)
        manifest = check_plugin_manifest(plugin_dir, expected_name=name)
        if manifest and isinstance(entry.get("description"), str) and manifest.get("description") \
                and entry["description"] != manifest["description"]:
            problem(path, f"{label} ({name}): description differs from its plugin.json")
    return listed_dirs


def check_unlisted_plugins(listed_dirs):
    template = os.path.join(ROOT, "plugins", "community", "_template")
    for path in walk_files():
        if os.path.basename(path) != "plugin.json" or os.path.basename(os.path.dirname(path)) != ".claude-plugin":
            continue
        plugin_dir = os.path.dirname(os.path.dirname(path))
        if plugin_dir in listed_dirs:
            continue
        if os.path.normpath(plugin_dir) == os.path.normpath(template):
            check_plugin_manifest(plugin_dir)
            continue
        problem(path, "this plugin is not listed in .claude-plugin/marketplace.json")


def check_mcp_files():
    for path in walk_files():
        if os.path.basename(path) != ".mcp.json":
            continue
        data = load_json(path)
        if data is None:
            continue
        servers = data.get("mcpServers", data) if isinstance(data, dict) else None
        if not isinstance(servers, dict) or not servers:
            problem(path, "expected an object of MCP servers (optionally under `mcpServers`)")
            continue
        for name, server in servers.items():
            if not isinstance(server, dict) or not (server.get("url") or server.get("command")):
                problem(path, f"server `{name}` needs a `url` or a `command`")


# ---------------------------------------------------------------- main

def main():
    for path in walk_files():
        if not is_text(path):
            continue
        text = read_text(path)
        if text is None:
            continue
        check_text_file(path, text)
        if path.endswith(".json"):
            try:
                json.loads(text)
            except json.JSONDecodeError as error:
                problem(path, f"invalid JSON: {error}")
        if os.path.basename(path) == "SKILL.md":
            check_skill(path, text)
    listed = check_marketplace()
    check_unlisted_plugins(listed)
    check_mcp_files()

    # Report each problem once, in a stable order.
    unique = sorted(set(problems))
    if unique:
        for message in unique:
            print(f"FAIL {message}")
        print(f"\nvalidate.py: {len(unique)} problem(s)")
        return 1
    print("validate.py: all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
