class MarketDataCoordinator {
    [MarketDataAgent]$DataAgent
    [string]$ConfigPath
    [hashtable]$ActiveTrainingSessions

    MarketDataCoordinator([string]$configPath) {
        $this.ConfigPath = $configPath
        $this.ActiveTrainingSessions = @{}
        
        # Load config
        $config = Get-Content $configPath | ConvertFrom-Json
        $messageBusPath = $config.messageBusPath

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
