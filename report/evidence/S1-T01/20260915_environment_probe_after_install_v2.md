timestamp_utc8=2026-09-15T16:31:27.0415834+08:00
working_directory=D:\FPGA_Competition
vcvars64=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
CUDA_PATH_V13_4=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4
PATH_prefix=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin\x64;C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.4\bin;D:\FPGA_Data\darknet\3rdparty\pthreads\bin
command=C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe D:\FPGA_Competition\verification\s1_t01_environment_probe.py --darknet-executable D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe --cuda-smoke-executable D:\FPGA_Competition\build\s1_t01\s1_t01_cuda_smoke.exe --identity-manifest D:\FPGA_Competition\report\evidence\S1-T01\20260914_sha256_manifest.txt --report D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v2.json
darknet_executable=D:\FPGA_Data\darknet\build\s1_t01_vc_cuda134_v2\Release\darknet.exe
cuda_smoke_executable=D:\FPGA_Competition\build\s1_t01\s1_t01_cuda_smoke.exe
identity_manifest=D:\FPGA_Competition\report\evidence\S1-T01\20260914_sha256_manifest.txt
report=D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v2.json
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v2.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_environment_probe_after_install_v2.stderr.log
exit_code=0
report_sha256=3e2b8233c3f17bae315748d056f938f3dab0c546b4bcf5331eab1392aaba41a8
status=PASS
checks:
{"python":"通过","numpy":"通过","nvidia_smi":"通过","nvcc":"通过","cmake":"通过","darknet":"通过：PE 校验与版本/帮助命令成功","cuda_device_smoke":"通过：固定设备运算返回成功标记"}
commands:
[{"command":["nvidia-smi","--query-gpu=name,memory.total,memory.free,driver_version","--format=csv,noheader,nounits"],"available":true,"exit_code":0,"stdout":"NVIDIA GeForce RTX 4060 Laptop GPU, 8188, 7828, 610.88","stderr":"","passed":true,"resolved_executable":"c:\\windows\\system32\\nvidia-smi.EXE"},{"command":["nvcc","--version"],"available":true,"exit_code":0,"stdout":"nvcc: NVIDIA (R) Cuda compiler driver\nCopyright (c) 2005-2026 NVIDIA Corporation\nBuilt on Sun_Aug_03_13:24:32_Pacific_Standard_Time_2026\nCuda compilation tools, release 13.4, V13.4.59\nBuild cuda_13.4.r13.4/compiler.38657139_0","stderr":"","passed":true,"resolved_executable":"C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v13.4\\bin\\nvcc.EXE"},{"command":["cmake","--version"],"available":true,"exit_code":0,"stdout":"cmake version 3.30.2\n\nCMake suite maintained and supported by Kitware (kitware.com/cmake).","stderr":"","passed":true,"resolved_executable":"C:\\Espressif\\tools\\cmake\\3.30.2\\bin\\cmake.EXE"},{"command":["D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe","--version"],"available":true,"exit_code":0,"stdout":"","stderr":"CUDA-version: 13030 (13030), GPU count: 1  \n OpenCV isn't used - data augmentation will be slow \nNot an option: --version","passed":true},{"command":["D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe"],"available":true,"exit_code":0,"stdout":"","stderr":"usage: D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe <function>","passed":true},{"command":["D:\\FPGA_Competition\\build\\s1_t01\\s1_t01_cuda_smoke.exe"],"available":true,"exit_code":0,"stdout":"S1_T01_CUDA_SMOKE_PASS device=0 name=NVIDIA GeForce RTX 4060 Laptop GPU","stderr":"","passed":true}]
stdout:
{
  "schema_version": 1,
  "created_at_utc8": "2026-09-15T16:31:26+08:00",
  "python": {
    "executable": "C:\\Users\\22061\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe",
    "version": "3.12.14",
    "implementation": "CPython"
  },
  "framework": "official-darknet-cuda",
  "cuda_required": true,
  "checks": {
    "python": "ͨ��",
    "numpy": "ͨ��",
    "nvidia_smi": "ͨ��",
    "nvcc": "ͨ��",
    "cmake": "ͨ��",
    "darknet": "ͨ����PE У����汾/��������ɹ�",
    "cuda_device_smoke": "ͨ�����̶��豸���㷵�سɹ����"
  },
  "commands": [
    {
      "command": [
        "nvidia-smi",
        "--query-gpu=name,memory.total,memory.free,driver_version",
        "--format=csv,noheader,nounits"
      ],
      "available": true,
      "exit_code": 0,
      "stdout": "NVIDIA GeForce RTX 4060 Laptop GPU, 8188, 7828, 610.88",
      "stderr": "",
      "passed": true,
      "resolved_executable": "c:\\windows\\system32\\nvidia-smi.EXE"
    },
    {
      "command": [
        "nvcc",
        "--version"
      ],
      "available": true,
      "exit_code": 0,
      "stdout": "nvcc: NVIDIA (R) Cuda compiler driver\nCopyright (c) 2005-2026 NVIDIA Corporation\nBuilt on Sun_Aug_03_13:24:32_Pacific_Standard_Time_2026\nCuda compilation tools, release 13.4, V13.4.59\nBuild cuda_13.4.r13.4/compiler.38657139_0",
      "stderr": "",
      "passed": true,
      "resolved_executable": "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v13.4\\bin\\nvcc.EXE"
    },
    {
      "command": [
        "cmake",
        "--version"
      ],
      "available": true,
      "exit_code": 0,
      "stdout": "cmake version 3.30.2\n\nCMake suite maintained and supported by Kitware (kitware.com/cmake).",
      "stderr": "",
      "passed": true,
      "resolved_executable": "C:\\Espressif\\tools\\cmake\\3.30.2\\bin\\cmake.EXE"
    },
    {
      "command": [
        "D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe",
        "--version"
      ],
      "available": true,
      "exit_code": 0,
      "stdout": "",
      "stderr": "CUDA-version: 13030 (13030), GPU count: 1  \n OpenCV isn't used - data augmentation will be slow \nNot an option: --version",
      "passed": true
    },
    {
      "command": [
        "D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe"
      ],
      "available": true,
      "exit_code": 0,
      "stdout": "",
      "stderr": "usage: D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe <function>",
      "passed": true
    },
    {
      "command": [
        "D:\\FPGA_Competition\\build\\s1_t01\\s1_t01_cuda_smoke.exe"
      ],
      "available": true,
      "exit_code": 0,
      "stdout": "S1_T01_CUDA_SMOKE_PASS device=0 name=NVIDIA GeForce RTX 4060 Laptop GPU",
      "stderr": "",
      "passed": true
    }
  ],
  "status": "PASS",
  "notes": [
    "��̽�벻��װ���������������ݡ����л������� YOLO ��ܡ�������ѵ����",
    "δ�ṩ Darknet ��̶� CUDA �豸�������ʱ����ܾ�����鱣��ʧ�ܡ�"
  ],
  "identity_manifest": "D:\\FPGA_Competition\\report\\evidence\\S1-T01\\20260914_sha256_manifest.txt",
  "identity_manifest_error": null,
  "darknet_executable": "D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe",
  "darknet_sha256": "358807f0f22f943fb521c0b8188e8b803abb0bc358965f273fa47d58bfadd48f",
  "darknet_version": "usage: D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe <function>",
  "darknet_version_command": [
    "D:\\FPGA_Data\\darknet\\build\\s1_t01_vc_cuda134_v2\\Release\\darknet.exe"
  ],
  "cuda_smoke_sha256": "4abc2065f7d798685043dd8066bc231f0098285e0ff1d82e66b2b360c4a8480c",
  "cuda_smoke_executable": "D:\\FPGA_Competition\\build\\s1_t01\\s1_t01_cuda_smoke.exe"
}

stderr:
