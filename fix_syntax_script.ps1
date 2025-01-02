Param(
    [string]$RootPath = ".\src"  # or wherever your .py files are
)

Write-Host "Scanning Python files under $RootPath for trailing backslashes and suspicious triple quotes..."

# Get all .py files recursively
$pyFiles = Get-ChildItem -Path $RootPath -Include *.py -Recurse

foreach ($file in $pyFiles) {
    $filePath = $file.FullName
    Write-Host "`nProcessing file: $filePath"

    # Read file content (as a single string)
    $content = Get-Content $filePath -Raw

    # --- PASS 1: Remove trailing backslashes at line-ends ---
    $lines = $content -split "`r?`n"
    $fixedLines = @()

    foreach ($line in $lines) {
        # Trim trailing whitespace
        $trimmed = $line.TrimEnd()

        # If line ends with a backslash, remove it
        if ($trimmed -match "\\$") {
            $trimmed = $trimmed -replace "\\$", ""
            Write-Host "  [Fix] Removed trailing backslash from: $line"
        }

        $fixedLines += $trimmed
    }

    # Join them back with newline
    $rejoined = $fixedLines -join "`r`n"

    # --- PASS 2: Attempt to handle suspicious triple quotes. ---
    # We'll do a naive regex to comment out triple quotes if they do NOT appear at start of line.
    # WARNING: This can break valid docstrings that appear inline.

    $pattern = '(?<!^[ \t]*)"""'  # Use single quotes to avoid parse error
    $rejoined = [Regex]::Replace($rejoined, $pattern, '#"""')

    # Write final content back to the file
    Set-Content -Path $filePath -Value $rejoined

    Write-Host "  [DONE] Wrote cleaned content to $filePath"
}

Write-Host "`nAll .py files processed. Please review changes & test your code!"
