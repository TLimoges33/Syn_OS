package middleware

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
	"github.com/syn-os/orchestrator/internal/config"
	"golang.org/x/crypto/bcrypt"
)

// JWTClaims represents JWT token claims
type JWTClaims struct {
	UserID   string   `json:"user_id"`
	Username string   `json:"username"`
	Roles    []string `json:"roles"`
	IsSystem bool     `json:"is_system"`
	jwt.RegisteredClaims
}

// ValidationRule represents input validation configuration
type ValidationRule struct {
	Required    bool
	MinLength   int
	MaxLength   int
	Pattern     *regexp.Regexp
	Sanitize    bool
	AllowedVals []string
}

var (
	// Common validation patterns
	usernamePattern = regexp.MustCompile(`^[a-zA-Z0-9._-]+$`)
	emailPattern    = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	uuidPattern     = regexp.MustCompile(`^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`)
	
	// Security risk patterns
	sqlInjectionPattern = regexp.MustCompile(`(?i)\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT|OR|AND)\b|--|#|/\*|\*/`)
	xssPattern         = regexp.MustCompile(`(?i)<script[^>]*>|javascript:|vbscript:|onload\s*=|onerror\s*=|onclick\s*=|<iframe[^>]*>|<object[^>]*>`)
	cmdInjectionPattern = regexp.MustCompile(`[;&|` + "`" + `$(){}[\]\\]|\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ping|wget|curl|nc|telnet|ssh|ftp)\b`)
)

// Enhanced JWT authentication middleware with proper token validation
func EnhancedJWTAuth(securityConfig config.SecurityConfig) gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		// Skip authentication if disabled
		if !securityConfig.EnableAuth {
			c.Next()
			return
		}

		// Get authorization header
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Authorization header required",
				"code":  "AUTH_HEADER_MISSING",
			})
			c.Abort()
			return
		}

		// Check for Bearer token format
		if !strings.HasPrefix(authHeader, "Bearer ") {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid authorization header format. Use 'Bearer <token>'",
				"code":  "AUTH_HEADER_INVALID_FORMAT",
			})
			c.Abort()
			return
		}

		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == "" {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Token required",
				"code":  "TOKEN_MISSING",
			})
			c.Abort()
			return
		}

		// Parse and validate JWT token
		claims, err := parseJWTToken(tokenString, securityConfig.JWTSecret)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": fmt.Sprintf("Invalid token: %v", err),
				"code":  "TOKEN_INVALID",
			})
			c.Abort()
			return
		}

		// Check token expiration
		if time.Now().Unix() > claims.ExpiresAt.Unix() {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Token expired",
				"code":  "TOKEN_EXPIRED",
			})
			c.Abort()
			return
		}

		// Set user context
		c.Set("user_id", claims.UserID)
		c.Set("username", claims.Username)
		c.Set("user_roles", claims.Roles)
		c.Set("is_system", claims.IsSystem)
		c.Set("authenticated", true)
		c.Set("jwt_claims", claims)

		c.Next()
	})
}

// Enhanced input validation middleware
func InputValidation() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		// Skip validation for GET requests without query params
		if c.Request.Method == "GET" && len(c.Request.URL.RawQuery) == 0 {
			c.Next()
			return
		}

		// Validate all input parameters
		if err := validateRequest(c); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Input validation failed",
				"details": err.Error(),
				"code": "INPUT_VALIDATION_ERROR",
			})
			c.Abort()
			return
		}

		c.Next()
	})
}

// Rate limiting middleware to prevent brute force attacks
func RateLimit() gin.HandlerFunc {
	// In production, use Redis or similar for distributed rate limiting
	clientRequests := make(map[string][]time.Time)
	
	return gin.HandlerFunc(func(c *gin.Context) {
		clientIP := c.ClientIP()
		now := time.Now()
		
		// Clean old entries
		if requests, exists := clientRequests[clientIP]; exists {
			var validRequests []time.Time
			for _, reqTime := range requests {
				if now.Sub(reqTime) <= time.Minute {
					validRequests = append(validRequests, reqTime)
				}
			}
			clientRequests[clientIP] = validRequests
		}
		
		// Check rate limit (100 requests per minute)
		if len(clientRequests[clientIP]) >= 100 {
			c.JSON(http.StatusTooManyRequests, gin.H{
				"error": "Rate limit exceeded",
				"code":  "RATE_LIMIT_EXCEEDED",
				"retry_after": 60,
			})
			c.Abort()
			return
		}
		
		// Add current request
		clientRequests[clientIP] = append(clientRequests[clientIP], now)
		
		c.Next()
	})
}

// parseJWTToken parses and validates a JWT token
func parseJWTToken(tokenString, secret string) (*JWTClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &JWTClaims{}, func(token *jwt.Token) (interface{}, error) {
		// Validate signing method
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("invalid signing method: %v", token.Header["alg"])
		}
		return []byte(secret), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*JWTClaims); ok && token.Valid {
		return claims, nil
	}

	return nil, fmt.Errorf("invalid token claims")
}

// generateJWTToken creates a new JWT token
func GenerateJWTToken(userID, username string, roles []string, secret string, duration time.Duration) (string, error) {
	claims := JWTClaims{
		UserID:   userID,
		Username: username,
		Roles:    roles,
		IsSystem: false,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(duration)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
			Issuer:    "syn-os-orchestrator",
			Subject:   userID,
			ID:        generateTokenID(),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(secret))
}

// generateSystemToken creates a system-level JWT token
func GenerateSystemToken(secret string, duration time.Duration) (string, error) {
	claims := JWTClaims{
		UserID:   "system",
		Username: "system",
		Roles:    []string{"system", "admin"},
		IsSystem: true,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(duration)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
			Issuer:    "syn-os-orchestrator",
			Subject:   "system",
			ID:        generateTokenID(),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(secret))
}

// validateRequest validates the incoming request for security risks
func validateRequest(c *gin.Context) error {
	// Validate query parameters
	for key, values := range c.Request.URL.Query() {
		for _, value := range values {
			if err := validateInput(key, value); err != nil {
				return fmt.Errorf("query parameter '%s': %v", key, err)
			}
		}
	}

	// Validate form data
	if c.Request.Method == "POST" || c.Request.Method == "PUT" || c.Request.Method == "PATCH" {
		c.Request.ParseForm()
		for key, values := range c.Request.PostForm {
			for _, value := range values {
				if err := validateInput(key, value); err != nil {
					return fmt.Errorf("form parameter '%s': %v", key, err)
				}
			}
		}
	}

	return nil
}

// validateInput validates individual input values
func validateInput(fieldName, value string) error {
	// Check for common security risks
	if sqlInjectionPattern.MatchString(value) {
		return fmt.Errorf("contains potentially dangerous SQL content")
	}

	if xssPattern.MatchString(value) {
		return fmt.Errorf("contains potentially dangerous script content")
	}

	if cmdInjectionPattern.MatchString(value) {
		return fmt.Errorf("contains potentially dangerous command injection content")
	}

	// Field-specific validation
	switch fieldName {
	case "username":
		return validateUsername(value)
	case "email":
		return validateEmail(value)
	case "id", "user_id", "service_id":
		return validateUUID(value)
	}

	// General string validation
	return validateString(value)
}

// validateUsername validates username format
func validateUsername(username string) error {
	if len(username) < 3 || len(username) > 50 {
		return fmt.Errorf("username must be between 3 and 50 characters")
	}

	if !usernamePattern.MatchString(username) {
		return fmt.Errorf("username can only contain letters, numbers, dots, underscores, and hyphens")
	}

	reservedUsernames := []string{
		"admin", "administrator", "root", "system", "api", "test", "guest",
		"null", "undefined", "anonymous", "public", "private",
	}

	for _, reserved := range reservedUsernames {
		if strings.EqualFold(username, reserved) {
			return fmt.Errorf("username is reserved")
		}
	}

	return nil
}

// validateEmail validates email format
func validateEmail(email string) error {
	if len(email) > 254 {
		return fmt.Errorf("email address too long")
	}

	if !emailPattern.MatchString(email) {
		return fmt.Errorf("invalid email address format")
	}

	return nil
}

// validateUUID validates UUID format
func validateUUID(uuid string) error {
	if !uuidPattern.MatchString(strings.ToLower(uuid)) {
		return fmt.Errorf("invalid UUID format")
	}

	return nil
}

// validateString performs general string validation
func validateString(value string) error {
	// Check for null bytes
	if strings.Contains(value, "\x00") {
		return fmt.Errorf("contains null bytes")
	}

	// Check maximum length
	if len(value) > 10000 {
		return fmt.Errorf("string too long (maximum 10000 characters)")
	}

	return nil
}

// generateTokenID generates a unique token ID
func generateTokenID() string {
	bytes := make([]byte, 16)
	rand.Read(bytes)
	return hex.EncodeToString(bytes)
}

// HashPassword hashes a password using bcrypt
func HashPassword(password string) (string, error) {
	bytes, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(bytes), err
}

// CheckPasswordHash checks if a password matches a hash
func CheckPasswordHash(password, hash string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hash), []byte(password))
	return err == nil
}

// Security headers middleware
func SecurityHeaders() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		// Prevent clickjacking
		c.Header("X-Frame-Options", "DENY")
		
		// Prevent MIME sniffing
		c.Header("X-Content-Type-Options", "nosniff")
		
		// Enable XSS protection
		c.Header("X-XSS-Protection", "1; mode=block")
		
		// Strict transport security
		c.Header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
		
		// Content security policy
		c.Header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'")
		
		// Referrer policy
		c.Header("Referrer-Policy", "strict-origin-when-cross-origin")
		
		c.Next()
	})
}