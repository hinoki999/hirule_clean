# Clean Python files
Get-ChildItem -Path "C:\Users\Alber\hirule_clean" -Filter "*.py" -Recurse | ForEach-Object {
    $file = $_
    Write-Host "Cleaning $($file.Name)..."
    
    # Read content
    $text = Get-Content $file.FullName -Raw
    
    # Remove userStyle tags and escaped quotes
    $text = $text -replace '<userStyle>.*?</userStyle>', ''
    $text = $text -replace '\\"', '"'
    
    # Save cleaned content
    Set-Content -Path $file.FullName -Value $text
}

Write-Host "Done cleaning files!"
