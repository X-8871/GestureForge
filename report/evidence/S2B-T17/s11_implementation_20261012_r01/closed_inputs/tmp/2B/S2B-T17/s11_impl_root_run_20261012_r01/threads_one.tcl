# 实现子进程在初始化前固定单线程，避免跨窗口资源叠加。
set_param general.maxThreads 1
if {[get_param general.maxThreads] != 1} {error S11_IMPL_THREADS_MISMATCH}
puts S11_IMPL_NATIVE_THREADS_1
