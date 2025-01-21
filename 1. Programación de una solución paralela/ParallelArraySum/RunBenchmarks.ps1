param (
    [int]$items
)

$threadsList = @(1, 2, 4, 8, 16, 32)
$exePath = "x64\Release\ParallelArraySum.exe"

Write-Output "Running benchmarks for $items items"
foreach ($threads in $threadsList) {
    $chunkSize = [math]::Ceiling($items / $threads)
    & $exePath --items $items --threads $threads --max_output_rows 0 --chunk_size $chunkSize
    Write-Output ""
}