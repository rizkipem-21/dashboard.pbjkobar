# ==============================
# AUTO DOWNLOAD INAPROC (FIX)
# ==============================

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dataPath = Join-Path $baseDir "data"

# buat folder data jika belum ada
if (!(Test-Path $dataPath)) {
    New-Item -ItemType Directory -Path $dataPath | Out-Null
}

$token = "inprc7642391c38774272bf57ca25ac1d4544"

$headers = @{
    Authorization = "Bearer $token"
}

# daftar endpoint
$urls = @(
    "https://data.inaproc.id/api/legacy/rup/paket-penyedia-terumumkan?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/rup/paket-swakelola-terumumkan?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/rup/master-satker?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/rup/program-master?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/rup/struktur-anggaran-pd?kode_klpd=D228&tahun=2026"
)

foreach ($url in $urls) {

    try {

        Write-Host ""
        Write-Host "DOWNLOAD:" $url -ForegroundColor Yellow

        # ambil nama endpoint
        $endpoint = ($url -split 'legacy/')[1] -split '\?'
        $baseName = ($endpoint[0] -replace '/', '_')

        if ($url -match "tahun=([0-9]{4})") {
            $tahun = $matches[1]
        } else {
            $tahun = "unknown"
        }

        $filename = "Legacy_${baseName}_${tahun}.json"
        $output = Join-Path $dataPath $filename

        # request API
        $response = Invoke-RestMethod -Method GET -Uri $url -Headers $headers

        # paksa file tetap ada
        if ($null -eq $response) {
            "[]" | Out-File -Encoding utf8 $output
        }
        else {
            $response | ConvertTo-Json -Depth 20 | Out-File -Encoding utf8 $output
        }

        Write-Host "SUKSES -> $filename" -ForegroundColor Green

    }
    catch {

        Write-Host "ERROR -> tetap buat file kosong" -ForegroundColor Red

        "[]" | Out-File -Encoding utf8 $output
    }
}

Write-Host ""
Write-Host "SELESAI DOWNLOAD SEMUA" -ForegroundColor Cyan