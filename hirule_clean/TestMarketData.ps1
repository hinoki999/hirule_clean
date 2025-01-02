class MarketDataDisplay {
    [void] DisplayPrice([decimal]$price, [decimal]$changePercent) {
        $timestamp = Get-Date -Format 'HH:mm:ss'
        $priceStr = "{0:N2}" -f $price
        $changeStr = "{0:N2}" -f $changePercent
        Write-Host "$timestamp - BTC/USD: $priceStr | Change: $changeStr%" -ForegroundColor Green
    }
}

class MarketDataService {
    [string]$BaseUrl = "https://api.kraken.com/0/public"
    [string]$MessageBusPath

    MarketDataService([string]$messageBusPath) {
        $this.MessageBusPath = $messageBusPath
        New-Item -ItemType Directory -Path $messageBusPath -Force | Out-Null
        New-Item -ItemType Directory -Path "$messageBusPath\history" -Force | Out-Null
    }

    [object] FetchTicker([string]$symbol) {
        $response = Invoke-RestMethod -Uri "$($this.BaseUrl)/Ticker?pair=$symbol" -Method Get
        return $response.result.$symbol
    }

    [void] ProcessTick([object]$tickData) {
        $price = [decimal]$tickData.c[0]
        $open = [decimal]$tickData.o
        $change = ($price - $open) / $open * 100

        $data = @{
            timestamp = Get-Date -Format 'o'
            symbol = "XXBTZUSD"
            price = $price
            changePercent = [Math]::Round($change, 2)
            volume = [decimal]$tickData.v[1]
            high24h = [decimal]$tickData.h[1]
            low24h = [decimal]$tickData.l[1]
        }

        # Save current state
        $data | ConvertTo-Json | Set-Content "$($this.MessageBusPath)\market_data.json"
        
        # Append to history
        "$($data | ConvertTo-Json -Compress)" | Add-Content "$($this.MessageBusPath)\history\XXBTZUSD-$(Get-Date -Format 'yyyyMMdd').json"

        # Display update
        $display = [MarketDataDisplay]::new()
        $display.DisplayPrice($price, $change)
    }

    [void] StartFeed([string]$symbol) {
        while ($true) {
            try {
                $tickData = $this.FetchTicker($symbol)
                $this.ProcessTick($tickData)
                Start-Sleep -Milliseconds 500
            } catch {
                Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
                Start-Sleep -Seconds 2
            }
        }
    }
}
