param(
    [Parameter(Mandatory=$true)]
    [string]$WorkbookPath,

    [Parameter(Mandatory=$true)]
    [string]$OutputDir
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Escape-CsvValue {
    param([object]$Value)
    if ($null -eq $Value) { return '""' }
    $text = [string]$Value
    $text = $text.Replace('"', '""')
    return '"' + $text + '"'
}

function Export-RangeToCsv {
    param(
        [object]$Worksheet,
        [string]$RangeAddress,
        [string]$CsvPath
    )

    $range = $Worksheet.Range($RangeAddress)
    $lines = New-Object System.Collections.Generic.List[string]
    for ($r = 1; $r -le $range.Rows.Count; $r++) {
        $values = @()
        for ($c = 1; $c -le $range.Columns.Count; $c++) {
            $values += Escape-CsvValue $range.Cells.Item($r, $c).Text
        }
        $lines.Add(($values -join ","))
    }
    [System.IO.File]::WriteAllLines($CsvPath, $lines, [System.Text.UTF8Encoding]::new($true))
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
$wb = $null

try {
    $wb = $excel.Workbooks.Open($WorkbookPath)

    $inout = $wb.Worksheets.Item(4)
    $inoutLastRow = $inout.UsedRange.Rows.Count
    Export-RangeToCsv $inout "A20:L${inoutLastRow}" (Join-Path $OutputDir "battery_transactions.csv")
    Export-RangeToCsv $inout "N20:R${inoutLastRow}" (Join-Path $OutputDir "battery_stock.csv")

    $items = $wb.Worksheets.Item(7)
    $itemsLastRow = $items.UsedRange.Rows.Count
    Export-RangeToCsv $items "A1:C${itemsLastRow}" (Join-Path $OutputDir "battery_items.csv")

    $schedule = $wb.Worksheets.Item(8)
    $scheduleLastRow = $schedule.UsedRange.Rows.Count
    Export-RangeToCsv $schedule "A1:F${scheduleLastRow}" (Join-Path $OutputDir "battery_schedule.csv")

    $log = $wb.Worksheets.Item(3)
    $logLastRow = $log.UsedRange.Rows.Count
    Export-RangeToCsv $log "B3:D${logLastRow}" (Join-Path $OutputDir "battery_usage_log.csv")
}
finally {
    if ($wb -ne $null) {
        $wb.Close($false) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($wb) | Out-Null
    }
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
