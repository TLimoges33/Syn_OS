//! TensorFlow Lite C API FFI Bindings
//!
//! Foreign Function Interface to TensorFlow Lite C library

#![allow(non_camel_case_types)]
#![allow(dead_code)]

use core::ffi::c_void;

// Opaque types
#[repr(C)]
pub struct TfLiteModel {
    _private: [u8; 0],
}

#[repr(C)]
pub struct TfLiteInterpreter {
    _private: [u8; 0],
}

#[repr(C)]
pub struct TfLiteInterpreterOptions {
    _private: [u8; 0],
}

#[repr(C)]
pub struct TfLiteTensor {
    _private: [u8; 0],
}

#[repr(C)]
pub struct TfLiteDelegate {
    _private: [u8; 0],
}

// Status codes
#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TfLiteStatus {
    kTfLiteOk = 0,
    kTfLiteError = 1,
    kTfLiteDelegateError = 2,
    kTfLiteApplicationError = 3,
}

// Tensor types
#[repr(C)]
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TfLiteType {
    kTfLiteNoType = 0,
    kTfLiteFloat32 = 1,
    kTfLiteInt32 = 2,
    kTfLiteUInt8 = 3,
    kTfLiteInt64 = 4,
    kTfLiteString = 5,
    kTfLiteBool = 6,
    kTfLiteInt16 = 7,
    kTfLiteComplex64 = 8,
    kTfLiteInt8 = 9,
    kTfLiteFloat16 = 10,
    kTfLiteFloat64 = 11,
}

// FFI functions (extern "C" declarations)
extern "C" {
    // Model operations
    pub fn TfLiteModelCreateFromFile(model_path: *const u8) -> *mut TfLiteModel;
    pub fn TfLiteModelDelete(model: *mut TfLiteModel);

    // Interpreter options
    pub fn TfLiteInterpreterOptionsCreate() -> *mut TfLiteInterpreterOptions;
    pub fn TfLiteInterpreterOptionsDelete(options: *mut TfLiteInterpreterOptions);
    pub fn TfLiteInterpreterOptionsSetNumThreads(options: *mut TfLiteInterpreterOptions, num_threads: i32);

    // Interpreter operations
    pub fn TfLiteInterpreterCreate(
        model: *const TfLiteModel,
        options: *const TfLiteInterpreterOptions,
    ) -> *mut TfLiteInterpreter;
    pub fn TfLiteInterpreterDelete(interpreter: *mut TfLiteInterpreter);
    pub fn TfLiteInterpreterAllocateTensors(interpreter: *mut TfLiteInterpreter) -> TfLiteStatus;
    pub fn TfLiteInterpreterInvoke(interpreter: *mut TfLiteInterpreter) -> TfLiteStatus;

    // Tensor access
    pub fn TfLiteInterpreterGetInputTensorCount(interpreter: *const TfLiteInterpreter) -> i32;
    pub fn TfLiteInterpreterGetOutputTensorCount(interpreter: *const TfLiteInterpreter) -> i32;
    pub fn TfLiteInterpreterGetInputTensor(
        interpreter: *const TfLiteInterpreter,
        input_index: i32,
    ) -> *mut TfLiteTensor;
    pub fn TfLiteInterpreterGetOutputTensor(
        interpreter: *const TfLiteInterpreter,
        output_index: i32,
    ) -> *const TfLiteTensor;

    // Tensor operations
    pub fn TfLiteTensorType(tensor: *const TfLiteTensor) -> TfLiteType;
    pub fn TfLiteTensorNumDims(tensor: *const TfLiteTensor) -> i32;
    pub fn TfLiteTensorDim(tensor: *const TfLiteTensor, dim_index: i32) -> i32;
    pub fn TfLiteTensorByteSize(tensor: *const TfLiteTensor) -> usize;
    pub fn TfLiteTensorData(tensor: *const TfLiteTensor) -> *mut c_void;
    pub fn TfLiteTensorCopyFromBuffer(
        tensor: *mut TfLiteTensor,
        input_data: *const c_void,
        input_data_size: usize,
    ) -> TfLiteStatus;
    pub fn TfLiteTensorCopyToBuffer(
        tensor: *const TfLiteTensor,
        output_data: *mut c_void,
        output_data_size: usize,
    ) -> TfLiteStatus;

    // Delegate operations (GPU, NPU, etc.)
    pub fn TfLiteGpuDelegateV2Create(options: *const c_void) -> *mut TfLiteDelegate;
    pub fn TfLiteGpuDelegateV2Delete(delegate: *mut TfLiteDelegate);
    pub fn TfLiteInterpreterModifyGraphWithDelegate(
        interpreter: *mut TfLiteInterpreter,
        delegate: *mut TfLiteDelegate,
    ) -> TfLiteStatus;
}

// Safe wrappers for common operations
pub struct TfLiteModelWrapper {
    model: *mut TfLiteModel,
}

impl TfLiteModelWrapper {
    pub fn from_file(path: &str) -> Result<Self, &'static str> {
        use alloc::ffi::CString;

        let c_path = CString::new(path).map_err(|_| "Invalid path")?;
        let model = unsafe { TfLiteModelCreateFromFile(c_path.as_ptr() as *const u8) };

        if model.is_null() {
            return Err("Failed to load model");
        }

        Ok(Self { model })
    }

    pub fn as_ptr(&self) -> *mut TfLiteModel {
        self.model
    }
}

impl Drop for TfLiteModelWrapper {
    fn drop(&mut self) {
        if !self.model.is_null() {
            unsafe { TfLiteModelDelete(self.model) };
        }
    }
}

pub struct TfLiteInterpreterWrapper {
    interpreter: *mut TfLiteInterpreter,
}

impl TfLiteInterpreterWrapper {
    pub fn new(model: &TfLiteModelWrapper, num_threads: i32) -> Result<Self, &'static str> {
        let options = unsafe { TfLiteInterpreterOptionsCreate() };
        if options.is_null() {
            return Err("Failed to create interpreter options");
        }

        unsafe { TfLiteInterpreterOptionsSetNumThreads(options, num_threads) };

        let interpreter = unsafe {
            TfLiteInterpreterCreate(model.as_ptr() as *const TfLiteModel, options as *const TfLiteInterpreterOptions)
        };

        unsafe { TfLiteInterpreterOptionsDelete(options) };

        if interpreter.is_null() {
            return Err("Failed to create interpreter");
        }

        // Allocate tensors
        let status = unsafe { TfLiteInterpreterAllocateTensors(interpreter) };
        if status != TfLiteStatus::kTfLiteOk {
            unsafe { TfLiteInterpreterDelete(interpreter) };
            return Err("Failed to allocate tensors");
        }

        Ok(Self { interpreter })
    }

    pub fn as_ptr(&self) -> *mut TfLiteInterpreter {
        self.interpreter
    }

    pub fn invoke(&self) -> Result<(), &'static str> {
        let status = unsafe { TfLiteInterpreterInvoke(self.interpreter) };
        if status == TfLiteStatus::kTfLiteOk {
            Ok(())
        } else {
            Err("Inference failed")
        }
    }
}

impl Drop for TfLiteInterpreterWrapper {
    fn drop(&mut self) {
        if !self.interpreter.is_null() {
            unsafe { TfLiteInterpreterDelete(self.interpreter) };
        }
    }
}

// Stub implementations when TFLite library is not available
#[cfg(not(feature = "tflite-runtime"))]
mod stubs {
    use super::*;

    #[no_mangle]
    pub extern "C" fn TfLiteModelCreateFromFile(_: *const u8) -> *mut TfLiteModel {
        core::ptr::null_mut()
    }

    #[no_mangle]
    pub extern "C" fn TfLiteModelDelete(_: *mut TfLiteModel) {}

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterOptionsCreate() -> *mut TfLiteInterpreterOptions {
        core::ptr::null_mut()
    }

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterOptionsDelete(_: *mut TfLiteInterpreterOptions) {}

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterOptionsSetNumThreads(_: *mut TfLiteInterpreterOptions, _: i32) {}

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterCreate(
        _: *const TfLiteModel,
        _: *const TfLiteInterpreterOptions,
    ) -> *mut TfLiteInterpreter {
        core::ptr::null_mut()
    }

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterDelete(_: *mut TfLiteInterpreter) {}

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterAllocateTensors(_: *mut TfLiteInterpreter) -> TfLiteStatus {
        TfLiteStatus::kTfLiteError
    }

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterInvoke(_: *mut TfLiteInterpreter) -> TfLiteStatus {
        TfLiteStatus::kTfLiteError
    }

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterGetInputTensorCount(_: *const TfLiteInterpreter) -> i32 {
        0
    }

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterGetOutputTensorCount(_: *const TfLiteInterpreter) -> i32 {
        0
    }

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterGetInputTensor(
        _: *const TfLiteInterpreter,
        _: i32,
    ) -> *mut TfLiteTensor {
        core::ptr::null_mut()
    }

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterGetOutputTensor(
        _: *const TfLiteInterpreter,
        _: i32,
    ) -> *const TfLiteTensor {
        core::ptr::null()
    }

    #[no_mangle]
    pub extern "C" fn TfLiteTensorType(_: *const TfLiteTensor) -> TfLiteType {
        TfLiteType::kTfLiteNoType
    }

    #[no_mangle]
    pub extern "C" fn TfLiteTensorNumDims(_: *const TfLiteTensor) -> i32 {
        0
    }

    #[no_mangle]
    pub extern "C" fn TfLiteTensorDim(_: *const TfLiteTensor, _: i32) -> i32 {
        0
    }

    #[no_mangle]
    pub extern "C" fn TfLiteTensorByteSize(_: *const TfLiteTensor) -> usize {
        0
    }

    #[no_mangle]
    pub extern "C" fn TfLiteTensorData(_: *const TfLiteTensor) -> *mut c_void {
        core::ptr::null_mut()
    }

    #[no_mangle]
    pub extern "C" fn TfLiteTensorCopyFromBuffer(
        _: *mut TfLiteTensor,
        _: *const c_void,
        _: usize,
    ) -> TfLiteStatus {
        TfLiteStatus::kTfLiteError
    }

    #[no_mangle]
    pub extern "C" fn TfLiteTensorCopyToBuffer(
        _: *const TfLiteTensor,
        _: *mut c_void,
        _: usize,
    ) -> TfLiteStatus {
        TfLiteStatus::kTfLiteError
    }

    #[no_mangle]
    pub extern "C" fn TfLiteGpuDelegateV2Create(_: *const c_void) -> *mut TfLiteDelegate {
        core::ptr::null_mut()
    }

    #[no_mangle]
    pub extern "C" fn TfLiteGpuDelegateV2Delete(_: *mut TfLiteDelegate) {}

    #[no_mangle]
    pub extern "C" fn TfLiteInterpreterModifyGraphWithDelegate(
        _: *mut TfLiteInterpreter,
        _: *mut TfLiteDelegate,
    ) -> TfLiteStatus {
        TfLiteStatus::kTfLiteError
    }
}
