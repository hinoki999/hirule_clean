# First, let's create a backup of all Python files
Get-ChildItem -Filter *.py -Recurse | ForEach-Object {
    Copy-Item $_.FullName "$($_.FullName).backup"
}

# Now fix the files
Get-ChildItem -Filter *.py -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    
    # Remove escaped quotes
    $content = $content -replace '\\"', '"'
    
    # Remove userStyle tags
    $content = $content -replace '<userStyle>Normal</userStyle>', ''
    $content = $content -replace '<userStyle>.*?</userStyle>', ''
    
    # Remove any trailing whitespace that might have been left
    $content = $content -replace '\s+$', ''
    
    # Write the cleaned content back to the file
    Set-Content -Path $_.FullName -Value $content
}

# Verify changes (will show files that still have potential issues)
Write-Host "`nChecking for any remaining issues..."
Get-ChildItem -Filter *.py -Recurse | Select-String -Pattern '\\"|<userStyle>'
