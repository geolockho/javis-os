# Copy code kubeconfig-generator từ brain sang repo thật. Không xoá file bên repo (không dùng /MIR).
# Bỏ qua .git, .env, secrets, venv, cache.
$src = Join-Path $PSScriptRoot "kubeconfig-generator"
$dst = "D:\FSEL\other-services\kubeconfig-generator"
robocopy $src $dst /E /NFL /NDL /NJH /NP `
  /XD .git .venv venv __pycache__ .pytest_cache secrets `
  /XF .env *.pyc *.kubeconfig
# robocopy: mã 0-7 là thành công
if ($LASTEXITCODE -ge 8) { Write-Error "robocopy lỗi, mã $LASTEXITCODE"; exit $LASTEXITCODE }
exit 0
