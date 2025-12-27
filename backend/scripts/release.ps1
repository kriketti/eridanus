param(
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [switch]$PushTag,
    [switch]$Deploy,
    [string]$AllowedBranch = "main",
    [switch]$DryRun
)

$versionPattern = "^v\d+\.\d+\.\d+$"
if ($Version -notmatch $versionPattern) {
    Write-Error "Version must match vMAJOR.MINOR.PATCH (ex: v1.3.0)."
    exit 1
}

$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Warning "Working tree is dirty. Consider committing before tagging."
}

$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne $AllowedBranch) {
    Write-Error "Current branch '$currentBranch' does not match required '$AllowedBranch'."
    exit 1
}

$existingTag = git tag -l $Version
if ($existingTag) {
    Write-Error "Tag '$Version' already exists."
    exit 1
}

$gaeVersion = $Version -replace "\.", "-"

if ($DryRun) {
    Write-Output "Dry run: would tag '$Version' and deploy as '$gaeVersion'."
    if ($PushTag) {
        Write-Output "Dry run: would push tag '$Version' to origin."
    }
    if ($Deploy) {
        Write-Output "Dry run: would deploy to App Engine with version '$gaeVersion'."
    }
    exit 0
}

git tag -a $Version -m "Release $Version"

if ($PushTag) {
    git push origin $Version
}

if ($Deploy) {
    gcloud app deploy --version=$gaeVersion
}

