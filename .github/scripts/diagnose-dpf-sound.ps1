<#
.SYNOPSIS
Collect read-only Docker and Windows diagnostics after DPF-Sound startup fails.
.DESCRIPTION
Print bounded diagnostics to the CI log before cleanup. Container inspection excludes
environment variables, which can contain license configuration or other secrets.
Unavailable diagnostics are reported explicitly without masking the startup failure.
#>

$ErrorActionPreference = 'Continue'
$script:diagnosticsFailed = $false

function Write-DockerDiagnostic {
    <#
    .SYNOPSIS
    Run a Docker diagnostic and report a nonzero exit code.
    #>
    param(
        [string[]]$DockerArguments
    )

    Write-Output "::group::docker $($DockerArguments -join ' ')"
    & docker @DockerArguments
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Docker diagnostic failed with exit code $LASTEXITCODE."
        $script:diagnosticsFailed = $true
    }
    Write-Output "::endgroup::"
}

Write-Output "UTC: $([DateTime]::UtcNow.ToString('o'))"
Write-Output "Runner: $env:RUNNER_NAME; run: $env:GITHUB_RUN_ID; attempt: $env:GITHUB_RUN_ATTEMPT; job: $env:GITHUB_JOB"
Write-DockerDiagnostic -DockerArguments @('version')
Write-DockerDiagnostic -DockerArguments @('info')
Write-DockerDiagnostic -DockerArguments @(
    'ps', '-a', '--no-trunc', '--filter', "name=^/$env:DPF_SOUND_CONT_NAME$"
)
# Do not print full inspect output: Config.Env contains the license server.
Write-DockerDiagnostic -DockerArguments @(
    'inspect', '--format',
    'ID={{.Id}} Created={{.Created}} State={{json .State}} Image={{.Image}} Isolation={{.HostConfig.Isolation}}',
    $env:DPF_SOUND_CONT_NAME
)
Write-DockerDiagnostic -DockerArguments @(
    'image', 'inspect', '--format', 'ID={{.Id}} OS={{.Os}} OSVersion={{.OsVersion}}',
    $env:ANSRV_DPF_SOUND_IMAGE
)

Write-Output '::group::Windows host and resources'
try {
    Get-CimInstance Win32_OperatingSystem -ErrorAction Stop |
        Select-Object Caption, Version, BuildNumber, LastBootUpTime,
            TotalVisibleMemorySize, FreePhysicalMemory |
        Format-List
    Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' -ErrorAction Stop |
        Select-Object DeviceID, Size, FreeSpace |
        Format-Table -AutoSize
    Get-Service -ErrorAction Stop |
        Where-Object { $_.Name -in @('docker', 'com.docker.service', 'vmcompute', 'hns') } |
        Select-Object Name, Status |
        Format-Table -AutoSize
} catch {
    Write-Warning "Windows host diagnostics unavailable: $($_.Exception.Message)"
    $script:diagnosticsFailed = $true
}
Write-Output '::endgroup::'

# Read existing logs only; do not enable analytic logging or change host services.
$since = (Get-Date).AddHours(-1)
foreach ($logName in @(
    'Application',
    'Microsoft-Windows-Hyper-V-Compute-Admin',
    'Microsoft-Windows-Hyper-V-Compute-Operational'
)) {
    Write-Output "::group::Recent events: $logName"
    $filter = @{ LogName = $logName; StartTime = $since }
    if ($logName -eq 'Application') {
        $filter.ProviderName = 'docker'
    }
    try {
        Get-WinEvent -FilterHashtable $filter -MaxEvents 30 -ErrorAction Stop |
            Select-Object TimeCreated, Id, LevelDisplayName, ProviderName, Message |
            Format-List
    } catch {
        Write-Warning "Event query returned no events or could not be read: $($_.Exception.Message)"
        $script:diagnosticsFailed = $true
    }
    Write-Output '::endgroup::'
}

if ($script:diagnosticsFailed) {
    exit 1
}
exit 0
