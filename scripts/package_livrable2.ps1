Param(
    [string]$Output = "livrable2_package.zip"
)

$ErrorActionPreference = "Stop"

Write-Host "Preparing Livrable 2 package..."

$items = @(
    "spark/jobs/01_extract_bronze.py",
    "spark/jobs/02_transform_silver.py",
    "spark/jobs/03_transform_gold.py",
    "spark/jobs/04_benchmarks.py",
    "airflow/dags/pipeline_pyspark_jobs.py",
    "docker-compose.yml",
    "jupyter/notebooks/01_Extract_Bronze_SOURCES_DIRECTES.ipynb",
    "jupyter/notebooks/02_Transform_Silver_NETTOYAGE.ipynb",
    "jupyter/notebooks/03_Transform_Gold_STAR_SCHEMA.ipynb",
    "jupyter/notebooks/04_Performance_Benchmarks.ipynb",
    "docs/ARCHITECTURE_PYSPARK_ONLY.md",
    "docs/PLAN_FINALISATION_LIVRABLE2.md",
    "livrable2/livrable2.tex"
)

$existing = $items | Where-Object { Test-Path $_ }
if ($existing.Count -eq 0) {
    Write-Error "No items found to package. Check paths."
}

if (Test-Path $Output) { Remove-Item $Output -Force }

Compress-Archive -Path $existing -DestinationPath $Output -Force

Write-Host "Package created: $Output"
