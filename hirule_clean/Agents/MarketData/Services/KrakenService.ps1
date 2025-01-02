class MarketDataService {
    [string]$BaseUrl = "https://api.kraken.com/0/public"
    [string]$Exchange

    MarketDataService([string]$exchange) {
        $this.Exchange = $exchange
    }

    [void] StartRealTimeData([string]$symbol) {
        Write-Host "Starting real-time BTC/USD price feed..."
        Write-Host "─" * 60

        while ($true) {
            try {
                $response = Invoke-RestMethod -Uri "$($this.BaseUrl)/Ticker?pair=$symbol" -Method Get
                $data = $response.result.$symbol

                # Properly extract values from arrays
                $currentPrice = [decimal]$data.c[0]
                $prevPrice = [decimal]$data.o
                $dayHigh = [decimal]$data.h[1]
                $dayLow = [decimal]$data.l[1]
                $volume = [decimal]$data.v[1]

                # Calculate percentage change
                $change = ($currentPrice - $prevPrice) / $prevPrice * 100
                $changeSymbol = if ($change -gt 0) { "+" } elseif ($change -lt 0) { "" } else { " " }
                $changeStr = if ($change -eq 0) { "(0.00%)" } else { "($changeSymbol$($change.ToString("0.00"))%)" }

                # Format the display string
                $displayStr = "$(Get-Date -Format 'HH:mm:ss') | $changeStr | 24h: $($dayLow.ToString('N0'))-$($dayHigh.ToString('N0')) | Vol: $($volume.ToString('N0')) BTC"
                Write-Host $displayStr

                Start-Sleep -Milliseconds 500

            } catch {
                Write-Error "Error fetching market data: $($_.Exception.Message)"
                Start-Sleep -Seconds 2
            }
        }
    }
}
