# Sync / Clone Ramabondanp Kernel Repositories
param (
    [string]$TargetDir = "$PSScriptRoot\..\sources",
    [int]$Depth = 1,
    [switch]$All
)

$kernelRepos = @(
    @{ Name = "android_kernel_common-5.10"; Branch = "android12-5.10-stg-damon"; Url = "https://github.com/ramabondanp/android_kernel_common-5.10.git"; Desc = "Rama982 GKI 5.10 (DAMON tuned)" },
    @{ Name = "android_kernel_alps-5.10"; Branch = "alps-mp-s0.mp1-ACK"; Url = "https://github.com/ramabondanp/android_kernel_alps-5.10.git"; Desc = "MediaTek ALPS 5.10 (MT6789 / Helio G99)" },
    @{ Name = "android_kernel_common-6.1"; Branch = "android14-6.1"; Url = "https://github.com/ramabondanp/android_kernel_common-6.1.git"; Desc = "Android Common Kernel 6.1" },
    @{ Name = "android_kernel_common-6.6"; Branch = "android15-6.6"; Url = "https://github.com/ramabondanp/android_kernel_common-6.6.git"; Desc = "Android Common Kernel 6.6" },
    @{ Name = "android_kernel_common-6.12"; Branch = "android16-6.12-2025-09"; Url = "https://github.com/ramabondanp/android_kernel_common-6.12.git"; Desc = "Android Common Kernel 6.12" },
    @{ Name = "kernel_xiaomi_mt6768"; Branch = "genom-release"; Url = "https://github.com/ramabondanp/kernel_xiaomi_mt6768.git"; Desc = "Xiaomi MT6768 (Redmi 9 / Poco M2 / Redmi Note 9)" },
    @{ Name = "kernel_xiaomi_rosemary"; Branch = "R"; Url = "https://github.com/ramabondanp/kernel_xiaomi_rosemary.git"; Desc = "Redmi Note 10S Helio G95" },
    @{ Name = "kernel_xiaomi_angelica"; Branch = "Q"; Url = "https://github.com/ramabondanp/kernel_xiaomi_angelica.git"; Desc = "Redmi 9C" },
    @{ Name = "kernel_xiaomi_beryllium"; Branch = "twelve-personal"; Url = "https://github.com/ramabondanp/kernel_xiaomi_beryllium.git"; Desc = "Poco F1" },
    @{ Name = "kernel_xiaomi_chopin"; Branch = "r"; Url = "https://github.com/ramabondanp/kernel_xiaomi_chopin.git"; Desc = "Xiaomi Chopin" },
    @{ Name = "android_kernel_oneplus_sm8150"; Branch = "master"; Url = "https://github.com/ramabondanp/android_kernel_oneplus_sm8150.git"; Desc = "OnePlus SM8150" },
    @{ Name = "android_kernel_xiaomi_sdm660"; Branch = "rp"; Url = "https://github.com/ramabondanp/android_kernel_xiaomi_sdm660.git"; Desc = "Xiaomi SDM660" }
)

if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
}

Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host " Rama982 / Ramabondanp Kernel Repositories Sync Tool" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

foreach ($repo in $kernelRepos) {
    $dest = Join-Path $TargetDir $repo.Name
    if (Test-Path $dest) {
        Write-Host "[EXISTS] $($repo.Name) -> Updating..." -ForegroundColor Yellow
        git -C $dest fetch --depth=$Depth origin $($repo.Branch)
    } else {
        Write-Host "[CLONING] $($repo.Name) ($($repo.Desc))..." -ForegroundColor Green
        git clone --depth $Depth -b $($repo.Branch) $($repo.Url) $dest
    }
}

Write-Host "Finished syncing kernel repos." -ForegroundColor Cyan
