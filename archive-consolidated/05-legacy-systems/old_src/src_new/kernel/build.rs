// build.rs
// Build script for the Syn_OS kernel

fn main() {
    // Tell Cargo to rerun if any of these files change
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-changed=x86_64-syn_os.json");
    println!("cargo:rerun-if-changed=.cargo/config.toml");
    
    // Add custom flags for target-specific builds
    println!("cargo:rustc-link-arg=--no-relax");
    println!("cargo:rustc-link-arg=-nostartfiles");
}
