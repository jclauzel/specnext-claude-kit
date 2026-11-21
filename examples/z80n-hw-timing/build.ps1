<#
  build.ps1 - build z80ntime.nex, the Z80N timing test, with z88dk (+zxn, zsdcc, newlib).

  USAGE
    .\build.ps1                       # z88dk in C:\z88dk, or in $env:Z88DK_DIR
    .\build.ps1 -Z88dk D:\tools\z88dk

  Writes build\z80ntime.nex and build\z80ntime.map (generated output, kept out of git), then prints the .nex's size
  and MD5, the address range of the measured blocks and the room left under the stack.
#>
[CmdletBinding()]
param(
    [string]$Z88dk = $(if ($env:Z88DK_DIR) { $env:Z88DK_DIR } else { "C:\z88dk" })
)

$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$zcc = Join-Path $Z88dk "bin\zcc.exe"
if (-not (Test-Path -LiteralPath $zcc)) { throw "zcc not found: $zcc (give -Z88dk <folder> or set Z88DK_DIR)" }
$env:ZCCCFG = Join-Path $Z88dk "lib\config"
$env:PATH = (Join-Path $Z88dk "bin") + ";" + $env:PATH

$out = Join-Path $PSScriptRoot "build"
New-Item -ItemType Directory -Force -Path $out | Out-Null
Remove-Item -Path (Join-Path $out "z80ntime*") -Force -ErrorAction SilentlyContinue

# -startup=0: the 32-column ULA terminal for printf; -clib=sdcc_iy: zsdcc with newlib (IY belongs to the library)
$zargs = @("+zxn", "-startup=0", "-clib=sdcc_iy", "-SO3", "--opt-code-size", "-pragma-include:zpragma.inc",
          "z80ntime.c", "timing.asm", "-subtype=nex", "-Cz--clean", "-create-app", "-m", "-o", "build/z80ntime")
Write-Host ("zcc " + ($zargs -join " "))
& $zcc @zargs
if ($LASTEXITCODE) { throw "zcc failed ($LASTEXITCODE)" }

$nex = Join-Path $out "z80ntime.nex"
$map = Join-Path $out "z80ntime.map"
if (-not (Test-Path -LiteralPath $nex)) { throw "no $nex written" }

# The measured code and the stack must stay at $8000 and up (banks 2 and 0, never contended at 3.5 MHz).
function MapAddr([string]$sym) {
    $hit = Select-String -LiteralPath $map -CaseSensitive -Pattern ('^' + $sym + '\s+=\s+\$([0-9A-Fa-f]{4})') |
        Select-Object -First 1
    if (-not $hit) { throw "no $sym in $map" }
    [Convert]::ToInt32($hit.Matches[0].Groups[1].Value, 16)
}
$first = MapAddr "_blk_empty"
$last = MapAddr "_blk_addhlde"
$tail = MapAddr "__BSS_END_tail"
if ($first -lt 0x8000) { throw ("the blocks start at {0:X4}, below 8000 (contended memory)" -f $first) }
$sp = 65368 - 512    # REGISTER_SP minus the crt's stack size
if ($tail -gt $sp) { throw ("the program ends at {0:X4}, into the stack (from {1:X4})" -f $tail, $sp) }

$md5 = (Get-FileHash -LiteralPath $nex -Algorithm MD5).Hash
Write-Host ("built {0}: {1} bytes, MD5 {2}" -f $nex, (Get-Item -LiteralPath $nex).Length, $md5)
Write-Host ("blocks from {0:X4} (_blk_empty) to {1:X4} (_blk_addhlde); program ends at {2:X4}, {3} bytes free above" -f
    $first, $last, $tail, ($sp - $tail))
