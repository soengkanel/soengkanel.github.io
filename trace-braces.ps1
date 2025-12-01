param([string]$file)
$lines = Get-Content $file
$depth = 0
foreach ($i in 0..($lines.Count-1)) {
    $line = $lines[$i]
    $o = ([regex]::Matches($line, '{')).Count
    $c = ([regex]::Matches($line, '}')).Count
    $depth += $o - $c
    $preview = $line.Substring(0, [Math]::Min(80, $line.Length))
    Write-Host ("{0,4} {1,3} | {2}" -f ($i+1), $depth, $preview)
}
Write-Host "Final depth: $depth"
