//! HTTP Client for SIEM Integration
//!
//! Provides reliable HTTP communication with retry logic and error handling

use alloc::string::String;
use alloc::vec::Vec;

/// HTTP method types
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum HttpMethod {
    GET,
    POST,
    PUT,
    DELETE,
}

/// HTTP request configuration
#[derive(Debug, Clone)]
pub struct HttpRequest {
    pub url: String,
    pub method: HttpMethod,
    pub headers: Vec<(String, String)>,
    pub body: Option<String>,
    pub timeout_seconds: u64,
}

/// HTTP response
#[derive(Debug, Clone)]
pub struct HttpResponse {
    pub status_code: u16,
    pub headers: Vec<(String, String)>,
    pub body: String,
}

/// Connection pool entry
#[derive(Debug, Clone)]
struct Connection {
    host: String,
    port: u16,
    last_used: u64,
}

/// HTTP client with retry logic and connection pooling
pub struct HttpClient {
    max_retries: u32,
    retry_delay_ms: u64,
    circuit_breaker_threshold: u32,
    failures: u32,
    connections: Vec<Connection>,
    max_connections: usize,
}

impl HttpClient {
    /// Create new HTTP client
    pub fn new() -> Self {
        Self {
            max_retries: 3,
            retry_delay_ms: 1000,
            circuit_breaker_threshold: 5,
            failures: 0,
            connections: Vec::new(),
            max_connections: 10,
        }
    }

    /// Configure retry behavior
    pub fn with_retries(mut self, max_retries: u32, delay_ms: u64) -> Self {
        self.max_retries = max_retries;
        self.retry_delay_ms = delay_ms;
        self
    }

    /// Send HTTP request with retry logic
    pub fn send(&mut self, request: &HttpRequest) -> Result<HttpResponse, &'static str> {
        // Circuit breaker check
        if self.failures >= self.circuit_breaker_threshold {
            return Err("Circuit breaker open - too many failures");
        }

        let mut attempts = 0;
        let mut last_error = "Unknown error";

        while attempts <= self.max_retries {
            match self.send_once(request) {
                Ok(response) => {
                    // Reset failure count on success
                    self.failures = 0;
                    return Ok(response);
                }
                Err(err) => {
                    last_error = err;
                    attempts += 1;

                    if attempts <= self.max_retries {
                        // TODO: Actual delay implementation
                        // For now, just increment failure count
                        self.failures += 1;
                    }
                }
            }
        }

        Err(last_error)
    }

    /// Send single HTTP request (internal)
    fn send_once(&self, request: &HttpRequest) -> Result<HttpResponse, &'static str> {
        // Build HTTP request
        let method_str = match request.method {
            HttpMethod::GET => "GET",
            HttpMethod::POST => "POST",
            HttpMethod::PUT => "PUT",
            HttpMethod::DELETE => "DELETE",
        };

        // Parse URL to extract host, port, and path
        let (host, port, path) = Self::parse_url(&request.url)?;

        // Build HTTP request string
        let mut http_request = String::new();
        http_request.push_str(method_str);
        http_request.push_str(" ");
        http_request.push_str(&path);
        http_request.push_str(" HTTP/1.1\r\n");
        http_request.push_str("Host: ");
        http_request.push_str(&host);
        http_request.push_str("\r\n");
        http_request.push_str("User-Agent: SynOS-SIEM-Connector/1.0\r\n");
        http_request.push_str("Accept: */*\r\n");

        // Add custom headers
        for (key, value) in &request.headers {
            http_request.push_str(key);
            http_request.push_str(": ");
            http_request.push_str(value);
            http_request.push_str("\r\n");
        }

        // Add body if present
        if let Some(body) = &request.body {
            http_request.push_str("Content-Length: ");
            http_request.push_str(&body.len().to_string());
            http_request.push_str("\r\n");
            http_request.push_str("Content-Type: application/json\r\n");
            http_request.push_str("\r\n");
            http_request.push_str(body);
        } else {
            http_request.push_str("\r\n");
        }

        // TODO: Use kernel TCP stack to send request
        // For now, return simulated response
        Ok(HttpResponse {
            status_code: 200,
            headers: Vec::new(),
            body: String::from("{\"status\":\"ok\"}"),
        })
    }

    /// Parse URL into host, port, and path
    fn parse_url(url: &str) -> Result<(String, u16, String), &'static str> {
        // Remove protocol prefix
        let url = if url.starts_with("http://") {
            &url[7..]
        } else if url.starts_with("https://") {
            &url[8..]
        } else {
            url
        };

        // Split host and path
        let parts: Vec<&str> = url.splitn(2, '/').collect();
        let host_port = parts[0];
        let path = if parts.len() > 1 {
            String::from("/") + parts[1]
        } else {
            String::from("/")
        };

        // Parse host and port
        let (host, port) = if host_port.contains(':') {
            let hp: Vec<&str> = host_port.splitn(2, ':').collect();
            let port = hp[1].parse::<u16>().map_err(|_| "Invalid port number")?;
            (String::from(hp[0]), port)
        } else {
            (String::from(host_port), 80)
        };

        Ok((host, port, path))
    }

    /// Reset circuit breaker
    pub fn reset_circuit_breaker(&mut self) {
        self.failures = 0;
    }

    /// Get failure count
    pub fn get_failures(&self) -> u32 {
        self.failures
    }

    /// Get or create connection for host:port
    fn get_connection(&mut self, host: &str, port: u16) -> Result<&Connection, &'static str> {
        // Check for existing connection
        let existing = self.connections.iter().position(|c| c.host == host && c.port == port);

        if let Some(idx) = existing {
            return Ok(&self.connections[idx]);
        }

        // Create new connection if under limit
        if self.connections.len() < self.max_connections {
            let conn = Connection {
                host: String::from(host),
                port,
                last_used: 0, // TODO: Get actual timestamp
            };
            self.connections.push(conn);
            Ok(&self.connections[self.connections.len() - 1])
        } else {
            // Evict oldest connection
            let oldest_idx = self.connections.iter()
                .enumerate()
                .min_by_key(|(_, c)| c.last_used)
                .map(|(idx, _)| idx)
                .ok_or("No connections available")?;

            self.connections[oldest_idx] = Connection {
                host: String::from(host),
                port,
                last_used: 0,
            };
            Ok(&self.connections[oldest_idx])
        }
    }

    /// Parse HTTP response
    fn parse_response(raw_response: &str) -> Result<HttpResponse, &'static str> {
        let lines: Vec<&str> = raw_response.lines().collect();

        if lines.is_empty() {
            return Err("Empty response");
        }

        // Parse status line: HTTP/1.1 200 OK
        let status_parts: Vec<&str> = lines[0].split_whitespace().collect();
        if status_parts.len() < 2 {
            return Err("Invalid status line");
        }

        let status_code = status_parts[1].parse::<u16>()
            .map_err(|_| "Invalid status code")?;

        // Parse headers
        let mut headers = Vec::new();
        let mut header_end = 1;

        for (i, line) in lines.iter().enumerate().skip(1) {
            if line.is_empty() {
                header_end = i + 1;
                break;
            }

            if let Some(pos) = line.find(':') {
                let key = line[..pos].trim();
                let value = line[pos + 1..].trim();
                headers.push((String::from(key), String::from(value)));
            }
        }

        // Extract body
        let body = if header_end < lines.len() {
            lines[header_end..].join("\n")
        } else {
            String::new()
        };

        Ok(HttpResponse {
            status_code,
            headers,
            body,
        })
    }

    /// Send POST request with JSON body
    pub fn post_json(&mut self, url: &str, json_body: &str) -> Result<HttpResponse, &'static str> {
        let request = HttpRequest {
            url: String::from(url),
            method: HttpMethod::POST,
            headers: vec![
                (String::from("Content-Type"), String::from("application/json")),
            ],
            body: Some(String::from(json_body)),
            timeout_seconds: 30,
        };

        self.send(&request)
    }

    /// Send GET request
    pub fn get(&mut self, url: &str) -> Result<HttpResponse, &'static str> {
        let request = HttpRequest {
            url: String::from(url),
            method: HttpMethod::GET,
            headers: Vec::new(),
            body: None,
            timeout_seconds: 30,
        };

        self.send(&request)
    }
}

impl Default for HttpClient {
    fn default() -> Self {
        Self::new()
    }
}

/// Batch HTTP request manager for high-throughput scenarios
pub struct BatchHttpClient {
    client: HttpClient,
    batch_size: usize,
    pending_requests: Vec<HttpRequest>,
}

impl BatchHttpClient {
    pub fn new(batch_size: usize) -> Self {
        Self {
            client: HttpClient::new(),
            batch_size,
            pending_requests: Vec::new(),
        }
    }

    /// Add request to batch
    pub fn add_request(&mut self, request: HttpRequest) {
        self.pending_requests.push(request);
    }

    /// Flush pending requests (send all)
    pub fn flush(&mut self) -> Result<Vec<HttpResponse>, &'static str> {
        let mut responses = Vec::new();

        for request in &self.pending_requests {
            match self.client.send(request) {
                Ok(response) => responses.push(response),
                Err(e) => return Err(e),
            }
        }

        self.pending_requests.clear();
        Ok(responses)
    }

    /// Send batch if size threshold reached
    pub fn try_flush(&mut self) -> Result<Option<Vec<HttpResponse>>, &'static str> {
        if self.pending_requests.len() >= self.batch_size {
            Ok(Some(self.flush()?))
        } else {
            Ok(None)
        }
    }

    /// Get pending request count
    pub fn pending_count(&self) -> usize {
        self.pending_requests.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_http_client_creation() {
        let client = HttpClient::new();
        assert_eq!(client.max_retries, 3);
        assert_eq!(client.max_connections, 10);
    }

    #[test]
    fn test_circuit_breaker() {
        let mut client = HttpClient::new();
        client.failures = 5;

        let request = HttpRequest {
            url: "http://example.com".into(),
            method: HttpMethod::POST,
            headers: Vec::new(),
            body: None,
            timeout_seconds: 30,
        };

        assert!(client.send(&request).is_err());
    }

    #[test]
    fn test_url_parsing() {
        let result = HttpClient::parse_url("http://api.example.com:8080/v1/events");
        assert!(result.is_ok());

        let (host, port, path) = result.unwrap();
        assert_eq!(host, "api.example.com");
        assert_eq!(port, 8080);
        assert_eq!(path, "/v1/events");
    }

    #[test]
    fn test_url_parsing_default_port() {
        let result = HttpClient::parse_url("http://api.example.com/v1/events");
        assert!(result.is_ok());

        let (host, port, path) = result.unwrap();
        assert_eq!(host, "api.example.com");
        assert_eq!(port, 80);
        assert_eq!(path, "/v1/events");
    }

    #[test]
    fn test_batch_client() {
        let mut batch = BatchHttpClient::new(5);
        assert_eq!(batch.pending_count(), 0);

        // Add requests
        for i in 0..3 {
            batch.add_request(HttpRequest {
                url: alloc::format!("http://api.example.com/event/{}", i),
                method: HttpMethod::POST,
                headers: Vec::new(),
                body: Some(String::from("{}")),
                timeout_seconds: 30,
            });
        }

        assert_eq!(batch.pending_count(), 3);

        // Should not flush yet (threshold is 5)
        assert!(batch.try_flush().unwrap().is_none());
        assert_eq!(batch.pending_count(), 3);

        // Add 2 more to reach threshold
        for i in 3..5 {
            batch.add_request(HttpRequest {
                url: alloc::format!("http://api.example.com/event/{}", i),
                method: HttpMethod::POST,
                headers: Vec::new(),
                body: Some(String::from("{}")),
                timeout_seconds: 30,
            });
        }

        // Should flush now
        let result = batch.try_flush();
        assert!(result.is_ok());
        assert!(result.unwrap().is_some());
        assert_eq!(batch.pending_count(), 0);
    }

    #[test]
    fn test_response_parsing() {
        let raw_response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 16\r\n\r\n{\"status\":\"ok\"}";
        let response = HttpClient::parse_response(raw_response);

        assert!(response.is_ok());
        let resp = response.unwrap();
        assert_eq!(resp.status_code, 200);
        assert_eq!(resp.body, "{\"status\":\"ok\"}");
        assert!(resp.headers.iter().any(|(k, v)| k == "Content-Type" && v == "application/json"));
    }
}
