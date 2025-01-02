class MarketDataAgent {
    [MarketDataService]$DataService
    [string]$MessageBusPath
    [System.Collections.ArrayList]$Subscribers

    MarketDataAgent([string]$exchange, [string]$messageBusPath) {
        $this.DataService = [MarketDataService]::new($exchange)
        $this.MessageBusPath = $messageBusPath
        $this.Subscribers = [System.Collections.ArrayList]::new()
    }

    [void] StartDataFeed([string]$symbol) {
        $job = Start-Job -ScriptBlock {
            param($baseUrl, $symbol, $messageBusPath)
            
            while ($true) {
                try {
                    $response = Invoke-RestMethod -Uri "$baseUrl/Ticker?pair=$symbol" -Method Get
                    $data = $response.result.$symbol
                    
                    $marketData = @{
                        Symbol = $symbol
                        Price = [decimal]$data.c[0]
                        Volume = [decimal]$data.v[1]
                        High = [decimal]$data.h[1]
                        Low = [decimal]$data.l[1]
                        Timestamp = Get-Date
                    }

                    # Publish to message bus
                    $messagePath = Join-Path $messageBusPath "market_data.json"
                    $marketData | ConvertTo-Json | Out-File $messagePath
                    
                    Start-Sleep -Milliseconds 500
                } catch {
                    Write-Error "$($_.Exception.Message)"
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
