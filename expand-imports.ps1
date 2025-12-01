$mainFile = "style.scss"
$sassDir = "_sass"
$lineNum = 0

Get-Content $mainFile | ForEach-Object {
    $line = $_
    if ($line -match '@import "([^"]+)"') {
        $importName = $matches[1]
        $importFile = "$sassDir/_$importName.scss"
        if (Test-Path $importFile) {
            Write-Host "# Expanding @import `"$importName`" from line $($lineNum + 1)"
            Get-Content $importFile | ForEach-Object {
                $lineNum++
                Write-Host ("{0,5} | {1}" -f $lineNum, $_)
            }
        } else {
            $lineNum++
            Write-Host ("{0,5} | {1}" -f $lineNum, $line)
        }
    } else {
        $lineNum++
        Write-Host ("{0,5} | {1}" -f $lineNum, $line)
    }
}
Write-Host "Total lines: $lineNum"
