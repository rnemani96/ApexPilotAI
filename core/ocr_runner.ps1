param(
    [Parameter(Mandatory=$true)]
    [string]$ImagePath
)

try {
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    [Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime] | Out-Null
    [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
    [Windows.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType=WindowsRuntime] | Out-Null
    [Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null

    $asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
        $_.Name -eq 'AsTask' -and $_.GetParameters().Length -eq 1 -and $_.GetGenericArguments().Length -eq 1
    } | Select-Object -First 1

    function Await($WinRtAsync, [Type]$ResultType) {
        $task = $asTaskGeneric.MakeGenericMethod($ResultType).Invoke($null, @($WinRtAsync))
        $task.Wait()
        return $task.Result
    }

    $fullPath = (Resolve-Path $ImagePath).Path
    $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($fullPath)) ([Windows.Storage.StorageFile])
    $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
    $decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
    $bitmap = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])

    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    if (-not $engine) {
        $lang = New-Object Windows.Globalization.Language("en-US")
        $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
    }

    $ocrResult = Await ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    Write-Output $ocrResult.Text
} catch {
    Write-Error $_
    exit 1
}
