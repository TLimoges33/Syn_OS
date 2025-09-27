use std::env;

fn main() {
    // Get the profile being used (debug or release)
    let profile = env::var("PROFILE").unwrap();
    println!("cargo:rerun-if-changed=build.rs");
    
    // Kernel-specific build configuration
    if profile == "release" {
        println!("cargo:rustc-cfg=release_build");
    }
}