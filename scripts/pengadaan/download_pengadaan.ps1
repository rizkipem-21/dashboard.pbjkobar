# ==============================
# AUTO DOWNLOAD PENGADAAN INAPROC (RETRY VERSION)
# ==============================

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dataPath = Join-Path $baseDir "..\..\data"

# buat folder data jika belum ada
if (!(Test-Path $dataPath)) {
    New-Item -ItemType Directory -Path $dataPath | Out-Null
}

$token = "inprc7642391c38774272bf57ca25ac1d4544"

$headers = @{
    Authorization = "Bearer $token"
}

# ============================================
# DAFTAR ENDPOINT
# ============================================

$urls = @(
    "https://data.inaproc.id/api/legacy/rup/paket-penyedia-terumumkan?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/rup/paket-swakelola-terumumkan?kode_klpd=D228&tahun=2026",
	"https://data.inaproc.id/api/legacy/tender/non-tender-ekontrak-bapbast?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/non-tender-ekontrak-kontrak?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/non-tender-ekontrak-spmkspp?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/non-tender-ekontrak-sppbj?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/non-tender-pengumuman?kode_klpd=D228&tahun=2026",
	"https://data.inaproc.id/api/legacy/tender/non-tender-selesai?kode_klpd=D228&tahun=2026"
    "https://data.inaproc.id/api/legacy/tender/pengumuman?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/tender-ekontrak-bapbast?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/tender-ekontrak-kontrak?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/tender-ekontrak-spmkspp?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/tender-ekontrak-sppbj?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/tender-selesai?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/tender-selesai-nilai?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/pencatatan-non-tender?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/tender/pencatatan-swakelola?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/ekatalog-archive/paket-e-purchasing?kode_klpd=D228&tahun=2026",
    "https://data.inaproc.id/api/legacy/ekatalog/paket-e-purchasing?kode_klpd=D228&tahun=2026"
)

# ============================================
# FUNGSI DOWNLOAD DENGAN RETRY
# ============================================

function Download-WithRetry($url, $output) {

    $maxRetry = 5
    $success = $false

    for ($i = 1; $i -le $maxRetry; $i++) {

        try {
            Write-Host "  Percobaan ke-$i..."

            $response = Invoke-RestMethod -Method GET -Uri $url -Headers $headers

            if ($null -ne $response) {
                $response | ConvertTo-Json -Depth 20 | Out-File -Encoding utf8 $output
                Write-Host "  SUKSES" -ForegroundColor Green
                $success = $true
                break
            }
        }
        catch {
            Write-Host "  Gagal percobaan ke-$i" -ForegroundColor Red
            Start-Sleep -Seconds 2
        }
    }

    if (-not $success) {
        Write-Host "  GAGAL TOTAL -> buat file kosong" -ForegroundColor Red
        "[]" | Out-File -Encoding utf8 $output
    }
}

# ============================================
# LOOP DOWNLOAD
# ============================================

foreach ($url in $urls) {

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

    Download-WithRetry $url $output

    Write-Host "FILE -> $filename"
}

Write-Host ""
Write-Host "SELESAI DOWNLOAD SEMUA DATA PENGADAAN" -ForegroundColor Cyan