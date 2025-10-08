use anyhow::{Context, Result};
use clap::{Arg, Command};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{error, info};

mod gpu_manager;
mod npu_manager;
mod device_monitor;

use gpu_manager::GpuManager;
use npu_manager::NpuManager;
use device_monitor::DeviceMonitor;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct HardwareConfig {
    pub gpu_enabled: bool,
    pub npu_enabled: bool,
    pub tpu_enabled: bool,
    pub auto_device_selection: bool,
    pub power_management: bool,
}

impl Default for HardwareConfig {
    fn default() -> Self {
        Self {
            gpu_enabled: true,
            npu_enabled: true,
            tpu_enabled: false,
            auto_device_selection: true,
            power_management: true,
        }
    }
}

pub struct HardwareAccelerator {
    config: HardwareConfig,
    gpu_manager: Arc<RwLock<GpuManager>>,
    npu_manager: Arc<RwLock<NpuManager>>,
    device_monitor: Arc<RwLock<DeviceMonitor>>,
}

impl HardwareAccelerator {
    pub fn new(config: HardwareConfig) -> Result<Self> {
        info!("Initializing SynOS Hardware Acceleration Daemon...");

        let gpu_manager = Arc::new(RwLock::new(
            GpuManager::new(config.gpu_enabled)?
        ));

        let npu_manager = Arc::new(RwLock::new(
            NpuManager::new(config.npu_enabled)?
        ));

        let device_monitor = Arc::new(RwLock::new(
            DeviceMonitor::new()?
        ));

        Ok(Self {
            config,
            gpu_manager,
            npu_manager,
            device_monitor,
        })
    }

    pub async fn run(&self) -> Result<()> {
        info!("Starting hardware acceleration daemon...");

        // Spawn GPU management task
        let gpu_handle = {
            let manager = Arc::clone(&self.gpu_manager);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = manager.write().await.monitor_gpu().await {
                        error!("GPU monitoring error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
                }
            })
        };

        // Spawn NPU management task
        let npu_handle = {
            let manager = Arc::clone(&self.npu_manager);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = manager.write().await.monitor_npu().await {
                        error!("NPU monitoring error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
                }
            })
        };

        // Spawn device monitoring task
        let monitor_handle = {
            let monitor = Arc::clone(&self.device_monitor);
            tokio::spawn(async move {
                loop {
                    if let Err(e) = monitor.write().await.update_devices().await {
                        error!("Device monitoring error: {}", e);
                    }
                    tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
                }
            })
        };

        info!("Hardware acceleration daemon running");

        // Wait for shutdown signal
        tokio::signal::ctrl_c().await?;

        info!("Shutting down hardware acceleration daemon...");
        gpu_handle.abort();
        npu_handle.abort();
        monitor_handle.abort();

        Ok(())
    }

    pub async fn get_status(&self) -> Result<HardwareStatus> {
        let gpu = self.gpu_manager.read().await;
        let npu = self.npu_manager.read().await;
        let monitor = self.device_monitor.read().await;

        Ok(HardwareStatus {
            gpu_available: gpu.is_available(),
            npu_available: npu.is_available(),
            gpu_utilization: gpu.get_utilization(),
            npu_utilization: npu.get_utilization(),
            devices_count: monitor.get_device_count(),
        })
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HardwareStatus {
    pub gpu_available: bool,
    pub npu_available: bool,
    pub gpu_utilization: f32,
    pub npu_utilization: f32,
    pub devices_count: usize,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_target(false)
        .with_thread_ids(true)
        .with_level(true)
        .init();

    let matches = Command::new("synos-hardware-accel")
        .version("1.0.0")
        .author("SynOS Team")
        .about("SynOS Hardware Acceleration Management Daemon")
        .arg(
            Arg::new("config")
                .short('c')
                .long("config")
                .value_name("FILE")
                .help("Configuration file path")
        )
        .arg(
            Arg::new("gpu")
                .long("enable-gpu")
                .help("Enable GPU acceleration")
                .action(clap::ArgAction::SetTrue)
        )
        .arg(
            Arg::new("npu")
                .long("enable-npu")
                .help("Enable NPU acceleration")
                .action(clap::ArgAction::SetTrue)
        )
        .get_matches();

    let config = if let Some(config_path) = matches.get_one::<String>("config") {
        let content = std::fs::read_to_string(config_path)
            .context("Failed to read config file")?;
        serde_json::from_str(&content)
            .context("Failed to parse config file")?
    } else {
        HardwareConfig::default()
    };

    info!("SynOS Hardware Acceleration Daemon v1.0.0");
    info!("Configuration: {:?}", config);

    let accelerator = HardwareAccelerator::new(config)?;
    accelerator.run().await?;

    Ok(())
}
