package middleware

import (
	"fmt"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// RequestID returns a middleware that adds a unique request ID to each request
func RequestID() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = uuid.New().String()
		}

		c.Header("X-Request-ID", requestID)
		c.Set("request_id", requestID)
		c.Next()
	})
}

// Logger returns a middleware that logs HTTP requests
func Logger() gin.HandlerFunc {
	return gin.LoggerWithFormatter(func(param gin.LogFormatterParams) string {
		return fmt.Sprintf("[%s] %s %s %s %d %s %s %s\n",
			param.TimeStamp.Format("2006/01/02 - 15:04:05"),
			param.ClientIP,
			param.Method,
			param.Path,
			param.StatusCode,
			param.Latency,
			param.Request.UserAgent(),
			param.ErrorMessage,
		)
	})
}

// StructuredLogger returns a middleware that logs requests in structured format
func StructuredLogger() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		raw := c.Request.URL.RawQuery

		// Process request
		c.Next()

		// Log request details
		param := gin.LogFormatterParams{
			Request:      c.Request,
			TimeStamp:    time.Now(),
			Latency:      time.Since(start),
			ClientIP:     c.ClientIP(),
			Method:       c.Request.Method,
			StatusCode:   c.Writer.Status(),
			ErrorMessage: c.Errors.ByType(gin.ErrorTypePrivate).String(),
			BodySize:     c.Writer.Size(),
		}

		if raw != "" {
			path = path + "?" + raw
		}
		param.Path = path

		// In a real implementation, this would use structured logging
		// For now, we'll use the standard formatter
		fmt.Printf("[GIN] %s | %3d | %13v | %15s | %-7s %s %s\n",
			param.TimeStamp.Format("2006/01/02 - 15:04:05"),
			param.StatusCode,
			param.Latency,
			param.ClientIP,
			param.Method,
			param.Path,
			param.ErrorMessage,
		)
	})
}
