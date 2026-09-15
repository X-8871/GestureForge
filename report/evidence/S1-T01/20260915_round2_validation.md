command=C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest verification.test_s1_t01_environment_probe -v
exit_code=0
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_round2_environment_probe_unittest.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_round2_environment_probe_unittest.stderr.log
stdout:

stderr:
test_darknet_usage_accepts_paths_but_rejects_other_basenames (verification.test_s1_t01_environment_probe.EnvironmentProbeTest.test_darknet_usage_accepts_paths_but_rejects_other_basenames)
Darknet �����е����·��������·���� Unix ·�����밴 basename ʶ�� ... ok
test_fake_cuda_success_marker_cannot_pass (verification.test_s1_t01_environment_probe.EnvironmentProbeTest.test_fake_cuda_success_marker_cannot_pass)
�� PE �ļ���ʹ���� CUDA �ɹ����Ҳ����ͨ���� ... ok
test_invalid_darknet_file_cannot_pass (verification.test_s1_t01_environment_probe.EnvironmentProbeTest.test_invalid_darknet_file_cannot_pass)
�� PE �ļ���ʹ����α��ɹ����Ҳ����ͨ���� ... ok
test_matching_digest_is_required_before_darknet_execution (verification.test_s1_t01_environment_probe.EnvironmentProbeTest.test_matching_digest_is_required_before_darknet_execution)
������ע��Ŀ���ժҪƥ�����������빦�������顣 ... ok
test_real_non_darknet_pe_cannot_pass (verification.test_s1_t01_environment_probe.EnvironmentProbeTest.test_real_non_darknet_pe_cannot_pass)
��Ч PE û���ύ��ժҪʱ��α�����ݲ��ܿ�����ַ���ͨ���� ... ok
test_unavailable_identity_manifest_cannot_pass (verification.test_s1_t01_environment_probe.EnvironmentProbeTest.test_unavailable_identity_manifest_cannot_pass)
�嵥����������ռλֵʱ�����ܱ����ͳ��κο������ݡ� ... ok
test_valid_pe_fake_cuda_output_is_rejected (verification.test_s1_t01_environment_probe.EnvironmentProbeTest.test_valid_pe_fake_cuda_output_is_rejected)
�ṹ��Ч�� PE ��ʹα�� CUDA �ɹ���ǣ�Ҳ������ͨ��ժҪ�󶨡� ... ok
test_valid_pe_fake_darknet_output_is_rejected (verification.test_s1_t01_environment_probe.EnvironmentProbeTest.test_valid_pe_fake_darknet_output_is_rejected)
�ṹ��Ч�� PE ��ʹα�� Darknet �����Ҳ������ͨ��ժҪ�󶨡� ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.068s

OK


command=C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m py_compile verification/s1_t01_environment_probe.py verification/test_s1_t01_environment_probe.py
exit_code=0
stdout_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_round2_py_compile.stdout.log
stderr_log=D:\FPGA_Competition\report\evidence\S1-T01\20260915_round2_py_compile.stderr.log
stdout:

stderr:


command=git diff --check
exit_code=0
