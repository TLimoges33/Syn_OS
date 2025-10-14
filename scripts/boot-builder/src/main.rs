use std::fs;
use std::path::PathBuf;
use std::process::{Command, Stdio};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🔧 Building bootable SynOS image using bootimage...");
    println!();

    // Get project root
    let project_root = std::env::current_dir()?
        .parent()
        .and_then(|p| p.parent())
        .ok_or("Failed to find project root")?
        .to_path_buf();

    println!("Project root: {}", project_root.display());

    // Define paths
    let kernel_dir = project_root.join("src/kernel");
    let out_dir = project_root.join("build");

    // Ensure output directory exists
    fs::create_dir_all(&out_dir)?;

    // Use bootimage to create bootable disk image
    println!("Building bootable image with bootimage...");

    let bootimage_build = Command::new("cargo")
        .current_dir(&kernel_dir)
        .args(&["bootimage", "--release", "--target=x86_64-unknown-none"])
        .env("BOOTIMAGE_OUTPUT_DIR", &out_dir)
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .status()?;

    if !bootimage_build.success() {
        return Err("Bootimage build failed - trying manual approach...".into());
    }

    println!("✅ Bootable image created successfully");

    // Look for the generated image
    let possible_locations = vec![
        out_dir.join("bootimage-kernel.bin"),
        kernel_dir.join("target/x86_64-unknown-none/release/bootimage-kernel.bin"),
    ];

    for location in &possible_locations {
        if location.exists() {
            let size = fs::metadata(location)?.len();
            println!("  Image: {}", location.display());
            println!(
                "  Size: {} bytes ({:.2} MB)",
                size,
                size as f64 / 1024.0 / 1024.0
            );

            // Copy to standard location
            let final_image = out_dir.join("synos-bios.img");
            fs::copy(location, &final_image)?;
            println!("  Copied to: {}", final_image.display());

            println!();
            println!("🎉 Build complete!");
            println!();
            println!("To test:");
            println!(
                "  qemu-system-x86_64 -drive format=raw,file={} -m 4G",
                final_image.display()
            );

            return Ok(());
        }
    }

    Err("Could not find generated bootimage".into())
}
