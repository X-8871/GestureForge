"""保存首次证书链失败原件，使用系统 TLS 验证下载同一官方 PDF。"""
from pathlib import Path
import hashlib
import json
import subprocess
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')
folder = Path(__file__).parent
for source, target in [('receipt.json','receipt_attempt_r01.json'),('official_pdf_download.json','official_pdf_download_attempt_r01.json')]:
    incoming, saved = folder / source, folder / target
    assert incoming.is_file() and not saved.exists()
    with saved.open('xb') as output:
        output.write(incoming.read_bytes())
pdf = folder / 'IHI0022H_amba_axi_protocol_spec.pdf'
assert folder.is_dir() and not pdf.exists()
curl = Path(r'C:\Windows\System32\curl.exe')
assert curl.is_file()
command = [str(curl), '--fail', '--location', '--max-time', '30', '--output', str(pdf), 'https://developer.arm.com/-/media/Arm%20Developer%20Community/PDF/IHI0022H_amba_axi_protocol_spec.pdf']
start = time.monotonic()
result = subprocess.run(command, capture_output=True)
(folder / 'curl_download.stdout.log').write_bytes(result.stdout)
(folder / 'curl_download.stderr.log').write_bytes(result.stderr)
record = {'command': command, 'native_exit_code': result.returncode, 'elapsed_seconds': time.monotonic()-start, 'TLS_certificate_validation':'Windows Schannel default; no insecure override', 'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest() if pdf.is_file() else None, 'pdf_bytes':pdf.stat().st_size if pdf.is_file() else None}
(folder / 'curl_download_receipt.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False,indent=2))
sys.exit(result.returncode)
