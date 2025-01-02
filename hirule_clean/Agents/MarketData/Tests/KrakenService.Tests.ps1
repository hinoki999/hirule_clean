# Import Pester if not already installed
if (-not (Get-Module -ListAvailable -Name Pester)) {
    Install-Module -Name Pester -Force -SkipPublisherCheck
}

Describe "MarketDataService" {
    BeforeAll {
        # Import the service
        . "$PSScriptRoot\..\Services\KrakenService.ps1"
        $global:service = [MarketDataService]::new("kraken")
    }

    It "Should initialize with correct properties" {
        $service.Exchange | Should -Be "kraken"
        $service.BaseUrl | Should -Be "https://api.kraken.com/0/public"
        $service.ActiveJobs.Count | Should -Be 0
    }

    It "Should handle API errors gracefully" {
        # Mock Invoke-RestMethod to throw an error
        Mock Invoke-RestMethod {
            throw "API Error"
        }

        # Start data feed in background job
        $job = Start-Job -ScriptBlock {
            $service.StartRealTimeData("XXBTZUSD")
        }

        # Wait briefly and check job hasnt failed
        Start-Sleep -Seconds 2
        $job.State | Should -Not -Be "Failed"

        # Clean up
        Stop-Job $job
        Remove-Job $job
    }

    AfterAll {
        # Cleanup
        $service.StopRealTimeData()
    }
}
