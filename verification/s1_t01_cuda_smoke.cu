#include <cuda_runtime.h>

#include <cstdio>

__global__ void s1_t01_smoke_kernel(const int* input, int* output) {
    const int index = static_cast<int>(threadIdx.x);
    output[index] = input[index] + 7;
}

static int fail_with_cuda_error(const char* stage, cudaError_t error) {
    std::fprintf(stderr, "S1_T01_CUDA_SMOKE_FAIL stage=%s error=%s\n", stage, cudaGetErrorString(error));
    return 2;
}

int main() {
    int device_count = 0;
    cudaError_t error = cudaGetDeviceCount(&device_count);
    if (error != cudaSuccess) {
        return fail_with_cuda_error("device_count", error);
    }
    if (device_count < 1) {
        std::fprintf(stderr, "S1_T01_CUDA_SMOKE_FAIL stage=device_count error=no_cuda_device\n");
        return 2;
    }

    error = cudaSetDevice(0);
    if (error != cudaSuccess) {
        return fail_with_cuda_error("set_device", error);
    }

    cudaDeviceProp properties{};
    error = cudaGetDeviceProperties(&properties, 0);
    if (error != cudaSuccess) {
        return fail_with_cuda_error("device_properties", error);
    }

    const int host_input[4] = {1, 2, 3, 4};
    int host_output[4] = {0, 0, 0, 0};
    int* device_input = nullptr;
    int* device_output = nullptr;

    error = cudaMalloc(reinterpret_cast<void**>(&device_input), sizeof(host_input));
    if (error != cudaSuccess) {
        return fail_with_cuda_error("malloc_input", error);
    }
    error = cudaMalloc(reinterpret_cast<void**>(&device_output), sizeof(host_output));
    if (error != cudaSuccess) {
        cudaFree(device_input);
        return fail_with_cuda_error("malloc_output", error);
    }

    error = cudaMemcpy(device_input, host_input, sizeof(host_input), cudaMemcpyHostToDevice);
    if (error != cudaSuccess) {
        cudaFree(device_output);
        cudaFree(device_input);
        return fail_with_cuda_error("copy_to_device", error);
    }

    s1_t01_smoke_kernel<<<1, 4>>>(device_input, device_output);
    error = cudaGetLastError();
    if (error != cudaSuccess) {
        cudaFree(device_output);
        cudaFree(device_input);
        return fail_with_cuda_error("kernel_launch", error);
    }
    error = cudaDeviceSynchronize();
    if (error != cudaSuccess) {
        cudaFree(device_output);
        cudaFree(device_input);
        return fail_with_cuda_error("device_synchronize", error);
    }

    error = cudaMemcpy(host_output, device_output, sizeof(host_output), cudaMemcpyDeviceToHost);
    cudaFree(device_output);
    cudaFree(device_input);
    if (error != cudaSuccess) {
        return fail_with_cuda_error("copy_to_host", error);
    }

    for (int index = 0; index < 4; ++index) {
        if (host_output[index] != host_input[index] + 7) {
            std::fprintf(stderr, "S1_T01_CUDA_SMOKE_FAIL stage=verify error=unexpected_result index=%d\n", index);
            return 2;
        }
    }

    std::printf("S1_T01_CUDA_SMOKE_PASS device=0 name=%s\n", properties.name);
    return 0;
}
