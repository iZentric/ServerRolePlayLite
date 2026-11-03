# Hosted-only synthetic test. No real JARs, player folders or PC runner.
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
if ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) { throw 'Hosted Unix fixture only' }
$root=Join-Path ([IO.Path]::GetTempPath()) ('fc-rp-variants-' + [guid]::NewGuid().ToString('N'))
$instances=Join-Path $root 'PrismLauncher/instances'
$lite=Join-Path $instances 'FunCity RP Lite'
$test=Join-Path $instances 'FunCity RP Lite Embeddium TEST'
$base=Get-Content -LiteralPath agent/FUNCITY-RP-LITE-SELECTIE.json -Raw | ConvertFrom-Json
$plan=Get-Content -LiteralPath agent/FUNCITY-RP-VARIANTE-LOWSPEC.json -Raw | ConvertFrom-Json
$original=@($base.retained_in_future_target)
$oculus='oculus-mc1.16.5-1.4.7.jar'
$rubidium='rubidium-mc1.16.5-0.2.13.jar'
$rubidiumOptions='TextruesRubidiumOptions-1.0.8-mc1.16.5.jar'
$embeddium='embeddium-0.3.18+mc1.16.5.jar'
$embeddiumOptions='textrue_embeddium_options-0.1.1+mc1.16.5.jar'
$embNames=@($original | Where-Object { $_ -cne $rubidium -and $_ -cne $rubidiumOptions }) + @($embeddium,$embeddiumOptions)
function Make-Source([string]$Profile,[string[]]$Names) {
  $mods=Join-Path $Profile '.minecraft/mods'
  New-Item -ItemType Directory -Path $mods -Force | Out-Null
  foreach ($name in $Names) {
    $text=if ($name -ceq $embeddium -or $name -ceq $embeddiumOptions) { 'candidate:' + $name } else { 'same:' + $name }
    [IO.File]::WriteAllText((Join-Path $mods $name),$text)
  }
  [IO.File]::WriteAllText((Join-Path $Profile 'mmc-pack.json'),'{}')
  [IO.File]::WriteAllText((Join-Path $Profile 'instance.cfg'),("[General]`nname=" + (Split-Path -Leaf $Profile) + "`n"))
  New-Item -ItemType Directory -Path (Join-Path $Profile '.minecraft/saves/SECRET-WORLD'),(Join-Path $Profile '.minecraft/config') -Force | Out-Null
  [IO.File]::WriteAllText((Join-Path $Profile '.minecraft/saves/SECRET-WORLD/level.dat'),'PRIVATE_WORLD')
  [IO.File]::WriteAllText((Join-Path $Profile '.minecraft/config/secret.txt'),'PRIVATE_CONFIG')
  [IO.File]::WriteAllText((Join-Path $Profile '.minecraft/accounts.json'),'PRIVATE_ACCOUNT')
  [IO.File]::WriteAllText((Join-Path $Profile '.minecraft/options.txt'),'renderDistance:12')
}
try {
  Make-Source $lite $original
  Make-Source $test $embNames
  $srcHash=(Get-FileHash -LiteralPath (Join-Path $lite '.minecraft/mods/Pizzaland_v68.jar') -Algorithm SHA256).Hash
  $bad=$plan.variants[0]
  $output=& ./scripts/fc_rp_lowspec_variants.ps1 -Variant low_rubidium -Lite (Join-Path $root 'Wrong-Lite') -Synthetic
  if ($LASTEXITCODE -eq 0 -or ($output -match 'PROFILE_CREATED_FOR_TEST')) { throw 'Wrong source must fail closed' }
  foreach ($variant in $plan.variants) {
    $args=@{ Variant=$variant.id; Lite=$lite; Synthetic=$true }
    if ($variant.id -ceq 'embeddium_test') { $args.EmbeddiumTest=$test }
    $output=& ./scripts/fc_rp_lowspec_variants.ps1 @args
    if ($LASTEXITCODE -ne 0 -or -not ($output -match 'PROFILE_CREATED_FOR_TEST=true')) {
      throw ('Failed to stage ' + $variant.id + ': ' + ($output -join ' '))
    }
    $dest=Join-Path $instances $variant.prism_name
    $mods=Join-Path $dest '.minecraft/mods'
    $expected=switch ($variant.id) {
      low_rubidium { @($original) }
      no_oculus_test { @($original | Where-Object { $_ -cne $oculus }) }
      embeddium_test { @($embNames | Where-Object { $_ -cne $oculus }) }
    }
    $copied=@(Get-ChildItem -LiteralPath $mods -File)
    if ($copied.Count -ne $expected.Count -or $expected.Count -ne $variant.jar_count -or
        @(Compare-Object -ReferenceObject $expected -DifferenceObject @($copied.Name)).Count -gt 0) {
      throw ('Wrong inventory: ' + $variant.id)
    }
    $sourceMods=if ($variant.id -ceq 'embeddium_test') { Join-Path $test '.minecraft/mods' } else { Join-Path $lite '.minecraft/mods' }
    foreach ($name in $expected) {
      if ((Get-FileHash -LiteralPath (Join-Path $sourceMods $name) -Algorithm SHA256).Hash -cne
          (Get-FileHash -LiteralPath (Join-Path $mods $name) -Algorithm SHA256).Hash) { throw 'Modified JAR bytes' }
    }
    $preset=Get-Content -LiteralPath (Join-Path $dest '.minecraft/options.txt') -Raw
    if ($preset -notmatch 'renderDistance:5' -or $preset -notmatch 'graphicsMode:0' -or
        $preset -notmatch 'particles:1' -or $preset -match 'maxFps:' -or
        (Test-Path -LiteralPath (Join-Path $dest '.minecraft/saves')) -or
        (Test-Path -LiteralPath (Join-Path $dest '.minecraft/config')) -or
        (Test-Path -LiteralPath (Join-Path $dest '.minecraft/accounts.json')) -or
        $output -match 'PRIVATE|SECRET|fc-rp-variants') { throw 'Preset/privacy regression' }
    $repeat=& ./scripts/fc_rp_lowspec_variants.ps1 @args
    if ($LASTEXITCODE -eq 0 -or -not (Test-Path -LiteralPath $dest) -or $repeat -match 'PROFILE_CREATED_FOR_TEST=true') {
      throw 'Existing profile must not be overwritten'
    }
  }
  if ((Get-FileHash -LiteralPath (Join-Path $lite '.minecraft/mods/Pizzaland_v68.jar') -Algorithm SHA256).Hash -cne $srcHash -or
      @(Get-ChildItem -LiteralPath (Join-Path $lite '.minecraft/mods') -File).Count -ne 22 -or
      @(Get-ChildItem -LiteralPath (Join-Path $test '.minecraft/mods') -File).Count -ne 22) { throw 'Source changed' }
  Write-Output 'PASS: 3 distinct profile fixtures 22/21/21; shared RP bytes identical, no FPS cap, no private files, collision and wrong source fail closed'
} finally {
  if (Test-Path -LiteralPath $root) { Remove-Item -LiteralPath $root -Recurse -Force -ErrorAction SilentlyContinue }
}
