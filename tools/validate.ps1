<#
.SYNOPSIS
  The repository checks, for those who would rather not install Python: the same checks as tools/validate.py.

.DESCRIPTION
      powershell -ExecutionPolicy Bypass -File tools\validate.ps1      (Windows PowerShell 5.1, built into Windows)
      pwsh -File tools/validate.ps1                                    (PowerShell 7 on Windows, macOS or Linux)

  Checks:
    - every SKILL.md starts with frontmatter holding `name` (equal to its folder) and `description`, and no two
      skills share a name, even in different plugins;
    - .claude-plugin/marketplace.json and every plugin.json parse, and they agree: every listed plugin exists, has a
      plugin.json with the same name, and names are unique; every .mcp.json parses;
    - no absolute personal paths, no email addresses, no tokens or keys (simple patterns);
    - text files are UTF-8, end with a newline and have no trailing spaces;
    - Markdown lines are at most 120 characters outside tables, code blocks and frontmatter.

  Exits 1 with one message per problem, 0 when everything passes. tools/validate.py stays the reference (CI runs it);
  this script reads frontmatter with a small parser of its own (top-level `key: value` lines, quoted values and
  `>` / `|` blocks), which covers what skills use. JSON error texts differ from Python's; the checks are the same.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$MaxMdLine = 120
$MaxDescription = 1536
$NameRe = '^[a-z0-9][a-z0-9-]*$'
$TextExtensions = @('.md', '.json', '.py', '.yml', '.yaml', '.asm', '.txt', '.lua', '.sh', '.ps1', '.toml')
$TextNames = @('LICENSE', 'CODEOWNERS', '.gitignore', '.gitattributes')
$SkipDirs = @('.git', '__pycache__', 'node_modules')

# Patterns are assembled from pieces so this file does not match itself.
$Slash = '/'
$Back = [regex]::Escape('\')
$PersonalPaths = @(
    @('a Windows user folder', ('(?i)[A-Za-z]:' + $Back + 'Users' + $Back)),
    @('a Windows user folder', ('(?i)[A-Za-z]:' + $Slash + 'Users' + $Slash)),
    @('a Linux home folder', ($Slash + 'home' + $Slash)),
    @('a macOS user folder', ('(?<![\w.~])' + $Slash + 'Users' + $Slash))
)
$Email = '[A-Za-z0-9._%+-]+' + '@' + '[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}'
$Secrets = @(
    @('a GitHub token', ('\b(gh' + '[pousr]_[A-Za-z0-9]{30,}|github' + '_pat_[A-Za-z0-9_]{20,})')),
    @('an Anthropic key', ('\bsk-' + 'ant-[A-Za-z0-9_-]{20,}')),
    @('an OpenAI-style key', ('\bsk-' + '[A-Za-z0-9]{32,}')),
    @('an AWS access key', ('\bAKIA' + '[0-9A-Z]{16}\b')),
    @('a Google API key', ('\bAIza' + '[0-9A-Za-z_-]{35}')),
    @('a Slack token', ('\bxox' + '[abprs]-[A-Za-z0-9-]{10,}')),
    @('a private key', ('-----BEGIN [A-Z ]*PRIVATE ' + 'KEY-----')),
    @('a bearer token', ('Bearer\s+[A-Za-z0-9._~+/-]{24,}'))
)

$script:Problems = New-Object System.Collections.Generic.List[string]
$Utf8Strict = New-Object System.Text.UTF8Encoding($false, $true)

function Get-Rel([string]$Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetFullPath($Root)
    if ($full.Length -le $root.Length) { return '.' }
    return $full.Substring($root.Length).TrimStart('\', '/').Replace('\', '/')
}

function Add-Problem([string]$Path, [string]$Message, $Line = $null) {
    $where = Get-Rel $Path
    if ($Line) { $where = "${where}:$Line" }
    $script:Problems.Add("${where}: $Message")
}

function Get-RepoFiles {
    $all = Get-ChildItem -LiteralPath $Root -Recurse -File -Force
    foreach ($f in $all) {
        $relDirs = (Get-Rel $f.DirectoryName).Split('/')
        $skip = $false
        foreach ($d in $relDirs) { if ($SkipDirs -contains $d) { $skip = $true } }
        if (-not $skip) { $f.FullName }
    }
}

function Test-IsText([string]$Path) {
    $name = [System.IO.Path]::GetFileName($Path)
    $ext = [System.IO.Path]::GetExtension($name).ToLowerInvariant()
    return ($TextNames -contains $name) -or ($TextExtensions -contains $ext)
}

function Read-Text([string]$Path) {
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    try { return $Utf8Strict.GetString($bytes) }
    catch { Add-Problem $Path "not UTF-8 ($($_.Exception.Message))"; return $null }
}

function Read-Json([string]$Path) {
    $text = Read-Text $Path
    if ($null -eq $text) { return $null }
    try { return ($text | ConvertFrom-Json) }
    catch { Add-Problem $Path "invalid JSON: $($_.Exception.Message)"; return $null }
}

function Get-Prop($Object, [string]$Name) {
    if ($null -eq $Object) { return $null }
    $p = $Object.PSObject.Properties[$Name]
    if ($null -eq $p) { return $null }
    return $p.Value
}

function Test-NonEmptyString($Value) {
    return ($Value -is [string]) -and ($Value.Trim().Length -gt 0)
}

# Returns @(frontmatter text, lines it spans including both markers) or @($null, 0).
function Split-Frontmatter([string]$Text) {
    $lines = $Text.Split("`n")
    if ($lines.Count -eq 0 -or $lines[0].Trim() -ne '---') { return @($null, 0) }
    for ($i = 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i].Trim() -eq '---') {
            return @((($lines[1..($i - 1)] | ForEach-Object { $_.TrimEnd("`r") }) -join "`n"), ($i + 1))
        }
    }
    return @($null, 0)
}

# A small YAML reader for skill frontmatter: top-level `key: value`, quoted values, `>` / `|` blocks, comments.
function ConvertFrom-Frontmatter([string]$Front) {
    $data = @{}
    $lines = if ($Front.Length) { $Front.Split("`n") } else { @() }
    $i = 0
    while ($i -lt $lines.Count) {
        $line = $lines[$i]
        if ($line.Trim().Length -eq 0 -or $line.TrimStart().StartsWith('#')) { $i++; continue }
        $m = [regex]::Match($line, '^([A-Za-z0-9_-]+):(?:\s+(.*))?$')
        if (-not $m.Success) { throw "line $($i + 1): expected `key: value` at the top level" }
        $key = $m.Groups[1].Value
        $value = if ($m.Groups[2].Success) { $m.Groups[2].Value.Trim() } else { '' }
        $i++
        if ($value -match '^[>|][+-]?$') {
            $fold = $value.StartsWith('>')
            $parts = New-Object System.Collections.Generic.List[string]
            while ($i -lt $lines.Count -and ($lines[$i].Trim().Length -eq 0 -or $lines[$i] -match '^\s+')) {
                $parts.Add($lines[$i].Trim()); $i++
            }
            $value = if ($fold) { ($parts -join ' ').Trim() } else { ($parts -join "`n").Trim() }
        } elseif ($value.Length -eq 0) {
            $nested = $false
            while ($i -lt $lines.Count -and $lines[$i] -match '^\s+') { $nested = $true; $i++ }
            $value = if ($nested) { '(mapping)' } else { $null }
        } elseif ($value.StartsWith('"')) {
            if (-not ($value.Length -ge 2 -and $value.EndsWith('"'))) { throw "line ${i}: unclosed double quote" }
            $value = [regex]::Unescape($value.Substring(1, $value.Length - 2))
        } elseif ($value.StartsWith("'")) {
            if (-not ($value.Length -ge 2 -and $value.EndsWith("'"))) { throw "line ${i}: unclosed single quote" }
            $value = $value.Substring(1, $value.Length - 2).Replace("''", "'")
        } else {
            if ($value -match '\s#') { $value = ($value -replace '\s+#.*$', '').Trim() }
            if ($value -match ': ') { throw "line ${i}: a plain value may not contain ': ' (quote it)" }
        }
        $data[$key] = $value
    }
    return $data
}

# ---------------------------------------------------------------- text hygiene and privacy

function Test-TextFile([string]$Path, [string]$Text) {
    if ($Text.Length -gt 0 -and -not $Text.EndsWith("`n")) { Add-Problem $Path 'no final newline' }
    $lines = $Text.Split("`n")
    $isMarkdown = $Path.EndsWith('.md')
    $frontLines = 0
    if ($isMarkdown) { $frontLines = (Split-Frontmatter $Text)[1] }
    $inCode = $false
    for ($n = 0; $n -lt $lines.Count; $n++) {
        $number = $n + 1
        $line = $lines[$n].TrimEnd("`r")
        if ($line -ne $line.TrimEnd(' ', "`t")) { Add-Problem $Path 'trailing spaces' $number }
        foreach ($pp in $PersonalPaths) {
            if ([regex]::IsMatch($line, $pp[1])) { Add-Problem $Path "looks like $($pp[0]) (personal absolute path)" $number }
        }
        $em = [regex]::Match($line, $Email)
        if ($em.Success) { Add-Problem $Path "looks like an email address: $($em.Value)" $number }
        foreach ($s in $Secrets) {
            if ([regex]::IsMatch($line, $s[1])) { Add-Problem $Path "looks like $($s[0])" $number }
        }
        if (-not $isMarkdown) { continue }
        $stripped = $line.TrimStart()
        if ($stripped.StartsWith('```') -or $stripped.StartsWith('~~~')) { $inCode = -not $inCode; continue }
        if ($inCode -or $number -le $frontLines -or $stripped.StartsWith('|')) { continue }
        if ($line.Length -gt $MaxMdLine) {
            Add-Problem $Path ("Markdown line of $($line.Length) characters (at most $MaxMdLine outside tables " +
                "and code blocks)") $number
        }
    }
    if ($isMarkdown -and $inCode) { Add-Problem $Path 'unclosed code block' }
}

# ---------------------------------------------------------------- skills

$script:SkillNames = @{}

function Test-Skill([string]$Path, [string]$Text) {
    $folder = Split-Path -Leaf (Split-Path -Parent $Path)
    if ($script:SkillNames.ContainsKey($folder)) {
        Add-Problem $Path ("skill name ``$folder`` is already used by $(Get-Rel $script:SkillNames[$folder]): " +
            'improve that skill or choose another name')
    } else { $script:SkillNames[$folder] = $Path }
    $front = (Split-Frontmatter $Text)[0]
    if ($null -eq $front) { Add-Problem $Path 'SKILL.md must start with YAML frontmatter between --- lines'; return }
    try { $data = ConvertFrom-Frontmatter $front }
    catch { Add-Problem $Path "invalid YAML frontmatter: $($_.Exception.Message)"; return }
    $name = $data['name']
    $description = $data['description']
    if (-not (Test-NonEmptyString $name)) { Add-Problem $Path 'frontmatter needs a `name`' }
    elseif ($name -cne $folder) { Add-Problem $Path "frontmatter name ``$name`` differs from its folder ``$folder``" }
    elseif ($name -cnotmatch $NameRe) { Add-Problem $Path "skill name ``$name`` must be lowercase letters, digits and hyphens" }
    if (-not (Test-NonEmptyString $description)) { Add-Problem $Path 'frontmatter needs a `description`' }
    else {
        $combined = $description + [string]$data['when_to_use']
        if ($combined.Length -gt $MaxDescription) {
            Add-Problem $Path "description is $($combined.Length) characters; Claude Code truncates at $MaxDescription"
        }
    }
    if (([regex]::Matches($Text, "`n")).Count -gt 500) {
        Add-Problem $Path 'SKILL.md is over 500 lines: move detail into references/'
    }
}

# ---------------------------------------------------------------- plugins and the marketplace

function Test-PluginManifest([string]$PluginDir, [string]$ExpectedName = $null) {
    $manifestPath = Join-Path (Join-Path $PluginDir '.claude-plugin') 'plugin.json'
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { Add-Problem $PluginDir 'no .claude-plugin/plugin.json'; return $null }
    $manifest = Read-Json $manifestPath
    if ($null -eq $manifest) { return $null }
    if ($manifest -isnot [System.Management.Automation.PSCustomObject]) {
        Add-Problem $manifestPath 'plugin.json must be a JSON object'; return $null
    }
    $name = Get-Prop $manifest 'name'
    if (-not ($name -is [string]) -or $name -cnotmatch $NameRe) {
        Add-Problem $manifestPath '`name` must be kebab-case (lowercase letters, digits and hyphens)'
    } elseif ($ExpectedName -and $name -cne $ExpectedName) {
        Add-Problem $manifestPath "name ``$name`` differs from the marketplace entry ``$ExpectedName``"
    }
    foreach ($field in @('description', 'version')) {
        if (-not (Test-NonEmptyString (Get-Prop $manifest $field))) { Add-Problem $manifestPath "``$field`` is missing" }
    }
    $author = Get-Prop $manifest 'author'
    if ($author -isnot [System.Management.Automation.PSCustomObject] -or -not (Test-NonEmptyString ([string](Get-Prop $author 'name')))) {
        Add-Problem $manifestPath '`author.name` is missing'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $PluginDir 'README.md') -PathType Leaf)) {
        Add-Problem $PluginDir 'every plugin needs a README.md (what it does, what it was tested on)'
    }
    if (Test-Path -LiteralPath (Join-Path $PluginDir 'CLAUDE.md') -PathType Leaf) {
        Add-Problem $PluginDir 'a CLAUDE.md at a plugin root is not loaded by Claude Code: use a skill'
    }
    return $manifest
}

function Test-Marketplace {
    $listed = New-Object System.Collections.Generic.HashSet[string]([StringComparer]::OrdinalIgnoreCase)
    $path = Join-Path (Join-Path $Root '.claude-plugin') 'marketplace.json'
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { Add-Problem $Root 'no .claude-plugin/marketplace.json'; return ,$listed }
    $market = Read-Json $path
    if ($market -isnot [System.Management.Automation.PSCustomObject]) {
        if ($null -ne $market) { Add-Problem $path 'marketplace.json must be a JSON object' }
        return ,$listed
    }
    $mname = Get-Prop $market 'name'
    if (-not ($mname -is [string]) -or $mname -cnotmatch $NameRe) { Add-Problem $path '`name` must be kebab-case' }
    $owner = Get-Prop $market 'owner'
    if ($owner -isnot [System.Management.Automation.PSCustomObject] -or -not (Test-NonEmptyString ([string](Get-Prop $owner 'name')))) {
        Add-Problem $path '`owner.name` is required'
    }
    $plugins = Get-Prop $market 'plugins'
    if ($null -eq $plugins -or $plugins -isnot [array] -or $plugins.Count -eq 0) {
        Add-Problem $path '`plugins` must be a non-empty list'; return ,$listed
    }
    $seen = New-Object System.Collections.Generic.HashSet[string]
    for ($index = 0; $index -lt $plugins.Count; $index++) {
        $entry = $plugins[$index]
        $label = "plugins[$index]"
        if ($entry -isnot [System.Management.Automation.PSCustomObject]) { Add-Problem $path "$label must be an object"; continue }
        $name = Get-Prop $entry 'name'
        $source = Get-Prop $entry 'source'
        if (-not ($name -is [string]) -or $name -cnotmatch $NameRe) { Add-Problem $path "${label}: ``name`` must be kebab-case"; continue }
        if (-not $seen.Add($name)) { Add-Problem $path "${label}: duplicate plugin name ``$name``" }
        $desc = Get-Prop $entry 'description'
        if (-not (Test-NonEmptyString $desc)) { Add-Problem $path "$label (${name}): ``description`` is missing" }
        if (-not ($source -is [string]) -or -not $source.StartsWith('./') -or ($source.Split('/') -contains '..')) {
            Add-Problem $path "$label (${name}): ``source`` must be a relative path starting with ./ and without .."
            continue
        }
        $pluginDir = [System.IO.Path]::GetFullPath((Join-Path $Root $source.Substring(2)))
        if (-not (Test-Path -LiteralPath $pluginDir -PathType Container)) {
            Add-Problem $path "$label (${name}): source folder $source does not exist"; continue
        }
        [void]$listed.Add($pluginDir.TrimEnd('\', '/'))
        $manifest = Test-PluginManifest $pluginDir $name
        $mdesc = Get-Prop $manifest 'description'
        if ($manifest -and ($desc -is [string]) -and $mdesc -and ($desc -cne $mdesc)) {
            Add-Problem $path "$label (${name}): description differs from its plugin.json"
        }
    }
    return ,$listed
}

function Test-UnlistedPlugins($Listed) {
    $template = [System.IO.Path]::GetFullPath((Join-Path $Root 'plugins/community/_template')).TrimEnd('\', '/')
    foreach ($path in $script:Files) {
        if ([System.IO.Path]::GetFileName($path) -ne 'plugin.json') { continue }
        if ((Split-Path -Leaf (Split-Path -Parent $path)) -ne '.claude-plugin') { continue }
        $pluginDir = ([System.IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $path)))).TrimEnd('\', '/')
        if ($Listed.Contains($pluginDir)) { continue }
        if ($pluginDir -eq $template) { [void](Test-PluginManifest $pluginDir); continue }
        Add-Problem $path 'this plugin is not listed in .claude-plugin/marketplace.json'
    }
}

function Test-McpFiles {
    foreach ($path in $script:Files) {
        if ([System.IO.Path]::GetFileName($path) -ne '.mcp.json') { continue }
        $data = Read-Json $path
        if ($null -eq $data) { continue }
        $servers = $null
        if ($data -is [System.Management.Automation.PSCustomObject]) {
            $servers = Get-Prop $data 'mcpServers'
            if ($null -eq $servers) { $servers = $data }
        }
        if ($servers -isnot [System.Management.Automation.PSCustomObject] -or @($servers.PSObject.Properties).Count -eq 0) {
            Add-Problem $path 'expected an object of MCP servers (optionally under `mcpServers`)'; continue
        }
        foreach ($p in $servers.PSObject.Properties) {
            $server = $p.Value
            if ($server -isnot [System.Management.Automation.PSCustomObject] -or
                -not ((Get-Prop $server 'url') -or (Get-Prop $server 'command'))) {
                Add-Problem $path "server ``$($p.Name)`` needs a ``url`` or a ``command``"
            }
        }
    }
}

# ---------------------------------------------------------------- main

$script:Files = @(Get-RepoFiles)
foreach ($path in $script:Files) {
    if (-not (Test-IsText $path)) { continue }
    $text = Read-Text $path
    if ($null -eq $text) { continue }
    Test-TextFile $path $text
    if ($path.EndsWith('.json')) {
        try { [void]($text | ConvertFrom-Json) } catch { Add-Problem $path "invalid JSON: $($_.Exception.Message)" }
    }
    if ([System.IO.Path]::GetFileName($path) -eq 'SKILL.md') { Test-Skill $path $text }
}
$listedDirs = Test-Marketplace
Test-UnlistedPlugins $listedDirs
Test-McpFiles

# Report each problem once, in a stable order.
$unique = [string[]]@($script:Problems | Select-Object -Unique)
[Array]::Sort($unique, [StringComparer]::Ordinal)
if ($unique.Count -gt 0) {
    foreach ($m in $unique) { Write-Output "FAIL $m" }
    Write-Output ''
    Write-Output "validate.ps1: $($unique.Count) problem(s)"
    exit 1
}
Write-Output 'validate.ps1: all checks passed'
exit 0
