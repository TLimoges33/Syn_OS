use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "synos-pkg")]
#[command(about = "SynOS High-Performance Package Manager")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Install a package
    Install {
        /// Package name
        package: String,
        /// Specific version
        #[arg(short, long)]
        version: Option<String>,
    },
    /// Remove a package
    Remove {
        /// Package name
        package: String,
    },
    /// Update all packages
    Update,
    /// Search for packages
    Search {
        /// Search term
        query: String,
    },
    /// Show package information
    Info {
        /// Package name
        package: String,
    },
    /// List installed packages
    List,
    /// Show system status
    Status,
}
