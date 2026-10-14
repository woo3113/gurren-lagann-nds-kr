$ErrorActionPreference = "Continue"
$emu = "D:\20_게임\_에뮬데이터\melonDS-1.1-windows-x86_64\melonDS.exe"
$rom = "D:\20_게임\_한글패치\그랜라간\out\Tengen Toppa Gurren Lagann (Korea).nds"
$outdir = "D:\20_게임\_한글패치\그랜라간\work"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Shot($name) {
  $b = [System.Windows.Forms.SystemInformation]::VirtualScreen
  $bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
  $bmp.Save("$outdir\$name", [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  Write-Output "shot $name"
}

Get-Process melonDS -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Process -FilePath $emu -ArgumentList @('-b','never',$rom)
Start-Sleep -Seconds 18
Shot "emu_01.png"
Start-Sleep -Seconds 14
Shot "emu_02.png"
Start-Sleep -Seconds 16
Shot "emu_03.png"
Write-Output "done"
