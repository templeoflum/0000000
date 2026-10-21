$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("C:\Users\User\Documents\0000000\Archetypal Context Protocol\[MSC] Modern Spiritual and Cultural\[HJ] Hero's Journey\[HJ] Hero.docx")
$doc.Content.Text | Out-File -FilePath "C:\Users\User\Documents\0000000\Archetypal Context Protocol\HJ_Hero_sample.txt" -Encoding UTF8
$doc.Close()
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Host "Conversion complete!"
