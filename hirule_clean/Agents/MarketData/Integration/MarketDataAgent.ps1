class MarketDataAgent {
    [MarketDataService]$DataService
    [string]$MessageBusPath
    [System.Collections.ArrayList]$Subscribers

    MarketDataAgent([string]$exchange, [string]$messageBusPath) {
        $this.DataService = [MarketDataService]::new($exchange)
        $this.MessageBusPath = $messageBusPath
        $this.Subscribers = [System.Collections.ArrayList]::new()
        
        # Ensure directories exist
        New-Item -ItemType Directory -Path $this.MessageBusPath -Force | Out-Null
        New-Item -ItemType Directory -Path (Join-Path $this.MessageBusPath "history") -Force | Out-Null
    }

    [void] StartDataFeed([string]$symbol) {
        $job = Start-Job -ScriptBlock {
            param($baseUrl, $symbol, $messageBusPath)
            
            # Function to format market data
            function Format-MarketData($rawData, $symbol) {
                $price = [decimal]$rawData.c[0]
                $open = [decimal]$rawData.o
                $changePercent = [Math]::Round(($price - $open) / $open * 100, 2)
                
                return @{
                    timestamp = Get-Date -Format 'o'
                    symbol = $symbol
                    data = @{
                        price = $price
                        volume = [decimal]$rawData.v[1]
                        high24h = [decimal]$rawData.h[1]
                        low24h = [decimal]$rawData.l[1]
                        openPrice = $open
                        changePercent = $changePercent
                    }
                }
            }
            
            while ($true) {
                try {
                    # Get market data
                    $response = Invoke-RestMethod -Uri "$baseUrl/Ticker?pair=$symbol" -Method Get
                    $rawData = $response.result.$symbol
                    
                    # Format data
                    $marketData = Format-MarketData $rawData $symbol
                    
                    # Write current data
                    $currentFile = Join-Path $messageBusPath "market_data.json"
                    $marketData | ConvertTo-Json -Depth 10 | Set-Content $currentFile
                    
                    # Write to history
                    $historyFile = Join-Path $messageBusPath "history\$symbol-$(Get-Date -Format 'yyyyMMdd').json"
                    "$($marketData | ConvertTo-Json -Compress)" | Add-Content $historyFile
                    
                    Start-Sleep -Milliseconds 500
                } catch {
                    $errorData = @{
                        timestamp = Get-Date -Format 'o'
                        error = $_.Exception.Message
                    }
                    $errorData | ConvertTo-Json | Add-Content (Join-Path $messageBusPath "error.log")
                    Start-Sleep -Seconds 2
                }
            }
        } -ArgumentList $this.DataService.BaseUrl, $symbol, $this.MessageBusPath

        $null = $this.Subscribers.Add($job)
    }

    [void] StopDataFeed() {
        foreach ($job in $this.Subscribers) {
            Stop-Job -Job $job
            Remove-Job -Job $job -Force
        }
        $this.Subscribers.Clear()
    }
}
