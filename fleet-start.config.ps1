# Per-repo fleet start config for mastodon-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'mastodon-mcp'
    BackendPort  = 10754
    FrontendPort = 10755
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'mastodon_mcp.server:app'
        SyncExtras    = @('dev')
        SyncOnStart  = $true
        Env           = @{ WEB_PORT = '10754' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
