use clap::Parser;
use synos_package_manager::{PackageManager, PackageManagerConfig, cli::{Cli, Commands}};
use tracing_subscriber;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logging
    tracing_subscriber::fmt::init();
    
    let cli = Cli::parse();
    
    // Load configuration
    let config = PackageManagerConfig::default();
    let manager = PackageManager::new(config).await?;
    
    match cli.command {
        Commands::Install { package, version } => {
            println!("Installing package: {} (version: {:?})", package, version);
            match manager.install_package(&package, version.as_deref()).await {
                Ok(()) => println!("✅ Successfully installed {}", package),
                Err(e) => {
                    eprintln!("❌ Installation failed: {}", e);
                    std::process::exit(1);
                }
            }
        }
        Commands::Remove { package } => {
            println!("Removing package: {}", package);
            match manager.remove_package(&package).await {
                Ok(()) => println!("✅ Successfully removed {}", package),
                Err(e) => {
                    eprintln!("❌ Removal failed: {}", e);
                    std::process::exit(1);
                }
            }
        }
        Commands::Update => {
            println!("Updating all packages...");
            match manager.update_all().await {
                Ok(updated) => {
                    if updated.is_empty() {
                        println!("✅ All packages are up to date");
                    } else {
                        println!("✅ Updated {} packages: {}", updated.len(), updated.join(", "));
                    }
                }
                Err(e) => {
                    eprintln!("❌ Update failed: {}", e);
                    std::process::exit(1);
                }
            }
        }
        Commands::Search { query } => {
            println!("Searching for packages matching: {}", query);
            // TODO: Implement search
            println!("Search functionality not yet implemented");
        }
        Commands::Info { package } => {
            println!("Package information for: {}", package);
            // TODO: Implement info
            println!("Info functionality not yet implemented");
        }
        Commands::List => {
            println!("Installed packages:");
            // TODO: Implement list
            println!("List functionality not yet implemented");
        }
        Commands::Status => {
            println!("System status:");
            let metrics = manager.get_metrics().await;
            if metrics.is_empty() {
                println!("No performance metrics available");
            } else {
                println!("Recent operations:");
                for metric in metrics.iter().take(10) {
                    println!("  {} - {}ms ({} packages)", 
                           metric.operation, 
                           metric.duration_ms, 
                           metric.packages_processed);
                }
            }
        }
    }
    
    Ok(())
}
