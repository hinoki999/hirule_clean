Write-Host "Setting up message bus directories..." -ForegroundColor Cyan

# Define all required paths
$paths = @{
    Base = ".\messaging\market_data"
    History = ".\messaging\market_data\history"
    Logs = ".\messaging\market_data\logs"
}

# Create each directory and verify
foreach ($dir in $paths.GetEnumerator()) {
    try {
        if (-not (Test-Path $dir.Value)) {
            New-Item -ItemType Directory -Path $dir.Value -Force | Out-Null
            Write-Host "✓ Created: $($dir.Value)" -ForegroundColor Green
        } else {
            Write-Host "✓ Verified: $($dir.Value)" -ForegroundColor Green
        }
    } catch {
        Write-Host "Error creating $($dir.Value): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nStarting message bus test..." -ForegroundColor Cyan

# Load required files
. ".\Agents\MarketData\Services\KrakenService.ps1"
. ".\Agents\MarketData\Integration\MarketDataAgent.ps1"

try {
    $agent = [MarketDataAgent]::new("kraken", $paths.Base)
    Write-Host "✓ Agent created" -ForegroundColor Green
    
    Write-Host "Starting data feed..." -ForegroundColor Yellow
    $agent.StartDataFeed("XXBTZUSD")
    
    Write-Host "Monitoring message bus for 15 seconds..." -ForegroundColor Yellow
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    
    while ($timer.ElapsedMilliseconds -lt 15000) {
        $dataPath = Join-Path $paths.Base "market_data.json"
        if (Test-Path $dataPath) {
            $marketData = Get-Content $dataPath | ConvertFrom-Json
            Write-Host "$(Get-Date -Format 'HH:mm:ss') - $($marketData.symbol): $($marketData.data.price) USD" -ForegroundColor Green
            
            # Verify history file is being written
            $todayHistoryFile = Join-Path $paths.History "$($marketData.symbol)-$(Get-Date -Format 'yyyyMMdd').json"
            if (Test-Path $todayHistoryFile) {
                $fileSize = (Get-Item $todayHistoryFile).Length
                if ($fileSize -gt 0) {
                    Write-Host "  → History updated ($([int]($fileSize/1024))KB)" -ForegroundColor DarkGray
                }
            }
        }
        Start-Sleep -Milliseconds 500
    }
    
    $agent.StopDataFeed()
    Write-Host "`n✓ Message bus test complete" -ForegroundColor Green
    
    Write-Host "`nVerifying history files..." -ForegroundColor Yellow
    Get-ChildItem $paths.History -Filter "*.json" | ForEach-Object {
        Write-Host "Found history file: $($_.Name) - Size: $([int]($_.Length/1024))KB" -ForegroundColor Green
    }

} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack: $($_.ScriptStackTrace)" -ForegroundColor DarkGray
}
