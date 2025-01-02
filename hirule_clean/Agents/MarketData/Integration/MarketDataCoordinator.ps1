class MarketDataCoordinator {
    [MarketDataAgent]$DataAgent
    [string]$ConfigPath
    [hashtable]$ActiveTrainingSessions

    MarketDataCoordinator([string]$configPath) {
        $this.ConfigPath = $configPath
        $this.ActiveTrainingSessions = @{}
        
        # Create message bus directory if it doesn't exist
        $messageBusPath = ".\messaging\market_data"
        New-Item -ItemType Directory -Path $messageBusPath -Force | Out-Null
        
        $this.DataAgent = [MarketDataAgent]::new("kraken", $messageBusPath)
    }

    [void] StartTrainingSession([string]$sessionId, [string[]]$symbols) {
        foreach ($symbol in $symbols) {
            $this.DataAgent.StartDataFeed($symbol)
        }
        $this.ActiveTrainingSessions[$sessionId] = $symbols
    }

    [void] StopTrainingSession([string]$sessionId) {
        if ($this.ActiveTrainingSessions.ContainsKey($sessionId)) {
            $this.DataAgent.StopDataFeed()
            $this.ActiveTrainingSessions.Remove($sessionId)
        }
    }
}
