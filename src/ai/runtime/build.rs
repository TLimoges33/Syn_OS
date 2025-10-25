//! Build script for SynOS AI Runtime
//!
//! Links against real AI inference libraries:
//! - TensorFlow Lite C API (libtensorflowlite_c.so)
//! - ONNX Runtime (libonnxruntime.so)
//! - PyTorch LibTorch (libtorch.so)

use std::path::PathBuf;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");

    // Get library search paths
    let lib_dirs = vec![
        "/usr/lib",
        "/usr/local/lib",
        "/usr/lib/x86_64-linux-gnu",
        "/opt/tensorflow/lib",
        "/opt/onnxruntime/lib",
        "/opt/libtorch/lib",
    ];

    // Add library search paths
    for dir in &lib_dirs {
        println!("cargo:rustc-link-search=native={}", dir);
    }

    // ========================================================================
    // TensorFlow Lite C API Linking
    // ========================================================================
    #[cfg(feature = "tensorflow-lite")]
    {
        println!("cargo:rustc-link-lib=dylib=tensorflowlite_c");

        // Check if library is available
        if !check_library_available("libtensorflowlite_c.so", &lib_dirs) {
            println!("cargo:warning=TensorFlow Lite C library not found!");
            println!("cargo:warning=Install with: sudo apt install libtensorflowlite-dev");
            println!("cargo:warning=Or build from source: https://www.tensorflow.org/lite/guide/build_cmake");
            panic!("libtensorflowlite_c.so not found - cannot build without stubs");
        }

        // GPU delegate (optional)
        if check_library_available("libtensorflowlite_gpu_delegate.so", &lib_dirs) {
            println!("cargo:rustc-link-lib=dylib=tensorflowlite_gpu_delegate");
            println!("cargo:rustc-cfg=feature=\"tflite_gpu\"");
        }

        // XNNPACK delegate (optional, often built-in)
        println!("cargo:rustc-cfg=feature=\"tflite_xnnpack\"");
    }

    // ========================================================================
    // ONNX Runtime Linking
    // ========================================================================
    #[cfg(feature = "onnx-runtime")]
    {
        println!("cargo:rustc-link-lib=dylib=onnxruntime");

        if !check_library_available("libonnxruntime.so", &lib_dirs) {
            println!("cargo:warning=ONNX Runtime library not found!");
            println!("cargo:warning=Download from: https://github.com/microsoft/onnxruntime/releases");
            println!("cargo:warning=Or install with: pip install onnxruntime && sudo cp $(python -c 'import onnxruntime; print(onnxruntime.__path__[0])')/capi/libonnxruntime.so* /usr/local/lib/");
            panic!("libonnxruntime.so not found - cannot build without stubs");
        }
    }

    // ========================================================================
    // PyTorch LibTorch Linking
    // ========================================================================
    #[cfg(feature = "pytorch")]
    {
        // PyTorch requires multiple libraries
        let torch_libs = vec![
            "torch",
            "torch_cpu",
            "c10",
        ];

        for lib in &torch_libs {
            println!("cargo:rustc-link-lib=dylib={}", lib);
        }

        if !check_library_available("libtorch.so", &lib_dirs) {
            println!("cargo:warning=PyTorch LibTorch not found!");
            println!("cargo:warning=Download from: https://pytorch.org/get-started/locally/");
            println!("cargo:warning=Extract and copy lib/* to /usr/local/lib/");
            panic!("libtorch.so not found - cannot build without stubs");
        }

        // Set rpath for LibTorch
        println!("cargo:rustc-link-arg=-Wl,-rpath,/usr/local/lib");
        println!("cargo:rustc-link-arg=-Wl,-rpath,/opt/libtorch/lib");
    }

    // ========================================================================
    // Optional: Generate bindings with bindgen
    // ========================================================================
    #[cfg(feature = "generate-bindings")]
    {
        generate_tflite_bindings();
        generate_onnx_bindings();
        generate_pytorch_bindings();
    }
}

/// Check if a library is available in the system
#[allow(dead_code)]
fn check_library_available(lib_name: &str, search_paths: &[&str]) -> bool {
    for path in search_paths {
        let full_path = PathBuf::from(path).join(lib_name);
        if full_path.exists() {
            println!("cargo:warning=Found {} at {}", lib_name, full_path.display());
            return true;
        }

        // Also check with version suffixes (.so.1, .so.2, etc.)
        if let Ok(entries) = std::fs::read_dir(path) {
            for entry in entries.flatten() {
                if entry.file_name().to_string_lossy().starts_with(lib_name) {
                    println!("cargo:warning=Found {} at {}", lib_name, entry.path().display());
                    return true;
                }
            }
        }
    }
    false
}

/// Generate TensorFlow Lite bindings with bindgen (optional)
#[cfg(feature = "generate-bindings")]
fn generate_tflite_bindings() {
    let bindings = bindgen::Builder::default()
        .header("/usr/include/tensorflow/lite/c/c_api.h")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        .generate()
        .expect("Unable to generate TFLite bindings");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("tflite_bindings.rs"))
        .expect("Couldn't write TFLite bindings!");
}

/// Generate ONNX Runtime bindings with bindgen (optional)
#[cfg(feature = "generate-bindings")]
fn generate_onnx_bindings() {
    let bindings = bindgen::Builder::default()
        .header("/usr/include/onnxruntime/core/session/onnxruntime_c_api.h")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        .generate()
        .expect("Unable to generate ONNX bindings");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("onnx_bindings.rs"))
        .expect("Couldn't write ONNX bindings!");
}

/// Generate PyTorch bindings with bindgen (optional)
#[cfg(feature = "generate-bindings")]
fn generate_pytorch_bindings() {
    let bindings = bindgen::Builder::default()
        .header("/opt/libtorch/include/torch/script.h")
        .clang_arg("-x")
        .clang_arg("c++")
        .clang_arg("-std=c++14")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        .generate()
        .expect("Unable to generate PyTorch bindings");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("pytorch_bindings.rs"))
        .expect("Couldn't write PyTorch bindings!");
}
