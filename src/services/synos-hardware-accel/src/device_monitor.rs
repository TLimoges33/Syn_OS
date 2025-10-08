use anyhow::Result;
use sysinfo::System;
use tracing::debug;

pub struct DeviceMonitor {
    system: System,
    devices: Vec<DeviceInfo>,
}

#[derive(Debug, Clone)]
struct DeviceInfo {
    name: String,
    device_type: DeviceType,
    status: DeviceStatus,
}

#[derive(Debug, Clone)]
enum DeviceType {
    Cpu,
    Gpu,
    Npu,
    Tpu,
    Other,
}

#[derive(Debug, Clone)]
enum DeviceStatus {
    Active,
    Idle,
    Error,
}

impl DeviceMonitor {
    pub fn new() -> Result<Self> {
        let mut system = System::new_all();
        system.refresh_all();

        Ok(Self {
            system,
            devices: Vec::new(),
        })
    }

    pub async fn update_devices(&mut self) -> Result<()> {
        self.system.refresh_all();

        // Simulate device discovery
        self.devices.clear();
        self.devices.push(DeviceInfo {
            name: "CPU".to_string(),
            device_type: DeviceType::Cpu,
            status: DeviceStatus::Active,
        });

        if self.devices.len() % 10 == 0 {
            debug!("Monitoring {} devices", self.devices.len());
        }

        Ok(())
    }

    pub fn get_device_count(&self) -> usize {
        self.devices.len()
    }

    #[allow(dead_code)]
    #[allow(dead_code)]
    pub fn get_active_devices(&self) -> Vec<String> {
        self.devices
            .iter()
            .filter(|d| matches!(d.status, DeviceStatus::Active))
            .map(|d| d.name.clone())
            .collect()
    }
}
