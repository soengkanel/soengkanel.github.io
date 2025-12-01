$files = @('_sass/_variables.scss','_sass/_reset.scss','_sass/_highlights.scss','_sass/_svg-icons.scss','_sass/_responsive.scss')
foreach ($f in $files) {
    $c = Get-Content $f -Raw
    $o = ([regex]::Matches($c, '{')).Count
    $cl = ([regex]::Matches($c, '}')).Count
    Write-Host "$f : open=$o close=$cl diff=$($o - $cl)"
}
