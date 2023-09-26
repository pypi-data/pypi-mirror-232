
#include <torch/extension.h>
#include <iostream>
#include <vector>
#include <stdexcept>
#include <string>
#include <unordered_map>
// #include <format>

// #include <c10/cuda/CUDAGuard.h>
// #include <c10/cuda/CUDAStream.h>
#include <c10/util/Exception.h>

#include <warpat/cuda.h>
#include <warpat/cuda_error.h>

#define PYBIND11_DETAILED_ERROR_MESSAGES  
#define TORCH_EXTENSION_NAME warp_attention_torch_cpp

#define CHECK_DTYPE(x, dt) CHECK_TRUE(x.dtype() == dt)//, XSTR(x) " should have dtype " XSTR(dtype) ", got " XSTR(x.dtype()) " instead")
#define CHECK_CUDA(x) CHECK_TRUE(x.is_cuda())//, XSTR(x) " is not a cuda tensor")
#define CHECK_CONTIGUOUS(x) CHECK_TRUE(x.is_contiguous())//, XSTR(x) " must be contiguous")
#define CHECK_NDIM(x, ndim) CHECK_TRUE(x.dim() == ndim)//, XSTR(x) "should have " XSTR(ndim) "dimensions, got " std::to_string(x.dim()) " instead")
#define CHECK_TRUE(...) TORCH_CHECK(__VA_ARGS__, "Expected " #__VA_ARGS__ " to be true, ")
#define CHECK_SHAPE(x, ...) TORCH_CHECK(x.sizes() == torch::IntArrayRef({__VA_ARGS__}), #x " must have shape (" #__VA_ARGS__ "), ")


// using namespace torch::indexing;

namespace warpat{
  
class WarpAttentionModule{
  private:
    // CUmodule kernelModule;
    std::unordered_map<int, CUmodule> kernelModules;
    std::unordered_map<int, CUcontext> contexts;
    torch::Tensor config;
    // std::string modulePath;
    py::dict modulePathMap;

    int get_head_dim_idx(int headDim){
      int headDimIdx;
      switch (headDim){
        case 32: headDimIdx=0; break;
        case 64: headDimIdx=1; break;
        case 128: headDimIdx=2; break;
        default: throw std::runtime_error("unsupported headDim.");
      }
      return headDimIdx;
    }

  public:
    WarpAttentionModule(
      // std::string &_modulePath, 
      torch::Tensor &_config,  //[numNumHeads, numGears, numVersions, 3]
      py::dict _modulePathMap // maps cc to path 
    )
      : config(_config)
      , modulePathMap(_modulePathMap)
    {
      CUDA_ERROR_CHECK(cuInit(0));
      // create(modulePath, config);
    }

    CUcontext make_context(CUdevice &device){
      CUcontext context;
      CUDA_ERROR_CHECK(cuDevicePrimaryCtxRetain(&context, device));
      return context;
    }

    CUmodule make_module(CUdevice &device){
      int ccMajor, ccMinor;
      CUDA_ERROR_CHECK(cuDeviceGetAttribute(&ccMajor, CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR, device));
      CUDA_ERROR_CHECK(cuDeviceGetAttribute(&ccMinor, CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR, device));
      // std::cout << "cc: " << ccMajor << ccMinor << std::endl;
      
      std::string cc = std::to_string(ccMajor) + "." + std::to_string(ccMinor); 
      // std::cout << "cc: " << cc << std::endl;
      CUmodule kernelModule;

      // std::cout << modulePathMap[cc.c_str()].cast<std::string>() << std::endl;

      if (modulePathMap.contains( cc.c_str() )){
        CUDA_ERROR_CHECK(cuModuleLoad(&kernelModule, modulePathMap[cc.c_str()].cast<std::string>().c_str() ));

      } else {
        throw std::runtime_error("no .cubin was found for compute capability " + cc);
      }
      return kernelModule;
      
    }

    void run(
      const torch::Tensor &query,                //[batchSize, qSeqLen, numHeads, headDim]
      const torch::Tensor &key,                  //[batchSize, kvSeqLen, numHeads, headDim]
      const torch::Tensor &value,                //[batchSize, kvSeqLen, numHeads, headDim]
      torch::Tensor &out,                        //[batchSize, qSeqLen, numHeads, headDim]
      float attnScale,
      int gear, int version,
      bool isCausal,
      size_t _stream
    ){
      TORCH_CHECK(query.dim() == 4, "`query` must be a 4 dimensional tensor");
      TORCH_CHECK(key.dim() == 4, "`key` must be a 4 dimensional tensor");
      TORCH_CHECK(value.dim() == 4, "`value` must be a 4 dimensional tensor");
      TORCH_CHECK(out.dim() == 4, "`out` must be a 4 dimensional tensor");
      
      int batchSize = query.size(0);
      int qSeqLen = query.size(1);
      int kvSeqLen = key.size(1);
      int numHeads = query.size(2);
      int headDim = query.size(3);

      int numVersions = config.size(3);
      int numGears = config.size(2);
      int headDimIdx = get_head_dim_idx(headDim);
      
      TORCH_CHECK(query.is_cuda(), "`query` is not a cuda tensor");
      auto _device = query.device();

      TORCH_CHECK(key.device() == _device, "all input tensors must be on the same device");
      TORCH_CHECK(value.device() == _device, "all input tensors must be on the same device");
      TORCH_CHECK(out.device() == _device, "all input tensors must be on the same device");
      
      TORCH_CHECK(query.stride(-1) == 1, "last stride of `query` must be 1");
      TORCH_CHECK(key.stride(-1) == 1, "last stride of `key` must be 1");
      TORCH_CHECK(value.stride(-1) == 1, "last stride of `value` must be 1");
      TORCH_CHECK(out.stride(-1) == 1, "last stride of `out` must be 1");

      TORCH_CHECK(query.dtype() == torch::kFloat16, "`query` must be a float16 tensor");
      TORCH_CHECK(key.dtype() == torch::kFloat16, "`key` must be a float16 tensor");
      TORCH_CHECK(value.dtype() == torch::kFloat16, "`value` must be a float16 tensor");
      TORCH_CHECK(out.dtype() == torch::kFloat16, "`out` must be a float16 tensor");

      TORCH_CHECK(gear >= 0 && gear < numGears, "gear out of range 0 ~ ", numGears - 1);
      TORCH_CHECK(version >=0 && version < numVersions, "version out of range 0 ~ ", numVersions - 1);

      CHECK_SHAPE(key, batchSize, kvSeqLen, numHeads, headDim);
      CHECK_SHAPE(value, batchSize, kvSeqLen, numHeads, headDim);
      CHECK_SHAPE(out, batchSize, qSeqLen, numHeads, headDim);

      unsigned int deviceIndex = _device.index();
      CUcontext prevContext;
      CUDA_ERROR_CHECK(cuCtxGetCurrent(&prevContext));

      CUdevice device;
      CUDA_ERROR_CHECK(cuDeviceGet(&device, deviceIndex ));

      if (contexts.count(deviceIndex) == 0 ){
        contexts[deviceIndex] = make_context(device);
      
      }
      CUDA_ERROR_CHECK(cuCtxSetCurrent(contexts[deviceIndex]));

      if (kernelModules.count(deviceIndex) == 0 ){
        kernelModules[deviceIndex] = make_module(device);
      }
      CUmodule currentModule = kernelModules[deviceIndex];

      int maxSmemPerBlock;
      CUDA_ERROR_CHECK(cuDeviceGetAttribute(&maxSmemPerBlock, CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK, device));

      unsigned int smemBytes = config.index({ headDimIdx, int(isCausal), gear, version, 0 }).item().to<int>();

      TORCH_CHECK(smemBytes <= maxSmemPerBlock, "requested shared memory is ", smemBytes, ", which exceeds device limit. Please select a different version.")

      unsigned int tpb = config.index({ headDimIdx, int(isCausal), gear, version, 1 }).item().to<int>();
      unsigned int tm = config.index({ headDimIdx, int(isCausal), gear, version, 2 }).item().to<int>();

      // std::string funcName = std::format("warp_attn_forward_{}_{}_{}", headDim, gear, version); // TODO:
      std::string funcName = "warp_attn_forward_" + std::to_string(headDim) + "_" + std::to_string(int(isCausal)) + "_" + std::to_string(gear) + "_" + std::to_string(version); // TODO:
      CUfunction func;

      CUDA_ERROR_CHECK(cuModuleGetFunction(&func, currentModule, funcName.c_str()));
      CUDA_ERROR_CHECK(cuFuncSetAttribute(func, CU_FUNC_ATTRIBUTE_MAX_DYNAMIC_SHARED_SIZE_BYTES, smemBytes));
      
      // std::cout << "funcName: " << funcName << std::endl;
      // std::cout << "smemBytes: " << smemBytes << std::endl;
      // std::cout << "tpb: " << tpb << std::endl;
      // std::cout << "tm: " << tm << std::endl;
      // std::cout << "gridSize: " << (qSeqLen + tm - 1) / tm << ", " << numHeads << ", " << batchSize << std::endl;

      void* ptrQuery = query.data_ptr();
      void* ptrKey = key.data_ptr();
      void* ptrValue = value.data_ptr();
      void* ptrOut = out.data_ptr();
      long long int strideQX = query.stride(0);
      long long int strideQY = query.stride(1);
      long long int strideQZ = query.stride(2);
      long long int strideKX = key.stride(0);
      long long int strideKY = key.stride(1);
      long long int strideKZ = key.stride(2);
      long long int strideVX = value.stride(0);
      long long int strideVY = value.stride(1);
      long long int strideVZ = value.stride(2);
      long long int strideOX = out.stride(0);
      long long int strideOY = out.stride(1);
      long long int strideOZ = out.stride(2);

      CUstream stream = (CUstream) _stream;

      void* args[21];
      args[0] = &ptrQuery;
      args[1] = &ptrKey;
      args[2] = &ptrValue;
      args[3] = &ptrOut;
      args[4] = &strideQX;
      args[5] = &strideQY;
      args[6] = &strideQZ;
      args[7] = &strideKX;
      args[8] = &strideKY;
      args[9] = &strideKZ;
      args[10] = &strideVX;
      args[11] = &strideVY;
      args[12] = &strideVZ;
      args[13] = &strideOX;
      args[14] = &strideOY;
      args[15] = &strideOZ;
      args[16] = &qSeqLen;
      args[17] = &kvSeqLen;
      args[18] = &numHeads;
      args[19] = &batchSize;
      args[20] = &attnScale;

      CUDA_ERROR_CHECK(cuLaunchKernel(
        func,
        (qSeqLen + tm - 1) / tm, 
        numHeads,
        batchSize, 
        tpb, 
        1,
        1,
        smemBytes, 
        stream, args, NULL
      ));

      cuStreamSynchronize(stream);
      CUDA_ERROR_CHECK(cuCtxSetCurrent(prevContext));
    }
};

WarpAttentionModule create_module(
  torch::Tensor &config, py::dict modulePathMap
){
  return WarpAttentionModule(config, modulePathMap);
}

}

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m) { 
  py::class_<warpat::WarpAttentionModule>(m, "WarpAttentionModule")
    .def("run", &warpat::WarpAttentionModule::run, "run warp attention");

  m.def("create_module", &warpat::create_module, "create warp attention module"); 
}