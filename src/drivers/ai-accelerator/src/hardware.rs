//! Hardware abstraction layer

pub struct HardwareInterface;

impl HardwareInterface {
    pub fn detect_accelerators() -> Vec<String> {
        vec![]
    }
}
