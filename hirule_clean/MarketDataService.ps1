
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

        # Extract and format values

        $price = [decimal]$tickData.c[0]

        $open = [decimal]$tickData.o

        $change = [Math]::Round(($price - $open) / $open * 100, 2)

        $volume = [decimal]$tickData.v[1]

        $high = [decimal]$tickData.h[1]

        $low = [decimal]$tickData.l[1]

        # Create data structure

        $data = @{

            timestamp = Get-Date -Format 'o'

            symbol = "XXBTZUSD"

            data = @{

                price = $price

                openPrice = $open

                changePercent = $change

                volume = $volume

                high24h = $high

                low24h = $low

            }

        }

        # Save current state

        $data | ConvertTo-Json -Depth 10 | Set-Content "$($this.MessageBusPath)\market_data.json"

        

        # Append to history

        "$($data | ConvertTo-Json -Compress)" | Add-Content "$($this.MessageBusPath)\history\XXBTZUSD-$(Get-Date -Format 'yyyyMMdd').json"

    }

    [void] StartFeed([string]$symbol) {

        while ($true) {

            try {

                $tickData = $this.FetchTicker($symbol)

                $this.ProcessTick($tickData)

                

                # Display formatted update

                $data = Get-Content "$($this.MessageBusPath)\market_data.json" | ConvertFrom-Json

                Write-Host ("$(Get-Date -Format 'HH:mm:ss') - BTC/USD: {0:N2} | Change: {1:N2}%" -f 

                    $data.data.price, $data.data.changePercent) -ForegroundColor Green

                

                Start-Sleep -Milliseconds 500

            } catch {

                Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red

                Start-Sleep -Seconds 2

            }

        }

    }

}

# Create and test the service

$service = [MarketDataService]::new(".\messaging\market_data")

Write-Host "Starting BTC/USD price feed..." -ForegroundColor Cyan

$service.StartFeed("XXBTZUSD")

