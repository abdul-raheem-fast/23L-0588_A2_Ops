param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

if (-not (Get-Command kaggle -ErrorAction SilentlyContinue)) {
    throw "Install the Kaggle CLI and configure its local API token before running this script."
}
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
kaggle datasets download -d cashbowman/ai-generated-images-vs-real-images -p $OutputDirectory --unzip

