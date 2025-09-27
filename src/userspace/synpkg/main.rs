//! SynPkg - Native Rust Package Manager for SynOS
//! 
//! A consciousness-aware package manager that integrates with multiple repositories
//! including Kali, BlackArch, Parrot, and SynOS-specific packages.

use clap::{Arg, Command};
use std::process;

mod core;
mod repository;
mod dependency;
mod cache;
mod consciousness;
mod security;

use core::SynPkgManager;

#[tokio::main]
async fn main() {
    let matches = Command::new("synpkg")
        .about("SynOS Consciousness-Aware Package Manager")
        .version("1.0.0")
        .subcommand(
            Command::new("install")
                .about("Install a package")
                .arg(Arg::new("package")
                    .help("Package name to install")
                    .required(true)
                    .index(1))
                .arg(Arg::new("context")
                    .long("context")
                    .help("Installation context (operational, educational, research)")
                    .default_value("operational"))
                .arg(Arg::new("source")
                    .long("source")
                    .help("Preferred package source (kali, blackarch, parrot, synos)")
                    .value_name("SOURCE"))
        )
        .subcommand(
            Command::new("remove")
                .about("Remove a package")
                .arg(Arg::new("package")
                    .help("Package name to remove")
                    .required(true)
                    .index(1))
        )
        .subcommand(
            Command::new("search")
                .about("Search for packages")
                .arg(Arg::new("query")
                    .help("Search query")
                    .required(true)
                    .index(1))
                .arg(Arg::new("category")
                    .long("category")
                    .help("Package category filter")
                    .value_name("CATEGORY"))
        )
        .subcommand(
            Command::new("update")
                .about("Update package database")
        )
        .subcommand(
            Command::new("upgrade")
                .about("Upgrade all packages")
        )
        .subcommand(
            Command::new("info")
                .about("Show package information")
                .arg(Arg::new("package")
                    .help("Package name")
                    .required(true)
                    .index(1))
        )
        .subcommand(
            Command::new("list")
                .about("List installed packages")
                .arg(Arg::new("filter")
                    .long("filter")
                    .help("Filter by status (installed, available, upgradable)")
                    .value_name("FILTER"))
        )
        .subcommand(
            Command::new("consciousness")
                .about("Consciousness-related operations")
                .subcommand(
                    Command::new("recommend")
                        .about("Get package recommendations")
                        .arg(Arg::new("context")
                            .help("Context for recommendations")
                            .required(true)
                            .index(1))
                )
                .subcommand(
                    Command::new("optimize")
                        .about("Optimize installed packages")
                )
        )
        .get_matches();

    // Initialize package manager
    let mut manager = match SynPkgManager::new().await {
        Ok(mgr) => mgr,
        Err(e) => {
            eprintln!("Failed to initialize SynPkg: {}", e);
            process::exit(1);
        }
    };

    // Handle commands
    let result = match matches.subcommand() {
        Some(("install", sub_matches)) => {
            let package = sub_matches.get_one::<String>("package").unwrap();
            let context = sub_matches.get_one::<String>("context").unwrap();
            let source = sub_matches.get_one::<String>("source");
            
            manager.install_package(package, context, source).await
        },
        Some(("remove", sub_matches)) => {
            let package = sub_matches.get_one::<String>("package").unwrap();
            manager.remove_package(package).await
        },
        Some(("search", sub_matches)) => {
            let query = sub_matches.get_one::<String>("query").unwrap();
            let category = sub_matches.get_one::<String>("category");
            manager.search_packages(query, category).await
        },
        Some(("update", _)) => {
            manager.update_repositories().await
        },
        Some(("upgrade", _)) => {
            manager.upgrade_packages().await
        },
        Some(("info", sub_matches)) => {
            let package = sub_matches.get_one::<String>("package").unwrap();
            manager.show_package_info(package).await
        },
        Some(("list", sub_matches)) => {
            let filter = sub_matches.get_one::<String>("filter");
            manager.list_packages(filter).await
        },
        Some(("consciousness", sub_matches)) => {
            match sub_matches.subcommand() {
                Some(("recommend", sub_sub_matches)) => {
                    let context = sub_sub_matches.get_one::<String>("context").unwrap();
                    manager.get_consciousness_recommendations(context).await
                },
                Some(("optimize", _)) => {
                    manager.optimize_packages().await
                },
                _ => {
                    eprintln!("Unknown consciousness subcommand");
                    process::exit(1);
                }
            }
        },
        _ => {
            eprintln!("No command specified. Use --help for usage information.");
            process::exit(1);
        }
    };

    if let Err(e) = result {
        eprintln!("Operation failed: {}", e);
        process::exit(1);
    }
}
