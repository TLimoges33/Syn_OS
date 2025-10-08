//! Window Management System for SynOS
//!
//! Provides window creation, management, and AI-enhanced layout optimization
//! with educational features for understanding window systems.

use crate::framebuffer::Framebuffer;
use crate::primitives::GraphicsPrimitives;
use crate::{Color, GraphicsError, Point, Rect};
use alloc::collections::BTreeMap;
use alloc::string::String;
use alloc::vec::Vec;

/// Window manager with AI optimization
pub struct WindowManager {
    windows: BTreeMap<WindowId, Window>,
    focused_window: Option<WindowId>,
    next_window_id: WindowId,
    screen_resolution: (u32, u32),
    ai_layout_enabled: bool,
    consciousness_level: f32,
}

/// Unique identifier for windows
pub type WindowId = u32;

/// Window structure with AI enhancement
#[derive(Debug, Clone)]
pub struct Window {
    _id: WindowId, // Reserved for window identification
    title: String,
    bounds: Rect,
    visible: bool,
    focused: bool,
    minimized: bool,
    resizable: bool,
    decorations: WindowDecorations,
    z_order: i32,
    _ai_priority: f32, // AI-driven priority for layout optimization (future use)
}

/// Window decoration configuration
#[derive(Debug, Clone)]
pub struct WindowDecorations {
    title_bar: bool,
    close_button: bool,
    minimize_button: bool,
    maximize_button: bool,
    resize_border: bool,
    border_color: Color,
    title_bar_color: Color,
    title_text_color: Color,
}

impl Default for WindowDecorations {
    fn default() -> Self {
        Self {
            title_bar: true,
            close_button: true,
            minimize_button: true,
            maximize_button: true,
            resize_border: true,
            border_color: Color::CONSCIOUSNESS_BLUE,
            title_bar_color: Color::AI_GREEN,
            title_text_color: Color::WHITE,
        }
    }
}

/// Window creation parameters
#[derive(Debug, Clone)]
pub struct WindowCreateInfo {
    pub title: String,
    pub x: i32,
    pub y: i32,
    pub width: u32,
    pub height: u32,
    pub resizable: bool,
    pub decorations: Option<WindowDecorations>,
}

impl WindowManager {
    /// Create a new window manager
    pub fn new(screen_width: u32, screen_height: u32) -> Self {
        crate::log_info!(
            "🪟 Initializing SynOS Window Manager: {}x{}",
            screen_width,
            screen_height
        );

        Self {
            windows: BTreeMap::new(),
            focused_window: None,
            next_window_id: 1,
            screen_resolution: (screen_width, screen_height),
            ai_layout_enabled: true,
            consciousness_level: 0.5,
        }
    }

    /// Create a new window with AI-optimized placement
    pub fn create_window(
        &mut self,
        create_info: WindowCreateInfo,
    ) -> Result<WindowId, GraphicsError> {
        let window_id = self.next_window_id;
        self.next_window_id += 1;

        // AI-enhanced window placement
        let optimized_bounds = if self.ai_layout_enabled {
            self.optimize_window_placement(&create_info)?
        } else {
            Rect::new(
                create_info.x,
                create_info.y,
                create_info.width,
                create_info.height,
            )
        };

        let window = Window {
            _id: window_id,
            title: create_info.title.clone(),
            bounds: optimized_bounds,
            visible: true,
            focused: false,
            minimized: false,
            resizable: create_info.resizable,
            decorations: create_info.decorations.unwrap_or_default(),
            z_order: self.get_next_z_order(),
            _ai_priority: self.calculate_ai_priority(&create_info.title),
        };

        self.windows.insert(window_id, window);
        self.focus_window(window_id)?;

        crate::log_info!(
            "✅ Created window '{}' (ID: {})",
            create_info.title,
            window_id
        );
        Ok(window_id)
    }

    /// AI-optimized window placement algorithm
    fn optimize_window_placement(
        &self,
        create_info: &WindowCreateInfo,
    ) -> Result<Rect, GraphicsError> {
        let (screen_width, screen_height) = self.screen_resolution;

        // Start with requested position
        let mut optimal_x = create_info.x;
        let mut optimal_y = create_info.y;

        // AI-driven placement optimization based on consciousness level
        if self.consciousness_level > 0.3 {
            // High consciousness: Avoid overlapping windows
            for _ in 0..10 {
                // Try up to 10 positions
                let test_rect =
                    Rect::new(optimal_x, optimal_y, create_info.width, create_info.height);

                if !self.has_overlapping_windows(&test_rect) {
                    break;
                }

                // Try cascade placement
                optimal_x += 30;
                optimal_y += 30;

                // Wrap around if we go off screen
                if optimal_x + create_info.width as i32 > screen_width as i32 {
                    optimal_x = 50;
                }
                if optimal_y + create_info.height as i32 > screen_height as i32 {
                    optimal_y = 50;
                }
            }
        }

        // Ensure window stays within screen bounds
        optimal_x = optimal_x
            .max(0)
            .min(screen_width as i32 - create_info.width as i32);
        optimal_y = optimal_y
            .max(0)
            .min(screen_height as i32 - create_info.height as i32);

        Ok(Rect::new(
            optimal_x,
            optimal_y,
            create_info.width,
            create_info.height,
        ))
    }

    /// Check if a rectangle overlaps with any existing windows
    fn has_overlapping_windows(&self, rect: &Rect) -> bool {
        self.windows
            .values()
            .any(|window| window.visible && !window.minimized && window.bounds.intersects(rect))
    }

    /// Calculate AI priority for a window based on its title and purpose
    fn calculate_ai_priority(&self, title: &str) -> f32 {
        match title.to_lowercase().as_str() {
            t if t.contains("education") || t.contains("tutorial") => 0.9,
            t if t.contains("security") || t.contains("threat") => 0.8,
            t if t.contains("consciousness") || t.contains("ai") => 0.7,
            t if t.contains("terminal") || t.contains("shell") => 0.6,
            _ => 0.5,
        }
    }

    /// Get the next Z-order value for window stacking
    fn get_next_z_order(&self) -> i32 {
        self.windows.values().map(|w| w.z_order).max().unwrap_or(0) + 1
    }

    /// Focus a specific window
    pub fn focus_window(&mut self, window_id: WindowId) -> Result<(), GraphicsError> {
        // Unfocus current window
        if let Some(current_id) = self.focused_window {
            if let Some(current_window) = self.windows.get_mut(&current_id) {
                current_window.focused = false;
            }
        }

        // Focus new window
        let next_z_order = self.get_next_z_order();
        if let Some(window) = self.windows.get_mut(&window_id) {
            window.focused = true;
            window.z_order = next_z_order;
            self.focused_window = Some(window_id);

            crate::log_info!("🎯 Focused window: {}", window.title);
            Ok(())
        } else {
            Err(GraphicsError::InvalidParameters)
        }
    }

    /// Close a window
    pub fn close_window(&mut self, window_id: WindowId) -> Result<(), GraphicsError> {
        if let Some(_window) = self.windows.remove(&window_id) {
            if self.focused_window == Some(window_id) {
                self.focused_window = None;

                // Focus the next highest Z-order window
                if let Some(next_window_id) = self.get_highest_z_order_window() {
                    self.focus_window(next_window_id)?;
                }
            }

            // Window closed successfully
            Ok(())
        } else {
            Err(GraphicsError::InvalidParameters)
        }
    }

    /// Get the window with the highest Z-order
    fn get_highest_z_order_window(&self) -> Option<WindowId> {
        self.windows
            .iter()
            .filter(|(_, w)| w.visible && !w.minimized)
            .max_by_key(|(_, w)| w.z_order)
            .map(|(id, _)| *id)
    }

    /// Minimize a window
    pub fn minimize_window(&mut self, window_id: WindowId) -> Result<(), GraphicsError> {
        if let Some(window) = self.windows.get_mut(&window_id) {
            window.minimized = true;
            window.visible = false;

            if self.focused_window == Some(window_id) {
                self.focused_window = None;

                // Focus the next available window
                if let Some(next_window_id) = self.get_highest_z_order_window() {
                    self.focus_window(next_window_id)?;
                }
            }

            crate::log_info!("📦 Minimized window: {}", window.title);
            Ok(())
        } else {
            Err(GraphicsError::InvalidParameters)
        }
    }

    /// Restore a minimized window
    pub fn restore_window(&mut self, window_id: WindowId) -> Result<(), GraphicsError> {
        if let Some(window) = self.windows.get_mut(&window_id) {
            window.minimized = false;
            window.visible = true;
            self.focus_window(window_id)?;

            crate::log_info!("📤 Restored window: {}", window.title);
            Ok(())
        } else {
            Err(GraphicsError::InvalidParameters)
        }
    }

    /// Move a window to a new position
    pub fn move_window(
        &mut self,
        window_id: WindowId,
        new_x: i32,
        new_y: i32,
    ) -> Result<(), GraphicsError> {
        if let Some(window) = self.windows.get_mut(&window_id) {
            let (screen_width, screen_height) = self.screen_resolution;

            // Ensure window stays within screen bounds
            let clamped_x = new_x
                .max(0)
                .min(screen_width as i32 - window.bounds.width as i32);
            let clamped_y = new_y
                .max(0)
                .min(screen_height as i32 - window.bounds.height as i32);

            window.bounds.x = clamped_x;
            window.bounds.y = clamped_y;

            Ok(())
        } else {
            Err(GraphicsError::InvalidParameters)
        }
    }

    /// Resize a window
    pub fn resize_window(
        &mut self,
        window_id: WindowId,
        new_width: u32,
        new_height: u32,
    ) -> Result<(), GraphicsError> {
        if let Some(window) = self.windows.get_mut(&window_id) {
            if !window.resizable {
                return Err(GraphicsError::InvalidParameters);
            }

            let (screen_width, screen_height) = self.screen_resolution;

            // Ensure window doesn't exceed screen size
            let max_width = (screen_width as i32 - window.bounds.x) as u32;
            let max_height = (screen_height as i32 - window.bounds.y) as u32;

            window.bounds.width = new_width.min(max_width).max(100); // Minimum 100px
            window.bounds.height = new_height.min(max_height).max(80); // Minimum 80px

            Ok(())
        } else {
            Err(GraphicsError::InvalidParameters)
        }
    }

    /// Render all windows to the framebuffer
    pub fn render(&self, framebuffer: &mut Framebuffer) -> Result<(), GraphicsError> {
        // Sort windows by Z-order (lowest first)
        let mut sorted_windows: Vec<&Window> = self.windows.values().collect();
        sorted_windows.sort_by_key(|w| w.z_order);

        // Render each visible window
        for window in sorted_windows {
            if window.visible && !window.minimized {
                self.render_window(framebuffer, window)?;
            }
        }

        Ok(())
    }

    /// Render a single window
    fn render_window(
        &self,
        framebuffer: &mut Framebuffer,
        window: &Window,
    ) -> Result<(), GraphicsError> {
        // Draw window background
        self.draw_window_background(framebuffer, window)?;

        // Draw window decorations if enabled
        if window.decorations.title_bar {
            self.draw_title_bar(framebuffer, window)?;
        }

        if window.decorations.resize_border {
            self.draw_window_border(framebuffer, window)?;
        }

        Ok(())
    }

    /// Draw window background
    fn draw_window_background(
        &self,
        framebuffer: &mut Framebuffer,
        window: &Window,
    ) -> Result<(), GraphicsError> {
        let background_color = if window.focused {
            Color::WHITE
        } else {
            Color::new(240, 240, 240, 255)
        };

        GraphicsPrimitives::fill_rect(framebuffer, window.bounds, background_color)
    }

    /// Draw window title bar
    fn draw_title_bar(
        &self,
        framebuffer: &mut Framebuffer,
        window: &Window,
    ) -> Result<(), GraphicsError> {
        let title_bar_height = 30;
        let title_bar_rect = Rect::new(
            window.bounds.x,
            window.bounds.y,
            window.bounds.width,
            title_bar_height,
        );

        // Draw title bar background
        let title_bar_color = if window.focused {
            window.decorations.title_bar_color
        } else {
            Color::new(128, 128, 128, 255)
        };

        GraphicsPrimitives::fill_rect(framebuffer, title_bar_rect, title_bar_color)?;

        // Draw title text
        let text_x = window.bounds.x + 10;
        let text_y = window.bounds.y + 8;
        GraphicsPrimitives::draw_text(
            framebuffer,
            &window.title,
            Point::new(text_x, text_y),
            window.decorations.title_text_color,
        )?;

        // Draw window control buttons if enabled
        if window.decorations.close_button {
            self.draw_close_button(framebuffer, window)?;
        }

        if window.decorations.minimize_button {
            self.draw_minimize_button(framebuffer, window)?;
        }

        if window.decorations.maximize_button {
            self.draw_maximize_button(framebuffer, window)?;
        }

        Ok(())
    }

    /// Draw window border
    fn draw_window_border(
        &self,
        framebuffer: &mut Framebuffer,
        window: &Window,
    ) -> Result<(), GraphicsError> {
        let border_color = if window.focused {
            window.decorations.border_color
        } else {
            Color::new(160, 160, 160, 255)
        };

        // Draw border rectangle
        GraphicsPrimitives::draw_rect(framebuffer, window.bounds, border_color)
    }

    /// Draw close button
    fn draw_close_button(
        &self,
        framebuffer: &mut Framebuffer,
        window: &Window,
    ) -> Result<(), GraphicsError> {
        let button_size = 20;
        let button_x = window.bounds.x + window.bounds.width as i32 - button_size - 5;
        let button_y = window.bounds.y + 5;

        let button_rect = Rect::new(button_x, button_y, button_size as u32, button_size as u32);
        GraphicsPrimitives::fill_rect(framebuffer, button_rect, Color::RED)?;

        // Draw X
        let center_x = button_x + button_size / 2;
        let center_y = button_y + button_size / 2;
        GraphicsPrimitives::draw_line(
            framebuffer,
            Point::new(center_x - 6, center_y - 6),
            Point::new(center_x + 6, center_y + 6),
            Color::WHITE,
        )?;
        GraphicsPrimitives::draw_line(
            framebuffer,
            Point::new(center_x + 6, center_y - 6),
            Point::new(center_x - 6, center_y + 6),
            Color::WHITE,
        )?;

        Ok(())
    }

    /// Draw minimize button
    fn draw_minimize_button(
        &self,
        framebuffer: &mut Framebuffer,
        window: &Window,
    ) -> Result<(), GraphicsError> {
        let button_size = 20;
        let button_x = window.bounds.x + window.bounds.width as i32 - (button_size * 2) - 10;
        let button_y = window.bounds.y + 5;

        let button_rect = Rect::new(button_x, button_y, button_size as u32, button_size as u32);
        GraphicsPrimitives::fill_rect(framebuffer, button_rect, Color::YELLOW)?;

        // Draw minimize line
        let line_y = button_y + button_size - 6;
        GraphicsPrimitives::draw_line(
            framebuffer,
            Point::new(button_x + 4, line_y),
            Point::new(button_x + button_size - 4, line_y),
            Color::BLACK,
        )?;

        Ok(())
    }

    /// Draw maximize button
    fn draw_maximize_button(
        &self,
        framebuffer: &mut Framebuffer,
        window: &Window,
    ) -> Result<(), GraphicsError> {
        let button_size = 20;
        let button_x = window.bounds.x + window.bounds.width as i32 - (button_size * 3) - 15;
        let button_y = window.bounds.y + 5;

        let button_rect = Rect::new(button_x, button_y, button_size as u32, button_size as u32);
        GraphicsPrimitives::fill_rect(framebuffer, button_rect, Color::GREEN)?;

        // Draw maximize rectangle
        let inner_rect = Rect::new(
            button_x + 4,
            button_y + 4,
            (button_size - 8) as u32,
            (button_size - 8) as u32,
        );
        GraphicsPrimitives::draw_rect(framebuffer, inner_rect, Color::BLACK)?;

        Ok(())
    }

    /// Update consciousness level for AI optimization
    pub fn update_consciousness(&mut self, level: f32) {
        self.consciousness_level = level.clamp(0.0, 1.0);

        // Adjust AI optimization based on consciousness level
        if self.consciousness_level > 0.7 {
            // High consciousness: Enable advanced AI features
            self.ai_layout_enabled = true;
        } else if self.consciousness_level < 0.3 {
            // Low consciousness: Disable AI optimization to save resources
            self.ai_layout_enabled = false;
        }

        crate::log_info!(
            "🧠 Window Manager consciousness updated: {:.2}",
            self.consciousness_level
        );
    }

    /// Get window information for debugging
    pub fn get_window_info(&self, window_id: WindowId) -> Option<&Window> {
        self.windows.get(&window_id)
    }

    /// Get list of all window IDs
    pub fn get_window_ids(&self) -> Vec<WindowId> {
        self.windows.keys().cloned().collect()
    }

    /// Educational function to demonstrate window management concepts
    pub fn demonstrate_window_concepts(&self) {
        crate::log_info!("🎓 Window Management Educational Demo:");
        crate::log_info!("  - Z-order: Windows stack on top of each other");
        crate::log_info!("  - Focus: Only one window receives input at a time");
        crate::log_info!("  - Decorations: Title bars, borders, and control buttons");
        crate::log_info!("  - AI optimization: Smart placement and layout");
        crate::log_info!("  - Consciousness: Adaptive behavior based on AI state");
    }
}

impl Drop for WindowManager {
    fn drop(&mut self) {
        crate::log_info!(
            "🪟 Window Manager shutting down, {} windows closed",
            self.windows.len()
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_window_creation() {
        let mut wm = WindowManager::new(1920, 1080);

        let create_info = WindowCreateInfo {
            title: "Test Window".to_string(),
            x: 100,
            y: 100,
            width: 800,
            height: 600,
            resizable: true,
            decorations: None,
        };

        let window_id = wm
            .create_window(create_info)
            .expect("Failed to create window");
        assert_eq!(window_id, 1);
        assert_eq!(wm.focused_window, Some(window_id));
    }

    #[test]
    fn test_window_focus() {
        let mut wm = WindowManager::new(1920, 1080);

        let create_info1 = WindowCreateInfo {
            title: "Window 1".to_string(),
            x: 100,
            y: 100,
            width: 400,
            height: 300,
            resizable: true,
            decorations: None,
        };

        let create_info2 = WindowCreateInfo {
            title: "Window 2".to_string(),
            x: 200,
            y: 200,
            width: 400,
            height: 300,
            resizable: true,
            decorations: None,
        };

        let window1 = wm.create_window(create_info1).unwrap();
        let window2 = wm.create_window(create_info2).unwrap();

        assert_eq!(wm.focused_window, Some(window2));

        wm.focus_window(window1).unwrap();
        assert_eq!(wm.focused_window, Some(window1));
    }
}
