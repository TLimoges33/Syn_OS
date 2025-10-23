//! Graphics Primitives for SynOS
//!
//! Provides basic drawing operations with AI-enhanced optimization
//! and educational features for learning graphics concepts.

use crate::{Color, Point, Rect, GraphicsError};
use crate::framebuffer::Framebuffer;
use alloc::vec::Vec;
use alloc::vec;


/// Graphics primitives with AI enhancement
pub struct GraphicsPrimitives;

impl GraphicsPrimitives {
    /// Draw a line between two points using Bresenham's algorithm
    pub fn draw_line(
        framebuffer: &mut Framebuffer,
        start: Point,
        end: Point,
        color: Color,
    ) -> Result<(), GraphicsError> {
        let dx = (end.x - start.x).abs();
        let dy = (end.y - start.y).abs();
        let sx = if start.x < end.x { 1 } else { -1 };
        let sy = if start.y < end.y { 1 } else { -1 };
        let mut err = dx - dy;

        let mut current = start;

        loop {
            framebuffer.set_pixel(current, color)?;

            if current.x == end.x && current.y == end.y {
                break;
            }

            let e2 = 2 * err;
            if e2 > -dy {
                err -= dy;
                current.x += sx;
            }
            if e2 < dx {
                err += dx;
                current.y += sy;
            }
        }

        Ok(())
    }

    /// Draw a circle using Bresenham's circle algorithm
    pub fn draw_circle(
        framebuffer: &mut Framebuffer,
        center: Point,
        radius: u32,
        color: Color,
    ) -> Result<(), GraphicsError> {
        let mut x = 0i32;
        let mut y = radius as i32;
        let mut d = 3 - 2 * radius as i32;

        while y >= x {
            // Draw 8 octants
            Self::draw_circle_points(framebuffer, center, x, y, color)?;
            x += 1;

            if d > 0 {
                y -= 1;
                d = d + 4 * (x - y) + 10;
            } else {
                d = d + 4 * x + 6;
            }
        }

        Ok(())
    }

    /// Draw filled circle
    pub fn fill_circle(
        framebuffer: &mut Framebuffer,
        center: Point,
        radius: u32,
        color: Color,
    ) -> Result<(), GraphicsError> {
        for y in -(radius as i32)..=(radius as i32) {
            for x in -(radius as i32)..=(radius as i32) {
                if x * x + y * y <= (radius as i32) * (radius as i32) {
                    framebuffer.set_pixel(
                        Point::new(center.x + x, center.y + y),
                        color,
                    )?;
                }
            }
        }

        Ok(())
    }

    /// Draw helper for circle points in all octants
    fn draw_circle_points(
        framebuffer: &mut Framebuffer,
        center: Point,
        x: i32,
        y: i32,
        color: Color,
    ) -> Result<(), GraphicsError> {
        framebuffer.set_pixel(Point::new(center.x + x, center.y + y), color)?;
        framebuffer.set_pixel(Point::new(center.x - x, center.y + y), color)?;
        framebuffer.set_pixel(Point::new(center.x + x, center.y - y), color)?;
        framebuffer.set_pixel(Point::new(center.x - x, center.y - y), color)?;
        framebuffer.set_pixel(Point::new(center.x + y, center.y + x), color)?;
        framebuffer.set_pixel(Point::new(center.x - y, center.y + x), color)?;
        framebuffer.set_pixel(Point::new(center.x + y, center.y - x), color)?;
        framebuffer.set_pixel(Point::new(center.x - y, center.y - x), color)?;
        Ok(())
    }

    /// Draw a triangle outline
    pub fn draw_triangle(
        framebuffer: &mut Framebuffer,
        p1: Point,
        p2: Point,
        p3: Point,
        color: Color,
    ) -> Result<(), GraphicsError> {
        Self::draw_line(framebuffer, p1, p2, color)?;
        Self::draw_line(framebuffer, p2, p3, color)?;
        Self::draw_line(framebuffer, p3, p1, color)?;
        Ok(())
    }

    /// Draw filled triangle using scanline algorithm
    pub fn fill_triangle(
        framebuffer: &mut Framebuffer,
        p1: Point,
        p2: Point,
        p3: Point,
        color: Color,
    ) -> Result<(), GraphicsError> {
        // Sort points by y coordinate
        let mut points = [p1, p2, p3];
        points.sort_by_key(|p| p.y);

        let (top, mid, bottom) = (points[0], points[1], points[2]);

        // Fill upper triangle
        Self::fill_triangle_half(framebuffer, top, mid, bottom, true, color)?;

        // Fill lower triangle
        Self::fill_triangle_half(framebuffer, top, mid, bottom, false, color)?;

        Ok(())
    }

    /// Helper for filling triangle halves
    fn fill_triangle_half(
        framebuffer: &mut Framebuffer,
        top: Point,
        mid: Point,
        bottom: Point,
        upper_half: bool,
        color: Color,
    ) -> Result<(), GraphicsError> {
        let (start_y, end_y) = if upper_half {
            (top.y, mid.y)
        } else {
            (mid.y, bottom.y)
        };

        for y in start_y..=end_y {
            if y == start_y || y == end_y {
                continue;
            }

            // Calculate x intersections
            let x1 = Self::interpolate_x(top, bottom, y);
            let x2 = if upper_half {
                Self::interpolate_x(top, mid, y)
            } else {
                Self::interpolate_x(mid, bottom, y)
            };

            let (start_x, end_x) = if x1 < x2 { (x1, x2) } else { (x2, x1) };

            // Draw horizontal line
            for x in start_x..=end_x {
                framebuffer.set_pixel(Point::new(x, y), color)?;
            }
        }

        Ok(())
    }

    /// Interpolate x coordinate for given y on line between two points
    fn interpolate_x(p1: Point, p2: Point, y: i32) -> i32 {
        if p2.y == p1.y {
            return p1.x;
        }

        p1.x + ((y - p1.y) * (p2.x - p1.x)) / (p2.y - p1.y)
    }

    /// Draw text using a simple bitmap font
    pub fn draw_text(
        framebuffer: &mut Framebuffer,
        text: &str,
        position: Point,
        color: Color,
    ) -> Result<(), GraphicsError> {
        let font = SimpleBitmapFont::new();
        let mut current_x = position.x;

        for ch in text.chars() {
            if let Some(glyph) = font.get_glyph(ch) {
                Self::draw_glyph(framebuffer, &glyph, Point::new(current_x, position.y), color)?;
                current_x += glyph.width as i32 + 1; // 1 pixel spacing
            }
        }

        Ok(())
    }

    /// Fill a rectangle with solid color
    pub fn fill_rect(
        framebuffer: &mut Framebuffer,
        rect: Rect,
        color: Color,
    ) -> Result<(), GraphicsError> {
        for y in rect.y..(rect.y + rect.height as i32) {
            for x in rect.x..(rect.x + rect.width as i32) {
                if x < framebuffer.resolution().width as i32 && y < framebuffer.resolution().height as i32 {
                    framebuffer.set_pixel(Point::new(x, y), color)?;
                }
            }
        }
        Ok(())
    }

    /// Draw rectangle outline
    pub fn draw_rect(
        framebuffer: &mut Framebuffer,
        rect: Rect,
        color: Color,
    ) -> Result<(), GraphicsError> {
        // Draw top and bottom edges
        for x in rect.x..(rect.x + rect.width as i32) {
            if x < framebuffer.resolution().width as i32 {
                if rect.y < framebuffer.resolution().height as i32 {
                    framebuffer.set_pixel(Point::new(x, rect.y), color)?;
                }
                if rect.y + rect.height as i32 - 1 < framebuffer.resolution().height as i32 {
                    framebuffer.set_pixel(Point::new(x, rect.y + rect.height as i32 - 1), color)?;
                }
            }
        }

        // Draw left and right edges
        for y in rect.y..(rect.y + rect.height as i32) {
            if y < framebuffer.resolution().height as i32 {
                if rect.x < framebuffer.resolution().width as i32 {
                    framebuffer.set_pixel(Point::new(rect.x, y), color)?;
                }
                if rect.x + rect.width as i32 - 1 < framebuffer.resolution().width as i32 {
                    framebuffer.set_pixel(Point::new(rect.x + rect.width as i32 - 1, y), color)?;
                }
            }
        }
        Ok(())
    }

    /// Draw a single character glyph
    fn draw_glyph(
        framebuffer: &mut Framebuffer,
        glyph: &Glyph,
        position: Point,
        color: Color,
    ) -> Result<(), GraphicsError> {
        for y in 0..glyph.height {
            for x in 0..glyph.width {
                let bit_index = y * glyph.width + x;
                let byte_index = (bit_index / 8) as usize;
                let bit_offset = bit_index % 8;

                if byte_index < glyph.data.len() {
                    let bit_set = (glyph.data[byte_index] >> (7 - bit_offset)) & 1 == 1;
                    if bit_set {
                        framebuffer.set_pixel(
                            Point::new(position.x + x as i32, position.y + y as i32),
                            color,
                        )?;
                    }
                }
            }
        }

        Ok(())
    }

    /// AI-enhanced drawing optimization
    pub fn optimize_drawing_operations(
        operations: &[DrawingOperation],
        consciousness_level: f32,
    ) -> Vec<DrawingOperation> {
        // AI optimization based on consciousness level
        let mut optimized = operations.to_vec();

        if consciousness_level > 0.5 {
            // High consciousness: merge similar operations
            optimized = Self::merge_similar_operations(optimized);
        }

        if consciousness_level > 0.7 {
            // Very high consciousness: reorder for cache efficiency
            optimized = Self::reorder_for_cache_efficiency(optimized);
        }

        optimized
    }

    /// Merge similar drawing operations for efficiency
    fn merge_similar_operations(operations: Vec<DrawingOperation>) -> Vec<DrawingOperation> {
        // Merge adjacent or overlapping operations of the same type and color
        let mut merged = Vec::new();
        let mut current_batch: Option<DrawingOperation> = None;

        for op in operations {
            match &current_batch {
                None => current_batch = Some(op),
                Some(batch) => {
                    if Self::can_merge_operations(batch, &op) {
                        // Merge operations by expanding the area
                        current_batch = Some(Self::merge_two_operations(batch.clone(), op));
                    } else {
                        // Can't merge, push current batch and start new one
                        merged.push(current_batch.take().unwrap());
                        current_batch = Some(op);
                    }
                }
            }
        }

        // Push final batch
        if let Some(batch) = current_batch {
            merged.push(batch);
        }

        merged
    }

    /// Reorder operations for better cache efficiency
    fn reorder_for_cache_efficiency(mut operations: Vec<DrawingOperation>) -> Vec<DrawingOperation> {
        // Sort by y-coordinate first (row-major order for better cache locality)
        // Then by x-coordinate within the same row for optimal memory access
        operations.sort_by(|a, b| {
            let (y_a, x_a) = Self::get_operation_coordinates(a);
            let (y_b, x_b) = Self::get_operation_coordinates(b);

            match y_a.cmp(&y_b) {
                core::cmp::Ordering::Equal => x_a.cmp(&x_b),
                other => other,
            }
        });

        // Group operations by type to minimize GPU state changes
        let mut rects = Vec::new();
        let mut lines = Vec::new();
        let mut circles = Vec::new();
        let mut pixels = Vec::new();

        for op in operations {
            match op {
                DrawingOperation::Rectangle { .. } => rects.push(op),
                DrawingOperation::Line { .. } => lines.push(op),
                DrawingOperation::Circle { .. } => circles.push(op),
                DrawingOperation::Pixel { .. } => pixels.push(op),
            }
        }

        // Combine in optimal order (rectangles first for fill operations, then outlines)
        let mut result = Vec::new();
        result.extend(rects);
        result.extend(lines);
        result.extend(circles);
        result.extend(pixels);

        result
    }

    /// Check if two operations can be merged
    fn can_merge_operations(op1: &DrawingOperation, op2: &DrawingOperation) -> bool {
        match (op1, op2) {
            (DrawingOperation::Rectangle { rect: r1, color: c1 },
             DrawingOperation::Rectangle { rect: r2, color: c2 }) => {
                // Same color and adjacent/overlapping rectangles
                c1 == c2 && Self::rectangles_adjacent(r1, r2)
            }
            (DrawingOperation::Pixel { point: p1, color: c1 },
             DrawingOperation::Pixel { point: p2, color: c2 }) => {
                // Same color and adjacent pixels
                c1 == c2 && Self::points_adjacent(p1, p2)
            }
            _ => false, // Different operation types can't be merged
        }
    }

    /// Merge two compatible operations
    fn merge_two_operations(op1: DrawingOperation, op2: DrawingOperation) -> DrawingOperation {
        match (&op1, op2) {
            (DrawingOperation::Rectangle { rect: r1, color },
             DrawingOperation::Rectangle { rect: r2, .. }) => {
                // Create bounding rectangle
                let min_x = r1.x.min(r2.x);
                let min_y = r1.y.min(r2.y);
                let max_x = (r1.x + r1.width as i32).max(r2.x + r2.width as i32);
                let max_y = (r1.y + r1.height as i32).max(r2.y + r2.height as i32);

                DrawingOperation::Rectangle {
                    rect: Rect::new(min_x, min_y, (max_x - min_x) as u32, (max_y - min_y) as u32),
                    color: *color,
                }
            }
            _ => op1, // Fallback to first operation
        }
    }

    /// Get primary coordinates for an operation (for sorting)
    fn get_operation_coordinates(op: &DrawingOperation) -> (i32, i32) {
        match op {
            DrawingOperation::Pixel { point, .. } => (point.y, point.x),
            DrawingOperation::Line { start, .. } => (start.y, start.x),
            DrawingOperation::Circle { center, .. } => (center.y, center.x),
            DrawingOperation::Rectangle { rect, .. } => (rect.y, rect.x),
        }
    }

    /// Check if two rectangles are adjacent or overlapping
    fn rectangles_adjacent(r1: &Rect, r2: &Rect) -> bool {
        let r1_right = r1.x + r1.width as i32;
        let r1_bottom = r1.y + r1.height as i32;
        let r2_right = r2.x + r2.width as i32;
        let r2_bottom = r2.y + r2.height as i32;

        // Check for overlap or adjacency
        !(r1_right < r2.x || r2_right < r1.x || r1_bottom < r2.y || r2_bottom < r1.y)
    }

    /// Check if two points are adjacent (within 1 pixel)
    fn points_adjacent(p1: &Point, p2: &Point) -> bool {
        let dx = (p1.x - p2.x).abs();
        let dy = (p1.y - p2.y).abs();
        dx <= 1 && dy <= 1
    }

    /// Educational demonstration of graphics primitives
    pub fn demonstrate_primitives(framebuffer: &mut Framebuffer) -> Result<(), GraphicsError> {
        crate::log_info!("🎓 Graphics Primitives Educational Demo");

        let resolution = framebuffer.resolution();
        let center_x = resolution.width as i32 / 2;
        let center_y = resolution.height as i32 / 2;

        // Clear with consciousness blue
        framebuffer.clear(Color::CONSCIOUSNESS_BLUE)?;

        // Draw coordinate axes
        Self::draw_line(
            framebuffer,
            Point::new(0, center_y),
            Point::new(resolution.width as i32, center_y),
            Color::WHITE,
        )?;
        Self::draw_line(
            framebuffer,
            Point::new(center_x, 0),
            Point::new(center_x, resolution.height as i32),
            Color::WHITE,
        )?;

        // Draw educational shapes
        let shapes_center = Point::new(center_x - 100, center_y - 100);

        // Circle demonstration
        Self::draw_circle(framebuffer, shapes_center, 30, Color::AI_GREEN)?;
        Self::fill_circle(framebuffer, Point::new(shapes_center.x, shapes_center.y + 20), 10, Color::EDUCATION_ORANGE)?;

        // Triangle demonstration
        let triangle_center = Point::new(center_x + 100, center_y - 100);
        Self::draw_triangle(
            framebuffer,
            Point::new(triangle_center.x, triangle_center.y - 30),
            Point::new(triangle_center.x - 30, triangle_center.y + 30),
            Point::new(triangle_center.x + 30, triangle_center.y + 30),
            Color::MAGENTA,
        )?;

        // Rectangle demonstration
        let rect = Rect::new(center_x - 50, center_y + 50, 100, 60);
        framebuffer.fill_rect(rect, Color::YELLOW)?;

        // Text demonstration
        Self::draw_text(
            framebuffer,
            "SynOS Graphics",
            Point::new(center_x - 60, center_y + 150),
            Color::WHITE,
        )?;

        crate::log_info!("✅ Primitives demonstration complete");
        Ok(())
    }
}

/// Drawing operation types for AI optimization
#[derive(Debug, Clone)]
pub enum DrawingOperation {
    Pixel { point: Point, color: Color },
    Line { start: Point, end: Point, color: Color },
    Circle { center: Point, radius: u32, color: Color },
    Rectangle { rect: Rect, color: Color },
}

/// Simple bitmap font for text rendering
struct SimpleBitmapFont {
    glyphs: Vec<(char, Glyph)>,
}

/// Character glyph definition
#[derive(Debug, Clone)]
struct Glyph {
    width: u32,
    height: u32,
    data: Vec<u8>,
}

impl SimpleBitmapFont {
    /// Create a new simple bitmap font
    fn new() -> Self {
        let mut font = Self {
            glyphs: Vec::new(),
        };

        // Add basic ASCII characters
        font.add_basic_glyphs();
        font
    }

    /// Add basic character glyphs
    fn add_basic_glyphs(&mut self) {
        // Simple 8x8 font definitions

        // 'S' for SynOS
        self.glyphs.push(('S', Glyph {
            width: 8,
            height: 8,
            data: vec![
                0b01111110,
                0b10000000,
                0b10000000,
                0b01111110,
                0b00000001,
                0b00000001,
                0b10000001,
                0b01111110,
            ],
        }));

        // 'y'
        self.glyphs.push(('y', Glyph {
            width: 8,
            height: 8,
            data: vec![
                0b00000000,
                0b00000000,
                0b10000001,
                0b10000001,
                0b01000010,
                0b00100100,
                0b00011000,
                0b00110000,
            ],
        }));

        // 'n'
        self.glyphs.push(('n', Glyph {
            width: 8,
            height: 8,
            data: vec![
                0b00000000,
                0b00000000,
                0b10111110,
                0b11000001,
                0b10000001,
                0b10000001,
                0b10000001,
                0b00000000,
            ],
        }));

        // 'O'
        self.glyphs.push(('O', Glyph {
            width: 8,
            height: 8,
            data: vec![
                0b01111110,
                0b10000001,
                0b10000001,
                0b10000001,
                0b10000001,
                0b10000001,
                0b10000001,
                0b01111110,
            ],
        }));

        // Space character
        self.glyphs.push((' ', Glyph {
            width: 8,
            height: 8,
            data: vec![0; 8],
        }));

        // Add more characters as needed...
    }

    /// Get glyph for a character
    fn get_glyph(&self, ch: char) -> Option<&Glyph> {
        self.glyphs.iter()
            .find(|(c, _)| *c == ch)
            .map(|(_, glyph)| glyph)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::graphics::{Resolution, ColorFormat};
    use alloc::vec;

    #[test]
    fn test_line_drawing() {
        let resolution = Resolution::new(100, 100, ColorFormat::RGBA8888);
        let mut buffer = vec![0u8; resolution.buffer_size()];
        let buffer_ptr = buffer.as_mut_ptr();

        let mut framebuffer = Framebuffer::new(resolution, buffer_ptr, 100 * 4).unwrap();

        let result = GraphicsPrimitives::draw_line(
            &mut framebuffer,
            Point::new(10, 10),
            Point::new(50, 50),
            Color::RED,
        );

        assert!(result.is_ok());
    }

    #[test]
    fn test_circle_drawing() {
        let resolution = Resolution::new(100, 100, ColorFormat::RGBA8888);
        let mut buffer = vec![0u8; resolution.buffer_size()];
        let buffer_ptr = buffer.as_mut_ptr();

        let mut framebuffer = Framebuffer::new(resolution, buffer_ptr, 100 * 4).unwrap();

        let result = GraphicsPrimitives::draw_circle(
            &mut framebuffer,
            Point::new(50, 50),
            20,
            Color::GREEN,
        );

        assert!(result.is_ok());
    }
}
