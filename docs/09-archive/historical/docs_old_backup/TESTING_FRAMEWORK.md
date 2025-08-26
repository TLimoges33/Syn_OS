# Syn_OS Testing Framework Documentation

* *Version**: 1.0
* *Date**: 2025-07-23
* *Purpose**: Define comprehensive testing strategy and framework for Syn_OS

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Testing Pyramid](#testing-pyramid)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [End-to-End Testing](#end-to-end-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [Test Data Management](#test-data-management)
9. [Test Automation](#test-automation)
10. [Testing Standards](#testing-standards)

## Testing Philosophy

### Core Principles

1. **Test Early, Test Often**: Shift-left testing approach
2. **Automate Everything**: Manual testing only for exploratory
3. **Fast Feedback**: Tests must run quickly
4. **Isolation**: Tests should not depend on each other
5. **Deterministic**: Same input = same output
6. **Comprehensive**: Cover happy path, edge cases, and errors

### Testing Goals

- **Code Coverage**: Minimum 80% for all components
- **Performance**: All tests complete in <30 minutes
- **Reliability**: Zero flaky tests
- **Security**: Every component security tested
- **Documentation**: Tests serve as living documentation

## Testing Pyramid

```text
         /\
        /  \  E2E Tests (5%)
       /    \  - User journeys
      /      \  - Cross-system flows
     /--------\
    /          \  Integration Tests (20%)
   /            \  - API contracts
  /              \  - Service interactions
 /----------------\
/                  \  Unit Tests (75%)
/                    \  - Business logic
/                      \  - Individual functions

- -----------------------  - Edge cases

```text

    /          \  Integration Tests (20%)
   /            \  - API contracts
  /              \  - Service interactions
 /----------------\
/                  \  Unit Tests (75%)
/                    \  - Business logic
/                      \  - Individual functions

- -----------------------  - Edge cases

```text
    /          \  Integration Tests (20%)
   /            \  - API contracts
  /              \  - Service interactions
 /----------------\
/                  \  Unit Tests (75%)
/                    \  - Business logic
/                      \  - Individual functions

- -----------------------  - Edge cases

```text
/                    \  - Business logic
/                      \  - Individual functions

- -----------------------  - Edge cases

```text

## Unit Testing

### Python Components (Pytest)

#### Test Structure

```python
#### Test Structure

```python

#### Test Structure

```python
```python

## tests/unit/test_neural_darwinism.py

import pytest
from unittest.mock import Mock, patch
from synapticos.consciousness import NeuralDarwinismEngine

class TestNeuralDarwinismEngine:
    """Test suite for Neural Darwinism Engine."""

    @pytest.fixture
    def engine(self):
        """Create engine instance for testing."""
        config = {
            "population_size": 100,
            "selection_pressure": 0.7,
            "mutation_rate": 0.1
        }
        return NeuralDarwinismEngine(config)

    @pytest.fixture
    def mock_population(self):
        """Create mock neural population."""
        population = Mock()
        population.fitness_scores = [0.5, 0.7, 0.3, 0.9, 0.6]
        return population

    def test_initialization(self, engine):
        """Test engine initializes with correct parameters."""
        assert engine.population_size == 100
        assert engine.selection_pressure == 0.7
        assert engine.mutation_rate == 0.1
        assert engine.generation == 0

    def test_selection_mechanism(self, engine, mock_population):
        """Test natural selection algorithm."""
        selected = engine.select_fittest(mock_population)

        # Should select top 70% (selection_pressure)
        assert len(selected) == 3
        assert all(ind.fitness >= 0.6 for ind in selected)

    @pytest.mark.parametrize("input_data,expected_fitness", [
        ({"complexity": 0.8}, 0.75),
        ({"complexity": 0.2}, 0.25),
        ({"complexity": 1.0}, 0.95),
    ])
    def test_fitness_calculation(self, engine, input_data, expected_fitness):
        """Test fitness calculation with various inputs."""
        fitness = engine.calculate_fitness(input_data)
        assert abs(fitness - expected_fitness) < 0.1

    def test_evolution_cycle(self, engine):
        """Test complete evolution cycle."""
        initial_fitness = engine.average_fitness

        # Run evolution for 10 generations
        for _ in range(10):
            engine.evolve()

        # Fitness should improve
        assert engine.average_fitness > initial_fitness
        assert engine.generation == 10

    @patch('synapticos.consciousness.logger')
    def test_emergence_detection(self, mock_logger, engine):
        """Test consciousness emergence detection."""
        # Simulate high coherence state
        engine.coherence_score = 0.95
        engine.complexity_score = 0.92

        emergence = engine.detect_emergence()

        assert emergence is True
        mock_logger.info.assert_called_with("Consciousness emergence detected!")

    def test_error_handling(self, engine):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            engine.process_input(None)

        with pytest.raises(TypeError):
            engine.evolve(generations="invalid")
```text

from synapticos.consciousness import NeuralDarwinismEngine

class TestNeuralDarwinismEngine:
    """Test suite for Neural Darwinism Engine."""

    @pytest.fixture
    def engine(self):
        """Create engine instance for testing."""
        config = {
            "population_size": 100,
            "selection_pressure": 0.7,
            "mutation_rate": 0.1
        }
        return NeuralDarwinismEngine(config)

    @pytest.fixture
    def mock_population(self):
        """Create mock neural population."""
        population = Mock()
        population.fitness_scores = [0.5, 0.7, 0.3, 0.9, 0.6]
        return population

    def test_initialization(self, engine):
        """Test engine initializes with correct parameters."""
        assert engine.population_size == 100
        assert engine.selection_pressure == 0.7
        assert engine.mutation_rate == 0.1
        assert engine.generation == 0

    def test_selection_mechanism(self, engine, mock_population):
        """Test natural selection algorithm."""
        selected = engine.select_fittest(mock_population)

        # Should select top 70% (selection_pressure)
        assert len(selected) == 3
        assert all(ind.fitness >= 0.6 for ind in selected)

    @pytest.mark.parametrize("input_data,expected_fitness", [
        ({"complexity": 0.8}, 0.75),
        ({"complexity": 0.2}, 0.25),
        ({"complexity": 1.0}, 0.95),
    ])
    def test_fitness_calculation(self, engine, input_data, expected_fitness):
        """Test fitness calculation with various inputs."""
        fitness = engine.calculate_fitness(input_data)
        assert abs(fitness - expected_fitness) < 0.1

    def test_evolution_cycle(self, engine):
        """Test complete evolution cycle."""
        initial_fitness = engine.average_fitness

        # Run evolution for 10 generations
        for _ in range(10):
            engine.evolve()

        # Fitness should improve
        assert engine.average_fitness > initial_fitness
        assert engine.generation == 10

    @patch('synapticos.consciousness.logger')
    def test_emergence_detection(self, mock_logger, engine):
        """Test consciousness emergence detection."""
        # Simulate high coherence state
        engine.coherence_score = 0.95
        engine.complexity_score = 0.92

        emergence = engine.detect_emergence()

        assert emergence is True
        mock_logger.info.assert_called_with("Consciousness emergence detected!")

    def test_error_handling(self, engine):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            engine.process_input(None)

        with pytest.raises(TypeError):
            engine.evolve(generations="invalid")

```text
from synapticos.consciousness import NeuralDarwinismEngine

class TestNeuralDarwinismEngine:
    """Test suite for Neural Darwinism Engine."""

    @pytest.fixture
    def engine(self):
        """Create engine instance for testing."""
        config = {
            "population_size": 100,
            "selection_pressure": 0.7,
            "mutation_rate": 0.1
        }
        return NeuralDarwinismEngine(config)

    @pytest.fixture
    def mock_population(self):
        """Create mock neural population."""
        population = Mock()
        population.fitness_scores = [0.5, 0.7, 0.3, 0.9, 0.6]
        return population

    def test_initialization(self, engine):
        """Test engine initializes with correct parameters."""
        assert engine.population_size == 100
        assert engine.selection_pressure == 0.7
        assert engine.mutation_rate == 0.1
        assert engine.generation == 0

    def test_selection_mechanism(self, engine, mock_population):
        """Test natural selection algorithm."""
        selected = engine.select_fittest(mock_population)

        # Should select top 70% (selection_pressure)
        assert len(selected) == 3
        assert all(ind.fitness >= 0.6 for ind in selected)

    @pytest.mark.parametrize("input_data,expected_fitness", [
        ({"complexity": 0.8}, 0.75),
        ({"complexity": 0.2}, 0.25),
        ({"complexity": 1.0}, 0.95),
    ])
    def test_fitness_calculation(self, engine, input_data, expected_fitness):
        """Test fitness calculation with various inputs."""
        fitness = engine.calculate_fitness(input_data)
        assert abs(fitness - expected_fitness) < 0.1

    def test_evolution_cycle(self, engine):
        """Test complete evolution cycle."""
        initial_fitness = engine.average_fitness

        # Run evolution for 10 generations
        for _ in range(10):
            engine.evolve()

        # Fitness should improve
        assert engine.average_fitness > initial_fitness
        assert engine.generation == 10

    @patch('synapticos.consciousness.logger')
    def test_emergence_detection(self, mock_logger, engine):
        """Test consciousness emergence detection."""
        # Simulate high coherence state
        engine.coherence_score = 0.95
        engine.complexity_score = 0.92

        emergence = engine.detect_emergence()

        assert emergence is True
        mock_logger.info.assert_called_with("Consciousness emergence detected!")

    def test_error_handling(self, engine):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            engine.process_input(None)

        with pytest.raises(TypeError):
            engine.evolve(generations="invalid")

```text
    @pytest.fixture
    def engine(self):
        """Create engine instance for testing."""
        config = {
            "population_size": 100,
            "selection_pressure": 0.7,
            "mutation_rate": 0.1
        }
        return NeuralDarwinismEngine(config)

    @pytest.fixture
    def mock_population(self):
        """Create mock neural population."""
        population = Mock()
        population.fitness_scores = [0.5, 0.7, 0.3, 0.9, 0.6]
        return population

    def test_initialization(self, engine):
        """Test engine initializes with correct parameters."""
        assert engine.population_size == 100
        assert engine.selection_pressure == 0.7
        assert engine.mutation_rate == 0.1
        assert engine.generation == 0

    def test_selection_mechanism(self, engine, mock_population):
        """Test natural selection algorithm."""
        selected = engine.select_fittest(mock_population)

        # Should select top 70% (selection_pressure)
        assert len(selected) == 3
        assert all(ind.fitness >= 0.6 for ind in selected)

    @pytest.mark.parametrize("input_data,expected_fitness", [
        ({"complexity": 0.8}, 0.75),
        ({"complexity": 0.2}, 0.25),
        ({"complexity": 1.0}, 0.95),
    ])
    def test_fitness_calculation(self, engine, input_data, expected_fitness):
        """Test fitness calculation with various inputs."""
        fitness = engine.calculate_fitness(input_data)
        assert abs(fitness - expected_fitness) < 0.1

    def test_evolution_cycle(self, engine):
        """Test complete evolution cycle."""
        initial_fitness = engine.average_fitness

        # Run evolution for 10 generations
        for _ in range(10):
            engine.evolve()

        # Fitness should improve
        assert engine.average_fitness > initial_fitness
        assert engine.generation == 10

    @patch('synapticos.consciousness.logger')
    def test_emergence_detection(self, mock_logger, engine):
        """Test consciousness emergence detection."""
        # Simulate high coherence state
        engine.coherence_score = 0.95
        engine.complexity_score = 0.92

        emergence = engine.detect_emergence()

        assert emergence is True
        mock_logger.info.assert_called_with("Consciousness emergence detected!")

    def test_error_handling(self, engine):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            engine.process_input(None)

        with pytest.raises(TypeError):
            engine.evolve(generations="invalid")

```text

#### Coverage Configuration

```ini

```ini
```ini

```ini

## .coveragerc

[run]
source = synapticos-overlay
omit =

    * /tests/*
    * /migrations/*
    * /__pycache__/*
    * /venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov

[xml]
output = coverage.xml
```text

omit =

    * /tests/*
    * /migrations/*
    * /__pycache__/*
    * /venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov

[xml]
output = coverage.xml

```text
omit =

    * /tests/*
    * /migrations/*
    * /__pycache__/*
    * /venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov

[xml]
output = coverage.xml

```text
    * /venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov

[xml]
output = coverage.xml

```text

### Go Components (Testing Package)

#### Test Structure

```go
```go

```go

```go
// orchestrator/internal/core/orchestrator_test.go
package core

import (
    "context"
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/suite"
)

// Mock dependencies
type MockDocker struct {
    mock.Mock
}

func (m *MockDocker) StartContainer(ctx context.Context, id string) error {
    args := m.Called(ctx, id)
    return args.Error(0)
}

// Test suite
type OrchestratorTestSuite struct {
    suite.Suite
    orchestrator *Orchestrator
    mockDocker   *MockDocker
}

func (suite *OrchestratorTestSuite) SetupTest() {
    suite.mockDocker = new(MockDocker)
    suite.orchestrator = NewOrchestrator(
        WithDocker(suite.mockDocker),
        WithTimeout(5 * time.Second),
    )
}

func (suite *OrchestratorTestSuite) TestServiceRegistration() {
    // Arrange
    service := ServiceConfig{
        Name:  "test-service",
        Image: "test:latest",
        Type:  ContainerService,
    }

    // Act
    err := suite.orchestrator.RegisterService(service)

    // Assert
    assert.NoError(suite.T(), err)
    assert.Contains(suite.T(), suite.orchestrator.services, "test-service")
}

func (suite *OrchestratorTestSuite) TestServiceStart() {
    // Arrange
    ctx := context.Background()
    serviceName := "test-service"

    suite.orchestrator.services[serviceName] = &Service{
        Config: ServiceConfig{Name: serviceName},
        Status: StatusStopped,
    }

    suite.mockDocker.On("StartContainer", ctx, mock.Anything).Return(nil)

    // Act
    err := suite.orchestrator.StartService(ctx, serviceName)

    // Assert
    assert.NoError(suite.T(), err)
    assert.Equal(suite.T(), StatusRunning, suite.orchestrator.services[serviceName].Status)
    suite.mockDocker.AssertExpectations(suite.T())
}

func (suite *OrchestratorTestSuite) TestConcurrentServiceStarts() {
    // Test concurrent access
    services := []string{"svc1", "svc2", "svc3"}

    for _, svc := range services {
        suite.orchestrator.RegisterService(ServiceConfig{Name: svc})
    }

    // Start services concurrently
    errChan := make(chan error, len(services))

    for _, svc := range services {
        go func(name string) {
            errChan <- suite.orchestrator.StartService(context.Background(), name)
        }(svc)
    }

    // Verify no errors
    for range services {
        assert.NoError(suite.T(), <-errChan)
    }
}

// Benchmark tests
func BenchmarkServiceRegistration(b *testing.B) {
    orch := NewOrchestrator()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        orch.RegisterService(ServiceConfig{
            Name: fmt.Sprintf("service-%d", i),
        })
    }
}

func TestOrchestratorSuite(t *testing.T) {
    suite.Run(t, new(OrchestratorTestSuite))
}
```text

    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/suite"
)

// Mock dependencies
type MockDocker struct {
    mock.Mock
}

func (m *MockDocker) StartContainer(ctx context.Context, id string) error {
    args := m.Called(ctx, id)
    return args.Error(0)
}

// Test suite
type OrchestratorTestSuite struct {
    suite.Suite
    orchestrator *Orchestrator
    mockDocker   *MockDocker
}

func (suite *OrchestratorTestSuite) SetupTest() {
    suite.mockDocker = new(MockDocker)
    suite.orchestrator = NewOrchestrator(
        WithDocker(suite.mockDocker),
        WithTimeout(5 * time.Second),
    )
}

func (suite *OrchestratorTestSuite) TestServiceRegistration() {
    // Arrange
    service := ServiceConfig{
        Name:  "test-service",
        Image: "test:latest",
        Type:  ContainerService,
    }

    // Act
    err := suite.orchestrator.RegisterService(service)

    // Assert
    assert.NoError(suite.T(), err)
    assert.Contains(suite.T(), suite.orchestrator.services, "test-service")
}

func (suite *OrchestratorTestSuite) TestServiceStart() {
    // Arrange
    ctx := context.Background()
    serviceName := "test-service"

    suite.orchestrator.services[serviceName] = &Service{
        Config: ServiceConfig{Name: serviceName},
        Status: StatusStopped,
    }

    suite.mockDocker.On("StartContainer", ctx, mock.Anything).Return(nil)

    // Act
    err := suite.orchestrator.StartService(ctx, serviceName)

    // Assert
    assert.NoError(suite.T(), err)
    assert.Equal(suite.T(), StatusRunning, suite.orchestrator.services[serviceName].Status)
    suite.mockDocker.AssertExpectations(suite.T())
}

func (suite *OrchestratorTestSuite) TestConcurrentServiceStarts() {
    // Test concurrent access
    services := []string{"svc1", "svc2", "svc3"}

    for _, svc := range services {
        suite.orchestrator.RegisterService(ServiceConfig{Name: svc})
    }

    // Start services concurrently
    errChan := make(chan error, len(services))

    for _, svc := range services {
        go func(name string) {
            errChan <- suite.orchestrator.StartService(context.Background(), name)
        }(svc)
    }

    // Verify no errors
    for range services {
        assert.NoError(suite.T(), <-errChan)
    }
}

// Benchmark tests
func BenchmarkServiceRegistration(b *testing.B) {
    orch := NewOrchestrator()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        orch.RegisterService(ServiceConfig{
            Name: fmt.Sprintf("service-%d", i),
        })
    }
}

func TestOrchestratorSuite(t *testing.T) {
    suite.Run(t, new(OrchestratorTestSuite))
}

```text
    "testing"
    "time"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"
    "github.com/stretchr/testify/suite"
)

// Mock dependencies
type MockDocker struct {
    mock.Mock
}

func (m *MockDocker) StartContainer(ctx context.Context, id string) error {
    args := m.Called(ctx, id)
    return args.Error(0)
}

// Test suite
type OrchestratorTestSuite struct {
    suite.Suite
    orchestrator *Orchestrator
    mockDocker   *MockDocker
}

func (suite *OrchestratorTestSuite) SetupTest() {
    suite.mockDocker = new(MockDocker)
    suite.orchestrator = NewOrchestrator(
        WithDocker(suite.mockDocker),
        WithTimeout(5 * time.Second),
    )
}

func (suite *OrchestratorTestSuite) TestServiceRegistration() {
    // Arrange
    service := ServiceConfig{
        Name:  "test-service",
        Image: "test:latest",
        Type:  ContainerService,
    }

    // Act
    err := suite.orchestrator.RegisterService(service)

    // Assert
    assert.NoError(suite.T(), err)
    assert.Contains(suite.T(), suite.orchestrator.services, "test-service")
}

func (suite *OrchestratorTestSuite) TestServiceStart() {
    // Arrange
    ctx := context.Background()
    serviceName := "test-service"

    suite.orchestrator.services[serviceName] = &Service{
        Config: ServiceConfig{Name: serviceName},
        Status: StatusStopped,
    }

    suite.mockDocker.On("StartContainer", ctx, mock.Anything).Return(nil)

    // Act
    err := suite.orchestrator.StartService(ctx, serviceName)

    // Assert
    assert.NoError(suite.T(), err)
    assert.Equal(suite.T(), StatusRunning, suite.orchestrator.services[serviceName].Status)
    suite.mockDocker.AssertExpectations(suite.T())
}

func (suite *OrchestratorTestSuite) TestConcurrentServiceStarts() {
    // Test concurrent access
    services := []string{"svc1", "svc2", "svc3"}

    for _, svc := range services {
        suite.orchestrator.RegisterService(ServiceConfig{Name: svc})
    }

    // Start services concurrently
    errChan := make(chan error, len(services))

    for _, svc := range services {
        go func(name string) {
            errChan <- suite.orchestrator.StartService(context.Background(), name)
        }(svc)
    }

    // Verify no errors
    for range services {
        assert.NoError(suite.T(), <-errChan)
    }
}

// Benchmark tests
func BenchmarkServiceRegistration(b *testing.B) {
    orch := NewOrchestrator()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        orch.RegisterService(ServiceConfig{
            Name: fmt.Sprintf("service-%d", i),
        })
    }
}

func TestOrchestratorSuite(t *testing.T) {
    suite.Run(t, new(OrchestratorTestSuite))
}

```text
    "github.com/stretchr/testify/suite"
)

// Mock dependencies
type MockDocker struct {
    mock.Mock
}

func (m *MockDocker) StartContainer(ctx context.Context, id string) error {
    args := m.Called(ctx, id)
    return args.Error(0)
}

// Test suite
type OrchestratorTestSuite struct {
    suite.Suite
    orchestrator *Orchestrator
    mockDocker   *MockDocker
}

func (suite *OrchestratorTestSuite) SetupTest() {
    suite.mockDocker = new(MockDocker)
    suite.orchestrator = NewOrchestrator(
        WithDocker(suite.mockDocker),
        WithTimeout(5 * time.Second),
    )
}

func (suite *OrchestratorTestSuite) TestServiceRegistration() {
    // Arrange
    service := ServiceConfig{
        Name:  "test-service",
        Image: "test:latest",
        Type:  ContainerService,
    }

    // Act
    err := suite.orchestrator.RegisterService(service)

    // Assert
    assert.NoError(suite.T(), err)
    assert.Contains(suite.T(), suite.orchestrator.services, "test-service")
}

func (suite *OrchestratorTestSuite) TestServiceStart() {
    // Arrange
    ctx := context.Background()
    serviceName := "test-service"

    suite.orchestrator.services[serviceName] = &Service{
        Config: ServiceConfig{Name: serviceName},
        Status: StatusStopped,
    }

    suite.mockDocker.On("StartContainer", ctx, mock.Anything).Return(nil)

    // Act
    err := suite.orchestrator.StartService(ctx, serviceName)

    // Assert
    assert.NoError(suite.T(), err)
    assert.Equal(suite.T(), StatusRunning, suite.orchestrator.services[serviceName].Status)
    suite.mockDocker.AssertExpectations(suite.T())
}

func (suite *OrchestratorTestSuite) TestConcurrentServiceStarts() {
    // Test concurrent access
    services := []string{"svc1", "svc2", "svc3"}

    for _, svc := range services {
        suite.orchestrator.RegisterService(ServiceConfig{Name: svc})
    }

    // Start services concurrently
    errChan := make(chan error, len(services))

    for _, svc := range services {
        go func(name string) {
            errChan <- suite.orchestrator.StartService(context.Background(), name)
        }(svc)
    }

    // Verify no errors
    for range services {
        assert.NoError(suite.T(), <-errChan)
    }
}

// Benchmark tests
func BenchmarkServiceRegistration(b *testing.B) {
    orch := NewOrchestrator()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        orch.RegisterService(ServiceConfig{
            Name: fmt.Sprintf("service-%d", i),
        })
    }
}

func TestOrchestratorSuite(t *testing.T) {
    suite.Run(t, new(OrchestratorTestSuite))
}

```text

### Rust Components (Cargo Test)

#### Test Structure

```rust
```rust

```rust

```rust
// security/src/auth/mod.rs
#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::*;
    use tokio::test;

    // Mock trait for testing
    mockall::mock! {
        pub TokenStore {}

        #[async_trait]
        impl TokenStore for TokenStore {
            async fn store(&self, token: &str, claims: Claims) -> Result<(), Error>;
            async fn retrieve(&self, token: &str) -> Result<Option<Claims>, Error>;
            async fn revoke(&self, token: &str) -> Result<(), Error>;
        }
    }

    #[test]
    async fn test_jwt_generation() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let user_id = "user123";
        let roles = vec!["user".to_string(), "admin".to_string()];

        // Act
        let token = auth.generate_token(user_id, roles.clone()).await.unwrap();

        // Assert
        assert!(!token.is_empty());
        assert!(token.starts_with("eyJ"));
    }

    #[test]
    async fn test_token_validation() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let token = auth.generate_token("user123", vec!["user".to_string()]).await.unwrap();

        // Act
        let claims = auth.validate_token(&token).await.unwrap();

        // Assert
        assert_eq!(claims.sub, "user123");
        assert_eq!(claims.roles, vec!["user"]);
    }

    #[test]
    async fn test_expired_token_rejection() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let expired_token = generate_expired_token();

        // Act
        let result = auth.validate_token(&expired_token).await;

        // Assert
        assert!(matches!(result, Err(AuthError::TokenExpired)));
    }

    #[test]
    async fn test_concurrent_token_validation() {
        let auth = Arc::new(JwtAuthenticator::new("secret_key"));
        let token = auth.generate_token("user123", vec!["user".to_string()]).await.unwrap();

        // Spawn multiple validation tasks
        let mut handles = vec![];

        for _ in 0..100 {
            let auth_clone = auth.clone();
            let token_clone = token.clone();

            handles.push(tokio::spawn(async move {
                auth_clone.validate_token(&token_clone).await
            }));
        }

        // All should succeed
        for handle in handles {
            assert!(handle.await.unwrap().is_ok());
        }
    }

    #[test]
    #[should_panic(expected = "Secret key cannot be empty")]
    fn test_empty_secret_key_panic() {
        JwtAuthenticator::new("");
    }
}
```text

    use tokio::test;

    // Mock trait for testing
    mockall::mock! {
        pub TokenStore {}

        #[async_trait]
        impl TokenStore for TokenStore {
            async fn store(&self, token: &str, claims: Claims) -> Result<(), Error>;
            async fn retrieve(&self, token: &str) -> Result<Option<Claims>, Error>;
            async fn revoke(&self, token: &str) -> Result<(), Error>;
        }
    }

    #[test]
    async fn test_jwt_generation() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let user_id = "user123";
        let roles = vec!["user".to_string(), "admin".to_string()];

        // Act
        let token = auth.generate_token(user_id, roles.clone()).await.unwrap();

        // Assert
        assert!(!token.is_empty());
        assert!(token.starts_with("eyJ"));
    }

    #[test]
    async fn test_token_validation() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let token = auth.generate_token("user123", vec!["user".to_string()]).await.unwrap();

        // Act
        let claims = auth.validate_token(&token).await.unwrap();

        // Assert
        assert_eq!(claims.sub, "user123");
        assert_eq!(claims.roles, vec!["user"]);
    }

    #[test]
    async fn test_expired_token_rejection() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let expired_token = generate_expired_token();

        // Act
        let result = auth.validate_token(&expired_token).await;

        // Assert
        assert!(matches!(result, Err(AuthError::TokenExpired)));
    }

    #[test]
    async fn test_concurrent_token_validation() {
        let auth = Arc::new(JwtAuthenticator::new("secret_key"));
        let token = auth.generate_token("user123", vec!["user".to_string()]).await.unwrap();

        // Spawn multiple validation tasks
        let mut handles = vec![];

        for _ in 0..100 {
            let auth_clone = auth.clone();
            let token_clone = token.clone();

            handles.push(tokio::spawn(async move {
                auth_clone.validate_token(&token_clone).await
            }));
        }

        // All should succeed
        for handle in handles {
            assert!(handle.await.unwrap().is_ok());
        }
    }

    #[test]
    #[should_panic(expected = "Secret key cannot be empty")]
    fn test_empty_secret_key_panic() {
        JwtAuthenticator::new("");
    }
}

```text
    use tokio::test;

    // Mock trait for testing
    mockall::mock! {
        pub TokenStore {}

        #[async_trait]
        impl TokenStore for TokenStore {
            async fn store(&self, token: &str, claims: Claims) -> Result<(), Error>;
            async fn retrieve(&self, token: &str) -> Result<Option<Claims>, Error>;
            async fn revoke(&self, token: &str) -> Result<(), Error>;
        }
    }

    #[test]
    async fn test_jwt_generation() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let user_id = "user123";
        let roles = vec!["user".to_string(), "admin".to_string()];

        // Act
        let token = auth.generate_token(user_id, roles.clone()).await.unwrap();

        // Assert
        assert!(!token.is_empty());
        assert!(token.starts_with("eyJ"));
    }

    #[test]
    async fn test_token_validation() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let token = auth.generate_token("user123", vec!["user".to_string()]).await.unwrap();

        // Act
        let claims = auth.validate_token(&token).await.unwrap();

        // Assert
        assert_eq!(claims.sub, "user123");
        assert_eq!(claims.roles, vec!["user"]);
    }

    #[test]
    async fn test_expired_token_rejection() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let expired_token = generate_expired_token();

        // Act
        let result = auth.validate_token(&expired_token).await;

        // Assert
        assert!(matches!(result, Err(AuthError::TokenExpired)));
    }

    #[test]
    async fn test_concurrent_token_validation() {
        let auth = Arc::new(JwtAuthenticator::new("secret_key"));
        let token = auth.generate_token("user123", vec!["user".to_string()]).await.unwrap();

        // Spawn multiple validation tasks
        let mut handles = vec![];

        for _ in 0..100 {
            let auth_clone = auth.clone();
            let token_clone = token.clone();

            handles.push(tokio::spawn(async move {
                auth_clone.validate_token(&token_clone).await
            }));
        }

        // All should succeed
        for handle in handles {
            assert!(handle.await.unwrap().is_ok());
        }
    }

    #[test]
    #[should_panic(expected = "Secret key cannot be empty")]
    fn test_empty_secret_key_panic() {
        JwtAuthenticator::new("");
    }
}

```text

        #[async_trait]
        impl TokenStore for TokenStore {
            async fn store(&self, token: &str, claims: Claims) -> Result<(), Error>;
            async fn retrieve(&self, token: &str) -> Result<Option<Claims>, Error>;
            async fn revoke(&self, token: &str) -> Result<(), Error>;
        }
    }

    #[test]
    async fn test_jwt_generation() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let user_id = "user123";
        let roles = vec!["user".to_string(), "admin".to_string()];

        // Act
        let token = auth.generate_token(user_id, roles.clone()).await.unwrap();

        // Assert
        assert!(!token.is_empty());
        assert!(token.starts_with("eyJ"));
    }

    #[test]
    async fn test_token_validation() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let token = auth.generate_token("user123", vec!["user".to_string()]).await.unwrap();

        // Act
        let claims = auth.validate_token(&token).await.unwrap();

        // Assert
        assert_eq!(claims.sub, "user123");
        assert_eq!(claims.roles, vec!["user"]);
    }

    #[test]
    async fn test_expired_token_rejection() {
        // Arrange
        let auth = JwtAuthenticator::new("secret_key");
        let expired_token = generate_expired_token();

        // Act
        let result = auth.validate_token(&expired_token).await;

        // Assert
        assert!(matches!(result, Err(AuthError::TokenExpired)));
    }

    #[test]
    async fn test_concurrent_token_validation() {
        let auth = Arc::new(JwtAuthenticator::new("secret_key"));
        let token = auth.generate_token("user123", vec!["user".to_string()]).await.unwrap();

        // Spawn multiple validation tasks
        let mut handles = vec![];

        for _ in 0..100 {
            let auth_clone = auth.clone();
            let token_clone = token.clone();

            handles.push(tokio::spawn(async move {
                auth_clone.validate_token(&token_clone).await
            }));
        }

        // All should succeed
        for handle in handles {
            assert!(handle.await.unwrap().is_ok());
        }
    }

    #[test]
    #[should_panic(expected = "Secret key cannot be empty")]
    fn test_empty_secret_key_panic() {
        JwtAuthenticator::new("");
    }
}

```text

## Integration Testing

### API Integration Tests

```python

```python
```python

```python

## tests/integration/test_api_integration.py

import pytest
import asyncio
import aiohttp
from testcontainers.compose import DockerCompose

class TestAPIIntegration:
    """Test API integration between services."""

    @pytest.fixture(scope="class")
    def docker_compose(self):
        """Start all services using docker-compose."""
        with DockerCompose(".", compose_file_name="docker-compose.test.yml") as compose:
            # Wait for services to be ready
            compose.wait_for("http://localhost:8080/health")
            compose.wait_for("http://localhost:8081/health")
            compose.wait_for("http://localhost:8082/health")
            yield compose

    @pytest.mark.asyncio
    async def test_authentication_flow(self, docker_compose):
        """Test complete authentication flow."""
        async with aiohttp.ClientSession() as session:
            # 1. Login to get token
            login_data = {"username": "test_user", "password": "test_pass"}
            async with session.post(
                "http://localhost:8081/api/v1/auth/login",
                json=login_data
            ) as resp:
                assert resp.status == 200
                token_data = await resp.json()
                token = token_data["access_token"]

            # 2. Use token to access protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            async with session.get(
                "http://localhost:8082/api/v1/consciousness/state",
                headers=headers
            ) as resp:
                assert resp.status == 200
                state = await resp.json()
                assert "active_populations" in state

    @pytest.mark.asyncio
    async def test_service_orchestration(self, docker_compose):
        """Test service orchestration workflow."""
        async with aiohttp.ClientSession() as session:
            # Register a new service
            service_config = {
                "name": "test-ai-service",
                "type": "container",
                "config": {
                    "image": "synos/test:latest",
                    "environment": {"LOG_LEVEL": "debug"}
                }
            }

            async with session.post(
                "http://localhost:8080/api/v1/services",
                json=service_config
            ) as resp:
                assert resp.status == 201
                service_data = await resp.json()
                service_id = service_data["service_id"]

            # Start the service
            async with session.post(
                f"http://localhost:8080/api/v1/services/{service_id}/start"
            ) as resp:
                assert resp.status == 200

            # Wait for service to be healthy
            await asyncio.sleep(5)

            # Check service status
            async with session.get(
                f"http://localhost:8080/api/v1/services/{service_id}/status"
            ) as resp:
                assert resp.status == 200
                status = await resp.json()
                assert status["status"] == "running"
                assert status["health"] == "healthy"
```text

import aiohttp
from testcontainers.compose import DockerCompose

class TestAPIIntegration:
    """Test API integration between services."""

    @pytest.fixture(scope="class")
    def docker_compose(self):
        """Start all services using docker-compose."""
        with DockerCompose(".", compose_file_name="docker-compose.test.yml") as compose:
            # Wait for services to be ready
            compose.wait_for("http://localhost:8080/health")
            compose.wait_for("http://localhost:8081/health")
            compose.wait_for("http://localhost:8082/health")
            yield compose

    @pytest.mark.asyncio
    async def test_authentication_flow(self, docker_compose):
        """Test complete authentication flow."""
        async with aiohttp.ClientSession() as session:
            # 1. Login to get token
            login_data = {"username": "test_user", "password": "test_pass"}
            async with session.post(
                "http://localhost:8081/api/v1/auth/login",
                json=login_data
            ) as resp:
                assert resp.status == 200
                token_data = await resp.json()
                token = token_data["access_token"]

            # 2. Use token to access protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            async with session.get(
                "http://localhost:8082/api/v1/consciousness/state",
                headers=headers
            ) as resp:
                assert resp.status == 200
                state = await resp.json()
                assert "active_populations" in state

    @pytest.mark.asyncio
    async def test_service_orchestration(self, docker_compose):
        """Test service orchestration workflow."""
        async with aiohttp.ClientSession() as session:
            # Register a new service
            service_config = {
                "name": "test-ai-service",
                "type": "container",
                "config": {
                    "image": "synos/test:latest",
                    "environment": {"LOG_LEVEL": "debug"}
                }
            }

            async with session.post(
                "http://localhost:8080/api/v1/services",
                json=service_config
            ) as resp:
                assert resp.status == 201
                service_data = await resp.json()
                service_id = service_data["service_id"]

            # Start the service
            async with session.post(
                f"http://localhost:8080/api/v1/services/{service_id}/start"
            ) as resp:
                assert resp.status == 200

            # Wait for service to be healthy
            await asyncio.sleep(5)

            # Check service status
            async with session.get(
                f"http://localhost:8080/api/v1/services/{service_id}/status"
            ) as resp:
                assert resp.status == 200
                status = await resp.json()
                assert status["status"] == "running"
                assert status["health"] == "healthy"

```text
import aiohttp
from testcontainers.compose import DockerCompose

class TestAPIIntegration:
    """Test API integration between services."""

    @pytest.fixture(scope="class")
    def docker_compose(self):
        """Start all services using docker-compose."""
        with DockerCompose(".", compose_file_name="docker-compose.test.yml") as compose:
            # Wait for services to be ready
            compose.wait_for("http://localhost:8080/health")
            compose.wait_for("http://localhost:8081/health")
            compose.wait_for("http://localhost:8082/health")
            yield compose

    @pytest.mark.asyncio
    async def test_authentication_flow(self, docker_compose):
        """Test complete authentication flow."""
        async with aiohttp.ClientSession() as session:
            # 1. Login to get token
            login_data = {"username": "test_user", "password": "test_pass"}
            async with session.post(
                "http://localhost:8081/api/v1/auth/login",
                json=login_data
            ) as resp:
                assert resp.status == 200
                token_data = await resp.json()
                token = token_data["access_token"]

            # 2. Use token to access protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            async with session.get(
                "http://localhost:8082/api/v1/consciousness/state",
                headers=headers
            ) as resp:
                assert resp.status == 200
                state = await resp.json()
                assert "active_populations" in state

    @pytest.mark.asyncio
    async def test_service_orchestration(self, docker_compose):
        """Test service orchestration workflow."""
        async with aiohttp.ClientSession() as session:
            # Register a new service
            service_config = {
                "name": "test-ai-service",
                "type": "container",
                "config": {
                    "image": "synos/test:latest",
                    "environment": {"LOG_LEVEL": "debug"}
                }
            }

            async with session.post(
                "http://localhost:8080/api/v1/services",
                json=service_config
            ) as resp:
                assert resp.status == 201
                service_data = await resp.json()
                service_id = service_data["service_id"]

            # Start the service
            async with session.post(
                f"http://localhost:8080/api/v1/services/{service_id}/start"
            ) as resp:
                assert resp.status == 200

            # Wait for service to be healthy
            await asyncio.sleep(5)

            # Check service status
            async with session.get(
                f"http://localhost:8080/api/v1/services/{service_id}/status"
            ) as resp:
                assert resp.status == 200
                status = await resp.json()
                assert status["status"] == "running"
                assert status["health"] == "healthy"

```text

    @pytest.fixture(scope="class")
    def docker_compose(self):
        """Start all services using docker-compose."""
        with DockerCompose(".", compose_file_name="docker-compose.test.yml") as compose:
            # Wait for services to be ready
            compose.wait_for("http://localhost:8080/health")
            compose.wait_for("http://localhost:8081/health")
            compose.wait_for("http://localhost:8082/health")
            yield compose

    @pytest.mark.asyncio
    async def test_authentication_flow(self, docker_compose):
        """Test complete authentication flow."""
        async with aiohttp.ClientSession() as session:
            # 1. Login to get token
            login_data = {"username": "test_user", "password": "test_pass"}
            async with session.post(
                "http://localhost:8081/api/v1/auth/login",
                json=login_data
            ) as resp:
                assert resp.status == 200
                token_data = await resp.json()
                token = token_data["access_token"]

            # 2. Use token to access protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            async with session.get(
                "http://localhost:8082/api/v1/consciousness/state",
                headers=headers
            ) as resp:
                assert resp.status == 200
                state = await resp.json()
                assert "active_populations" in state

    @pytest.mark.asyncio
    async def test_service_orchestration(self, docker_compose):
        """Test service orchestration workflow."""
        async with aiohttp.ClientSession() as session:
            # Register a new service
            service_config = {
                "name": "test-ai-service",
                "type": "container",
                "config": {
                    "image": "synos/test:latest",
                    "environment": {"LOG_LEVEL": "debug"}
                }
            }

            async with session.post(
                "http://localhost:8080/api/v1/services",
                json=service_config
            ) as resp:
                assert resp.status == 201
                service_data = await resp.json()
                service_id = service_data["service_id"]

            # Start the service
            async with session.post(
                f"http://localhost:8080/api/v1/services/{service_id}/start"
            ) as resp:
                assert resp.status == 200

            # Wait for service to be healthy
            await asyncio.sleep(5)

            # Check service status
            async with session.get(
                f"http://localhost:8080/api/v1/services/{service_id}/status"
            ) as resp:
                assert resp.status == 200
                status = await resp.json()
                assert status["status"] == "running"
                assert status["health"] == "healthy"

```text

### Message Bus Integration Tests

```python

```python
```python

```python

## tests/integration/test_message_bus.py

import pytest
import asyncio
from nats.aio.client import Client as NATS

class TestMessageBusIntegration:
    """Test message bus integration."""

    @pytest.fixture
    async def nats_client(self):
        """Create NATS client."""
        nc = NATS()
        await nc.connect("nats://localhost:4222")
        yield nc
        await nc.close()

    @pytest.mark.asyncio
    async def test_service_event_flow(self, nats_client):
        """Test service event publishing and subscription."""
        received_events = []

        # Subscribe to service events
        async def message_handler(msg):
            event = json.loads(msg.data.decode())
            received_events.append(event)

        await nats_client.subscribe("events.service.*", cb=message_handler)

        # Publish test events
        events = [
            {"event_type": "service.started", "service": "test1"},
            {"event_type": "service.stopped", "service": "test2"},
            {"event_type": "service.failed", "service": "test3"},
        ]

        for event in events:
            await nats_client.publish(
                f"events.{event['event_type']}",
                json.dumps(event).encode()
            )

        # Wait for messages
        await asyncio.sleep(1)

        # Verify all events received
        assert len(received_events) == 3
        assert all(e["event_type"] in [ev["event_type"] for ev in events]
                  for e in received_events)

    @pytest.mark.asyncio
    async def test_request_reply_pattern(self, nats_client):
        """Test request-reply communication pattern."""
        # Set up responder
        async def responder(msg):
            request = json.loads(msg.data.decode())
            response = {"result": request["value"] * 2}
            await nats_client.publish(msg.reply, json.dumps(response).encode())

        await nats_client.subscribe("compute.double", cb=responder)

        # Send request
        request = {"value": 21}
        response = await nats_client.request(
            "compute.double",
            json.dumps(request).encode(),
            timeout=2
        )

        # Verify response
        result = json.loads(response.data.decode())
        assert result["result"] == 42
```text

from nats.aio.client import Client as NATS

class TestMessageBusIntegration:
    """Test message bus integration."""

    @pytest.fixture
    async def nats_client(self):
        """Create NATS client."""
        nc = NATS()
        await nc.connect("nats://localhost:4222")
        yield nc
        await nc.close()

    @pytest.mark.asyncio
    async def test_service_event_flow(self, nats_client):
        """Test service event publishing and subscription."""
        received_events = []

        # Subscribe to service events
        async def message_handler(msg):
            event = json.loads(msg.data.decode())
            received_events.append(event)

        await nats_client.subscribe("events.service.*", cb=message_handler)

        # Publish test events
        events = [
            {"event_type": "service.started", "service": "test1"},
            {"event_type": "service.stopped", "service": "test2"},
            {"event_type": "service.failed", "service": "test3"},
        ]

        for event in events:
            await nats_client.publish(
                f"events.{event['event_type']}",
                json.dumps(event).encode()
            )

        # Wait for messages
        await asyncio.sleep(1)

        # Verify all events received
        assert len(received_events) == 3
        assert all(e["event_type"] in [ev["event_type"] for ev in events]
                  for e in received_events)

    @pytest.mark.asyncio
    async def test_request_reply_pattern(self, nats_client):
        """Test request-reply communication pattern."""
        # Set up responder
        async def responder(msg):
            request = json.loads(msg.data.decode())
            response = {"result": request["value"] * 2}
            await nats_client.publish(msg.reply, json.dumps(response).encode())

        await nats_client.subscribe("compute.double", cb=responder)

        # Send request
        request = {"value": 21}
        response = await nats_client.request(
            "compute.double",
            json.dumps(request).encode(),
            timeout=2
        )

        # Verify response
        result = json.loads(response.data.decode())
        assert result["result"] == 42

```text
from nats.aio.client import Client as NATS

class TestMessageBusIntegration:
    """Test message bus integration."""

    @pytest.fixture
    async def nats_client(self):
        """Create NATS client."""
        nc = NATS()
        await nc.connect("nats://localhost:4222")
        yield nc
        await nc.close()

    @pytest.mark.asyncio
    async def test_service_event_flow(self, nats_client):
        """Test service event publishing and subscription."""
        received_events = []

        # Subscribe to service events
        async def message_handler(msg):
            event = json.loads(msg.data.decode())
            received_events.append(event)

        await nats_client.subscribe("events.service.*", cb=message_handler)

        # Publish test events
        events = [
            {"event_type": "service.started", "service": "test1"},
            {"event_type": "service.stopped", "service": "test2"},
            {"event_type": "service.failed", "service": "test3"},
        ]

        for event in events:
            await nats_client.publish(
                f"events.{event['event_type']}",
                json.dumps(event).encode()
            )

        # Wait for messages
        await asyncio.sleep(1)

        # Verify all events received
        assert len(received_events) == 3
        assert all(e["event_type"] in [ev["event_type"] for ev in events]
                  for e in received_events)

    @pytest.mark.asyncio
    async def test_request_reply_pattern(self, nats_client):
        """Test request-reply communication pattern."""
        # Set up responder
        async def responder(msg):
            request = json.loads(msg.data.decode())
            response = {"result": request["value"] * 2}
            await nats_client.publish(msg.reply, json.dumps(response).encode())

        await nats_client.subscribe("compute.double", cb=responder)

        # Send request
        request = {"value": 21}
        response = await nats_client.request(
            "compute.double",
            json.dumps(request).encode(),
            timeout=2
        )

        # Verify response
        result = json.loads(response.data.decode())
        assert result["result"] == 42

```text
    @pytest.fixture
    async def nats_client(self):
        """Create NATS client."""
        nc = NATS()
        await nc.connect("nats://localhost:4222")
        yield nc
        await nc.close()

    @pytest.mark.asyncio
    async def test_service_event_flow(self, nats_client):
        """Test service event publishing and subscription."""
        received_events = []

        # Subscribe to service events
        async def message_handler(msg):
            event = json.loads(msg.data.decode())
            received_events.append(event)

        await nats_client.subscribe("events.service.*", cb=message_handler)

        # Publish test events
        events = [
            {"event_type": "service.started", "service": "test1"},
            {"event_type": "service.stopped", "service": "test2"},
            {"event_type": "service.failed", "service": "test3"},
        ]

        for event in events:
            await nats_client.publish(
                f"events.{event['event_type']}",
                json.dumps(event).encode()
            )

        # Wait for messages
        await asyncio.sleep(1)

        # Verify all events received
        assert len(received_events) == 3
        assert all(e["event_type"] in [ev["event_type"] for ev in events]
                  for e in received_events)

    @pytest.mark.asyncio
    async def test_request_reply_pattern(self, nats_client):
        """Test request-reply communication pattern."""
        # Set up responder
        async def responder(msg):
            request = json.loads(msg.data.decode())
            response = {"result": request["value"] * 2}
            await nats_client.publish(msg.reply, json.dumps(response).encode())

        await nats_client.subscribe("compute.double", cb=responder)

        # Send request
        request = {"value": 21}
        response = await nats_client.request(
            "compute.double",
            json.dumps(request).encode(),
            timeout=2
        )

        # Verify response
        result = json.loads(response.data.decode())
        assert result["result"] == 42

```text

## End-to-End Testing

### User Journey Tests

```javascript
```javascript

```javascript

```javascript
// tests/e2e/user-journeys.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Security Learning Journey', () => {
    test.beforeEach(async ({ page }) => {
        // Login before each test
        await page.goto('http://localhost:3000/login');
        await page.fill('#username', 'test_user');
        await page.fill('#password', 'test_pass');
        await page.click('#login-button');
        await expect(page).toHaveURL('http://localhost:3000/dashboard');
    });

    test('Complete beginner security lesson', async ({ page }) => {
        // Navigate to security tutor
        await page.click('[data-testid="security-tutor-link"]');

        // Select beginner course
        await page.click('[data-testid="course-beginner-nmap"]');

        // Complete lesson steps
        await expect(page.locator('.lesson-title')).toContainText('Introduction to Nmap');

        // Interactive terminal test
        await page.click('[data-testid="launch-terminal"]');
        const terminal = page.locator('[data-testid="terminal-window"]');
        await terminal.type('nmap --version');
        await terminal.press('Enter');

        // Verify output
        await expect(terminal).toContainText('Nmap version');

        // Complete exercise
        await terminal.type('nmap -sn 192.168.1.0/24');
        await terminal.press('Enter');

        // Submit answer
        await page.click('[data-testid="submit-exercise"]');

        // Verify completion
        await expect(page.locator('.completion-message')).toContainText('Congratulations!');
        await expect(page.locator('.xp-gained')).toContainText('+100 XP');
    });

    test('AI assistance during exploitation', async ({ page }) => {
        // Navigate to practice environment
        await page.goto('http://localhost:3000/practice/exploitation');

        // Ask AI for help
        await page.click('[data-testid="ai-assistant-toggle"]');
        await page.fill('[data-testid="ai-input"]', 'How do I exploit this buffer overflow?');
        await page.press('[data-testid="ai-input"]', 'Enter');

        // Verify AI response
        const aiResponse = page.locator('[data-testid="ai-response"]');
        await expect(aiResponse).toContainText('buffer overflow');
        await expect(aiResponse).toContainText('Step 1:');

        // Follow AI guidance
        const terminal = page.locator('[data-testid="practice-terminal"]');
        await terminal.type('gdb vulnerable_program');
        await terminal.press('Enter');

        // Verify context-aware suggestions
        await expect(page.locator('[data-testid="ai-suggestion"]')).toContainText('pattern_create');
    });
});

test.describe('System Administration', () => {
    test('Monitor and manage services', async ({ page }) => {
        await page.goto('http://localhost:3000/admin/services');

        // Check service status
        const serviceGrid = page.locator('[data-testid="service-grid"]');
        await expect(serviceGrid.locator('.service-card')).toHaveCount(5);

        // Restart a service
        await page.click('[data-testid="service-consciousness"] [data-testid="restart-button"]');

        // Verify restart
        await expect(page.locator('[data-testid="service-consciousness"] .status')).toContainText('restarting');
        await page.waitForTimeout(5000);
        await expect(page.locator('[data-testid="service-consciousness"] .status')).toContainText('running');

        // Check logs
        await page.click('[data-testid="service-consciousness"] [data-testid="view-logs"]');
        await expect(page.locator('.log-viewer')).toContainText('Service restarted successfully');
    });
});
```text

        // Login before each test
        await page.goto('http://localhost:3000/login');
        await page.fill('#username', 'test_user');
        await page.fill('#password', 'test_pass');
        await page.click('#login-button');
        await expect(page).toHaveURL('http://localhost:3000/dashboard');
    });

    test('Complete beginner security lesson', async ({ page }) => {
        // Navigate to security tutor
        await page.click('[data-testid="security-tutor-link"]');

        // Select beginner course
        await page.click('[data-testid="course-beginner-nmap"]');

        // Complete lesson steps
        await expect(page.locator('.lesson-title')).toContainText('Introduction to Nmap');

        // Interactive terminal test
        await page.click('[data-testid="launch-terminal"]');
        const terminal = page.locator('[data-testid="terminal-window"]');
        await terminal.type('nmap --version');
        await terminal.press('Enter');

        // Verify output
        await expect(terminal).toContainText('Nmap version');

        // Complete exercise
        await terminal.type('nmap -sn 192.168.1.0/24');
        await terminal.press('Enter');

        // Submit answer
        await page.click('[data-testid="submit-exercise"]');

        // Verify completion
        await expect(page.locator('.completion-message')).toContainText('Congratulations!');
        await expect(page.locator('.xp-gained')).toContainText('+100 XP');
    });

    test('AI assistance during exploitation', async ({ page }) => {
        // Navigate to practice environment
        await page.goto('http://localhost:3000/practice/exploitation');

        // Ask AI for help
        await page.click('[data-testid="ai-assistant-toggle"]');
        await page.fill('[data-testid="ai-input"]', 'How do I exploit this buffer overflow?');
        await page.press('[data-testid="ai-input"]', 'Enter');

        // Verify AI response
        const aiResponse = page.locator('[data-testid="ai-response"]');
        await expect(aiResponse).toContainText('buffer overflow');
        await expect(aiResponse).toContainText('Step 1:');

        // Follow AI guidance
        const terminal = page.locator('[data-testid="practice-terminal"]');
        await terminal.type('gdb vulnerable_program');
        await terminal.press('Enter');

        // Verify context-aware suggestions
        await expect(page.locator('[data-testid="ai-suggestion"]')).toContainText('pattern_create');
    });
});

test.describe('System Administration', () => {
    test('Monitor and manage services', async ({ page }) => {
        await page.goto('http://localhost:3000/admin/services');

        // Check service status
        const serviceGrid = page.locator('[data-testid="service-grid"]');
        await expect(serviceGrid.locator('.service-card')).toHaveCount(5);

        // Restart a service
        await page.click('[data-testid="service-consciousness"] [data-testid="restart-button"]');

        // Verify restart
        await expect(page.locator('[data-testid="service-consciousness"] .status')).toContainText('restarting');
        await page.waitForTimeout(5000);
        await expect(page.locator('[data-testid="service-consciousness"] .status')).toContainText('running');

        // Check logs
        await page.click('[data-testid="service-consciousness"] [data-testid="view-logs"]');
        await expect(page.locator('.log-viewer')).toContainText('Service restarted successfully');
    });
});

```text
        // Login before each test
        await page.goto('http://localhost:3000/login');
        await page.fill('#username', 'test_user');
        await page.fill('#password', 'test_pass');
        await page.click('#login-button');
        await expect(page).toHaveURL('http://localhost:3000/dashboard');
    });

    test('Complete beginner security lesson', async ({ page }) => {
        // Navigate to security tutor
        await page.click('[data-testid="security-tutor-link"]');

        // Select beginner course
        await page.click('[data-testid="course-beginner-nmap"]');

        // Complete lesson steps
        await expect(page.locator('.lesson-title')).toContainText('Introduction to Nmap');

        // Interactive terminal test
        await page.click('[data-testid="launch-terminal"]');
        const terminal = page.locator('[data-testid="terminal-window"]');
        await terminal.type('nmap --version');
        await terminal.press('Enter');

        // Verify output
        await expect(terminal).toContainText('Nmap version');

        // Complete exercise
        await terminal.type('nmap -sn 192.168.1.0/24');
        await terminal.press('Enter');

        // Submit answer
        await page.click('[data-testid="submit-exercise"]');

        // Verify completion
        await expect(page.locator('.completion-message')).toContainText('Congratulations!');
        await expect(page.locator('.xp-gained')).toContainText('+100 XP');
    });

    test('AI assistance during exploitation', async ({ page }) => {
        // Navigate to practice environment
        await page.goto('http://localhost:3000/practice/exploitation');

        // Ask AI for help
        await page.click('[data-testid="ai-assistant-toggle"]');
        await page.fill('[data-testid="ai-input"]', 'How do I exploit this buffer overflow?');
        await page.press('[data-testid="ai-input"]', 'Enter');

        // Verify AI response
        const aiResponse = page.locator('[data-testid="ai-response"]');
        await expect(aiResponse).toContainText('buffer overflow');
        await expect(aiResponse).toContainText('Step 1:');

        // Follow AI guidance
        const terminal = page.locator('[data-testid="practice-terminal"]');
        await terminal.type('gdb vulnerable_program');
        await terminal.press('Enter');

        // Verify context-aware suggestions
        await expect(page.locator('[data-testid="ai-suggestion"]')).toContainText('pattern_create');
    });
});

test.describe('System Administration', () => {
    test('Monitor and manage services', async ({ page }) => {
        await page.goto('http://localhost:3000/admin/services');

        // Check service status
        const serviceGrid = page.locator('[data-testid="service-grid"]');
        await expect(serviceGrid.locator('.service-card')).toHaveCount(5);

        // Restart a service
        await page.click('[data-testid="service-consciousness"] [data-testid="restart-button"]');

        // Verify restart
        await expect(page.locator('[data-testid="service-consciousness"] .status')).toContainText('restarting');
        await page.waitForTimeout(5000);
        await expect(page.locator('[data-testid="service-consciousness"] .status')).toContainText('running');

        // Check logs
        await page.click('[data-testid="service-consciousness"] [data-testid="view-logs"]');
        await expect(page.locator('.log-viewer')).toContainText('Service restarted successfully');
    });
});

```text
        await expect(page).toHaveURL('http://localhost:3000/dashboard');
    });

    test('Complete beginner security lesson', async ({ page }) => {
        // Navigate to security tutor
        await page.click('[data-testid="security-tutor-link"]');

        // Select beginner course
        await page.click('[data-testid="course-beginner-nmap"]');

        // Complete lesson steps
        await expect(page.locator('.lesson-title')).toContainText('Introduction to Nmap');

        // Interactive terminal test
        await page.click('[data-testid="launch-terminal"]');
        const terminal = page.locator('[data-testid="terminal-window"]');
        await terminal.type('nmap --version');
        await terminal.press('Enter');

        // Verify output
        await expect(terminal).toContainText('Nmap version');

        // Complete exercise
        await terminal.type('nmap -sn 192.168.1.0/24');
        await terminal.press('Enter');

        // Submit answer
        await page.click('[data-testid="submit-exercise"]');

        // Verify completion
        await expect(page.locator('.completion-message')).toContainText('Congratulations!');
        await expect(page.locator('.xp-gained')).toContainText('+100 XP');
    });

    test('AI assistance during exploitation', async ({ page }) => {
        // Navigate to practice environment
        await page.goto('http://localhost:3000/practice/exploitation');

        // Ask AI for help
        await page.click('[data-testid="ai-assistant-toggle"]');
        await page.fill('[data-testid="ai-input"]', 'How do I exploit this buffer overflow?');
        await page.press('[data-testid="ai-input"]', 'Enter');

        // Verify AI response
        const aiResponse = page.locator('[data-testid="ai-response"]');
        await expect(aiResponse).toContainText('buffer overflow');
        await expect(aiResponse).toContainText('Step 1:');

        // Follow AI guidance
        const terminal = page.locator('[data-testid="practice-terminal"]');
        await terminal.type('gdb vulnerable_program');
        await terminal.press('Enter');

        // Verify context-aware suggestions
        await expect(page.locator('[data-testid="ai-suggestion"]')).toContainText('pattern_create');
    });
});

test.describe('System Administration', () => {
    test('Monitor and manage services', async ({ page }) => {
        await page.goto('http://localhost:3000/admin/services');

        // Check service status
        const serviceGrid = page.locator('[data-testid="service-grid"]');
        await expect(serviceGrid.locator('.service-card')).toHaveCount(5);

        // Restart a service
        await page.click('[data-testid="service-consciousness"] [data-testid="restart-button"]');

        // Verify restart
        await expect(page.locator('[data-testid="service-consciousness"] .status')).toContainText('restarting');
        await page.waitForTimeout(5000);
        await expect(page.locator('[data-testid="service-consciousness"] .status')).toContainText('running');

        // Check logs
        await page.click('[data-testid="service-consciousness"] [data-testid="view-logs"]');
        await expect(page.locator('.log-viewer')).toContainText('Service restarted successfully');
    });
});

```text

### Visual Regression Tests

```javascript
```javascript

```javascript

```javascript
// tests/e2e/visual-regression.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Visual Regression', () => {
    test('Dashboard layout', async ({ page }) => {
        await page.goto('http://localhost:3000/dashboard');
        await expect(page).toHaveScreenshot('dashboard.png', {
            fullPage: true,
            animations: 'disabled'
        });
    });

    test('Dark mode consistency', async ({ page }) => {
        await page.goto('http://localhost:3000/settings');
        await page.click('[data-testid="theme-toggle"]');

        // Check multiple pages in dark mode
        const pages = ['/dashboard', '/security-tutor', '/services'];

        for (const path of pages) {
            await page.goto(`http://localhost:3000${path}`);
            await expect(page).toHaveScreenshot(`dark-mode${path.replace('/', '-')}.png`);
        }
    });
});
```text

        await page.goto('http://localhost:3000/dashboard');
        await expect(page).toHaveScreenshot('dashboard.png', {
            fullPage: true,
            animations: 'disabled'
        });
    });

    test('Dark mode consistency', async ({ page }) => {
        await page.goto('http://localhost:3000/settings');
        await page.click('[data-testid="theme-toggle"]');

        // Check multiple pages in dark mode
        const pages = ['/dashboard', '/security-tutor', '/services'];

        for (const path of pages) {
            await page.goto(`http://localhost:3000${path}`);
            await expect(page).toHaveScreenshot(`dark-mode${path.replace('/', '-')}.png`);
        }
    });
});

```text
        await page.goto('http://localhost:3000/dashboard');
        await expect(page).toHaveScreenshot('dashboard.png', {
            fullPage: true,
            animations: 'disabled'
        });
    });

    test('Dark mode consistency', async ({ page }) => {
        await page.goto('http://localhost:3000/settings');
        await page.click('[data-testid="theme-toggle"]');

        // Check multiple pages in dark mode
        const pages = ['/dashboard', '/security-tutor', '/services'];

        for (const path of pages) {
            await page.goto(`http://localhost:3000${path}`);
            await expect(page).toHaveScreenshot(`dark-mode${path.replace('/', '-')}.png`);
        }
    });
});

```text
    });

    test('Dark mode consistency', async ({ page }) => {
        await page.goto('http://localhost:3000/settings');
        await page.click('[data-testid="theme-toggle"]');

        // Check multiple pages in dark mode
        const pages = ['/dashboard', '/security-tutor', '/services'];

        for (const path of pages) {
            await page.goto(`http://localhost:3000${path}`);
            await expect(page).toHaveScreenshot(`dark-mode${path.replace('/', '-')}.png`);
        }
    });
});

```text

## Performance Testing

### Load Testing with K6

```javascript
```javascript

```javascript

```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
    stages: [
        { duration: '2m', target: 100 },  // Ramp up
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 200 },  // Ramp up more
        { duration: '5m', target: 200 },  // Stay at 200 users
        { duration: '2m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
        errors: ['rate<0.1'],             // Error rate under 10%
    },
};

export default function () {
    // Test authentication endpoint
    const authPayload = JSON.stringify({
        username: `user_${__VU}`,
        password: 'test_password',
    });

    const authResponse = http.post(
        'http://localhost:8081/api/v1/auth/login',
        authPayload,
        { headers: { 'Content-Type': 'application/json' } }
    );

    const success = check(authResponse, {
        'auth status is 200': (r) => r.status === 200,
        'auth response time < 200ms': (r) => r.timings.duration < 200,
        'token received': (r) => JSON.parse(r.body).access_token !== undefined,
    });

    errorRate.add(!success);

    if (success) {
        const token = JSON.parse(authResponse.body).access_token;

        // Test AI inference endpoint
        const inferenceResponse = http.post(
            'http://localhost:8082/api/v1/consciousness/process',
            JSON.stringify({
                input: { type: 'security_query', content: 'How to scan ports?' }
            }),
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                }
            }
        );

        check(inferenceResponse, {
            'inference status is 200': (r) => r.status === 200,
            'inference response time < 1000ms': (r) => r.timings.duration < 1000,
        });
    }

    sleep(1);
}
```text

const errorRate = new Rate('errors');

export const options = {
    stages: [
        { duration: '2m', target: 100 },  // Ramp up
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 200 },  // Ramp up more
        { duration: '5m', target: 200 },  // Stay at 200 users
        { duration: '2m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
        errors: ['rate<0.1'],             // Error rate under 10%
    },
};

export default function () {
    // Test authentication endpoint
    const authPayload = JSON.stringify({
        username: `user_${__VU}`,
        password: 'test_password',
    });

    const authResponse = http.post(
        'http://localhost:8081/api/v1/auth/login',
        authPayload,
        { headers: { 'Content-Type': 'application/json' } }
    );

    const success = check(authResponse, {
        'auth status is 200': (r) => r.status === 200,
        'auth response time < 200ms': (r) => r.timings.duration < 200,
        'token received': (r) => JSON.parse(r.body).access_token !== undefined,
    });

    errorRate.add(!success);

    if (success) {
        const token = JSON.parse(authResponse.body).access_token;

        // Test AI inference endpoint
        const inferenceResponse = http.post(
            'http://localhost:8082/api/v1/consciousness/process',
            JSON.stringify({
                input: { type: 'security_query', content: 'How to scan ports?' }
            }),
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                }
            }
        );

        check(inferenceResponse, {
            'inference status is 200': (r) => r.status === 200,
            'inference response time < 1000ms': (r) => r.timings.duration < 1000,
        });
    }

    sleep(1);
}

```text
const errorRate = new Rate('errors');

export const options = {
    stages: [
        { duration: '2m', target: 100 },  // Ramp up
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 200 },  // Ramp up more
        { duration: '5m', target: 200 },  // Stay at 200 users
        { duration: '2m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
        errors: ['rate<0.1'],             // Error rate under 10%
    },
};

export default function () {
    // Test authentication endpoint
    const authPayload = JSON.stringify({
        username: `user_${__VU}`,
        password: 'test_password',
    });

    const authResponse = http.post(
        'http://localhost:8081/api/v1/auth/login',
        authPayload,
        { headers: { 'Content-Type': 'application/json' } }
    );

    const success = check(authResponse, {
        'auth status is 200': (r) => r.status === 200,
        'auth response time < 200ms': (r) => r.timings.duration < 200,
        'token received': (r) => JSON.parse(r.body).access_token !== undefined,
    });

    errorRate.add(!success);

    if (success) {
        const token = JSON.parse(authResponse.body).access_token;

        // Test AI inference endpoint
        const inferenceResponse = http.post(
            'http://localhost:8082/api/v1/consciousness/process',
            JSON.stringify({
                input: { type: 'security_query', content: 'How to scan ports?' }
            }),
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                }
            }
        );

        check(inferenceResponse, {
            'inference status is 200': (r) => r.status === 200,
            'inference response time < 1000ms': (r) => r.timings.duration < 1000,
        });
    }

    sleep(1);
}

```text
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 200 },  // Ramp up more
        { duration: '5m', target: 200 },  // Stay at 200 users
        { duration: '2m', target: 0 },    // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
        errors: ['rate<0.1'],             // Error rate under 10%
    },
};

export default function () {
    // Test authentication endpoint
    const authPayload = JSON.stringify({
        username: `user_${__VU}`,
        password: 'test_password',
    });

    const authResponse = http.post(
        'http://localhost:8081/api/v1/auth/login',
        authPayload,
        { headers: { 'Content-Type': 'application/json' } }
    );

    const success = check(authResponse, {
        'auth status is 200': (r) => r.status === 200,
        'auth response time < 200ms': (r) => r.timings.duration < 200,
        'token received': (r) => JSON.parse(r.body).access_token !== undefined,
    });

    errorRate.add(!success);

    if (success) {
        const token = JSON.parse(authResponse.body).access_token;

        // Test AI inference endpoint
        const inferenceResponse = http.post(
            'http://localhost:8082/api/v1/consciousness/process',
            JSON.stringify({
                input: { type: 'security_query', content: 'How to scan ports?' }
            }),
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                }
            }
        );

        check(inferenceResponse, {
            'inference status is 200': (r) => r.status === 200,
            'inference response time < 1000ms': (r) => r.timings.duration < 1000,
        });
    }

    sleep(1);
}

```text

### Stress Testing

```python

```python
```python

```python

## tests/performance/stress_test.py

import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

class StressTest:
    def __init__(self, base_url, concurrent_users=1000):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []

    async def single_user_scenario(self, user_id):
        """Simulate a single user's actions."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                # Login
                login_resp = await session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"username": f"user_{user_id}", "password": "test"}
                )
                token = (await login_resp.json())["access_token"]

                # Make multiple requests
                headers = {"Authorization": f"Bearer {token}"}

                tasks = [
                    session.get(f"{self.base_url}/api/v1/consciousness/state", headers=headers),
                    session.post(
                        f"{self.base_url}/api/v1/context/update",
                        json={"activity": "test"},
                        headers=headers
                    ),
                    session.get(f"{self.base_url}/api/v1/services", headers=headers),
                ]

                responses = await asyncio.gather(*tasks)

                # Record results
                self.results.append({
                    "user_id": user_id,
                    "duration": time.time() - start_time,
                    "success": all(r.status == 200 for r in responses),
                    "status_codes": [r.status for r in responses]
                })

            except Exception as e:
                self.results.append({
                    "user_id": user_id,
                    "duration": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                })

    async def run_stress_test(self):
        """Run stress test with concurrent users."""
        print(f"Starting stress test with {self.concurrent_users} concurrent users...")

        tasks = [
            self.single_user_scenario(i)
            for i in range(self.concurrent_users)
        ]

        await asyncio.gather(*tasks)

        # Analyze results
        successful = sum(1 for r in self.results if r["success"])
        avg_duration = sum(r["duration"] for r in self.results) / len(self.results)

        print(f"\nResults:")
        print(f"Success rate: {successful/self.concurrent_users*100:.2f}%")
        print(f"Average duration: {avg_duration:.2f}s")
        print(f"Requests per second: {self.concurrent_users/avg_duration:.2f}")

if __name__ == "__main__":
    stress_test = StressTest("http://localhost:8080", concurrent_users=1000)
    asyncio.run(stress_test.run_stress_test())
```text

import time
from concurrent.futures import ThreadPoolExecutor

class StressTest:
    def __init__(self, base_url, concurrent_users=1000):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []

    async def single_user_scenario(self, user_id):
        """Simulate a single user's actions."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                # Login
                login_resp = await session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"username": f"user_{user_id}", "password": "test"}
                )
                token = (await login_resp.json())["access_token"]

                # Make multiple requests
                headers = {"Authorization": f"Bearer {token}"}

                tasks = [
                    session.get(f"{self.base_url}/api/v1/consciousness/state", headers=headers),
                    session.post(
                        f"{self.base_url}/api/v1/context/update",
                        json={"activity": "test"},
                        headers=headers
                    ),
                    session.get(f"{self.base_url}/api/v1/services", headers=headers),
                ]

                responses = await asyncio.gather(*tasks)

                # Record results
                self.results.append({
                    "user_id": user_id,
                    "duration": time.time() - start_time,
                    "success": all(r.status == 200 for r in responses),
                    "status_codes": [r.status for r in responses]
                })

            except Exception as e:
                self.results.append({
                    "user_id": user_id,
                    "duration": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                })

    async def run_stress_test(self):
        """Run stress test with concurrent users."""
        print(f"Starting stress test with {self.concurrent_users} concurrent users...")

        tasks = [
            self.single_user_scenario(i)
            for i in range(self.concurrent_users)
        ]

        await asyncio.gather(*tasks)

        # Analyze results
        successful = sum(1 for r in self.results if r["success"])
        avg_duration = sum(r["duration"] for r in self.results) / len(self.results)

        print(f"\nResults:")
        print(f"Success rate: {successful/self.concurrent_users*100:.2f}%")
        print(f"Average duration: {avg_duration:.2f}s")
        print(f"Requests per second: {self.concurrent_users/avg_duration:.2f}")

if __name__ == "__main__":
    stress_test = StressTest("http://localhost:8080", concurrent_users=1000)
    asyncio.run(stress_test.run_stress_test())

```text
import time
from concurrent.futures import ThreadPoolExecutor

class StressTest:
    def __init__(self, base_url, concurrent_users=1000):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []

    async def single_user_scenario(self, user_id):
        """Simulate a single user's actions."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                # Login
                login_resp = await session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"username": f"user_{user_id}", "password": "test"}
                )
                token = (await login_resp.json())["access_token"]

                # Make multiple requests
                headers = {"Authorization": f"Bearer {token}"}

                tasks = [
                    session.get(f"{self.base_url}/api/v1/consciousness/state", headers=headers),
                    session.post(
                        f"{self.base_url}/api/v1/context/update",
                        json={"activity": "test"},
                        headers=headers
                    ),
                    session.get(f"{self.base_url}/api/v1/services", headers=headers),
                ]

                responses = await asyncio.gather(*tasks)

                # Record results
                self.results.append({
                    "user_id": user_id,
                    "duration": time.time() - start_time,
                    "success": all(r.status == 200 for r in responses),
                    "status_codes": [r.status for r in responses]
                })

            except Exception as e:
                self.results.append({
                    "user_id": user_id,
                    "duration": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                })

    async def run_stress_test(self):
        """Run stress test with concurrent users."""
        print(f"Starting stress test with {self.concurrent_users} concurrent users...")

        tasks = [
            self.single_user_scenario(i)
            for i in range(self.concurrent_users)
        ]

        await asyncio.gather(*tasks)

        # Analyze results
        successful = sum(1 for r in self.results if r["success"])
        avg_duration = sum(r["duration"] for r in self.results) / len(self.results)

        print(f"\nResults:")
        print(f"Success rate: {successful/self.concurrent_users*100:.2f}%")
        print(f"Average duration: {avg_duration:.2f}s")
        print(f"Requests per second: {self.concurrent_users/avg_duration:.2f}")

if __name__ == "__main__":
    stress_test = StressTest("http://localhost:8080", concurrent_users=1000)
    asyncio.run(stress_test.run_stress_test())

```text
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.results = []

    async def single_user_scenario(self, user_id):
        """Simulate a single user's actions."""
        async with aiohttp.ClientSession() as session:
            start_time = time.time()

            try:
                # Login
                login_resp = await session.post(
                    f"{self.base_url}/api/v1/auth/login",
                    json={"username": f"user_{user_id}", "password": "test"}
                )
                token = (await login_resp.json())["access_token"]

                # Make multiple requests
                headers = {"Authorization": f"Bearer {token}"}

                tasks = [
                    session.get(f"{self.base_url}/api/v1/consciousness/state", headers=headers),
                    session.post(
                        f"{self.base_url}/api/v1/context/update",
                        json={"activity": "test"},
                        headers=headers
                    ),
                    session.get(f"{self.base_url}/api/v1/services", headers=headers),
                ]

                responses = await asyncio.gather(*tasks)

                # Record results
                self.results.append({
                    "user_id": user_id,
                    "duration": time.time() - start_time,
                    "success": all(r.status == 200 for r in responses),
                    "status_codes": [r.status for r in responses]
                })

            except Exception as e:
                self.results.append({
                    "user_id": user_id,
                    "duration": time.time() - start_time,
                    "success": False,
                    "error": str(e)
                })

    async def run_stress_test(self):
        """Run stress test with concurrent users."""
        print(f"Starting stress test with {self.concurrent_users} concurrent users...")

        tasks = [
            self.single_user_scenario(i)
            for i in range(self.concurrent_users)
        ]

        await asyncio.gather(*tasks)

        # Analyze results
        successful = sum(1 for r in self.results if r["success"])
        avg_duration = sum(r["duration"] for r in self.results) / len(self.results)

        print(f"\nResults:")
        print(f"Success rate: {successful/self.concurrent_users*100:.2f}%")
        print(f"Average duration: {avg_duration:.2f}s")
        print(f"Requests per second: {self.concurrent_users/avg_duration:.2f}")

if __name__ == "__main__":
    stress_test = StressTest("http://localhost:8080", concurrent_users=1000)
    asyncio.run(stress_test.run_stress_test())

```text

## Security Testing

### Penetration Testing

```python

```python
```python

```python

## tests/security/test_penetration.py

import pytest
from zapv2 import ZAPv2
import requests

class TestSecurityPenetration:
    """Automated penetration testing suite."""

    @pytest.fixture(scope="class")
    def zap(self):
        """Initialize ZAP proxy."""
        return ZAPv2(proxies={'http': 'http://127.0.0.1:8090'})

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities."""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL--",
            "' OR 1=1--",
        ]

        for payload in payloads:
            response = requests.post(
                "http://localhost:8081/api/v1/auth/login",
                json={"username": payload, "password": "test"}
            )

            # Should not return 500 or expose SQL errors
            assert response.status_code in [400, 401]
            assert "sql" not in response.text.lower()
            assert "syntax" not in response.text.lower()

    def test_xss_prevention(self):
        """Test XSS attack prevention."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        ]

        for payload in xss_payloads:
            response = requests.post(
                "http://localhost:8082/api/v1/consciousness/process",
                json={"input": {"content": payload}},
                headers={"Authorization": "Bearer test_token"}
            )

            # Response should escape or reject malicious input
            if response.status_code == 200:
                assert payload not in response.text
                assert "&lt;script&gt;" in response.text or "invalid input" in response.text.lower()

    def test_authentication_bypass(self):
        """Test authentication bypass attempts."""
        bypass_attempts = [
            {"Authorization": "Bearer "},
            {"Authorization": "Bearer null"},
            {"Authorization": "Bearer undefined"},
            {"Authorization": "Basic YWRtaW46YWRtaW4="},
            {},  # No auth header
        ]

        for headers in bypass_attempts:
            response = requests.get(
                "http://localhost:8082/api/v1/consciousness/state",
                headers=headers
            )

            # Should require valid authentication
            assert response.status_code == 401

    def test_api_fuzzing(self, zap):
        """Fuzz test API endpoints."""
        target = "http://localhost:8080"

        # Spider the API
        print("Spidering API...")
        zap.spider.scan(target)

        # Wait for spider to complete
        while int(zap.spider.status()) < 100:
            time.sleep(1)

        # Run active scan
        print("Running active scan...")
        zap.ascan.scan
import requests

class TestSecurityPenetration:
    """Automated penetration testing suite."""

    @pytest.fixture(scope="class")
    def zap(self):
        """Initialize ZAP proxy."""
        return ZAPv2(proxies={'http': 'http://127.0.0.1:8090'})

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities."""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL--",
            "' OR 1=1--",
        ]

        for payload in payloads:
            response = requests.post(
                "http://localhost:8081/api/v1/auth/login",
                json={"username": payload, "password": "test"}
            )

            # Should not return 500 or expose SQL errors
            assert response.status_code in [400, 401]
            assert "sql" not in response.text.lower()
            assert "syntax" not in response.text.lower()

    def test_xss_prevention(self):
        """Test XSS attack prevention."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        ]

        for payload in xss_payloads:
            response = requests.post(
                "http://localhost:8082/api/v1/consciousness/process",
                json={"input": {"content": payload}},
                headers={"Authorization": "Bearer test_token"}
            )

            # Response should escape or reject malicious input
            if response.status_code == 200:
                assert payload not in response.text
                assert "&lt;script&gt;" in response.text or "invalid input" in response.text.lower()

    def test_authentication_bypass(self):
        """Test authentication bypass attempts."""
        bypass_attempts = [
            {"Authorization": "Bearer "},
            {"Authorization": "Bearer null"},
            {"Authorization": "Bearer undefined"},
            {"Authorization": "Basic YWRtaW46YWRtaW4="},
            {},  # No auth header
        ]

        for headers in bypass_attempts:
            response = requests.get(
                "http://localhost:8082/api/v1/consciousness/state",
                headers=headers
            )

            # Should require valid authentication
            assert response.status_code == 401

    def test_api_fuzzing(self, zap):
        """Fuzz test API endpoints."""
        target = "http://localhost:8080"

        # Spider the API
        print("Spidering API...")
        zap.spider.scan(target)

        # Wait for spider to complete
        while int(zap.spider.status()) < 100:
            time.sleep(1)

        # Run active scan
        print("Running active scan...")
        zap.ascan.scan
import requests

class TestSecurityPenetration:
    """Automated penetration testing suite."""

    @pytest.fixture(scope="class")
    def zap(self):
        """Initialize ZAP proxy."""
        return ZAPv2(proxies={'http': 'http://127.0.0.1:8090'})

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities."""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL--",
            "' OR 1=1--",
        ]

        for payload in payloads:
            response = requests.post(
                "http://localhost:8081/api/v1/auth/login",
                json={"username": payload, "password": "test"}
            )

            # Should not return 500 or expose SQL errors
            assert response.status_code in [400, 401]
            assert "sql" not in response.text.lower()
            assert "syntax" not in response.text.lower()

    def test_xss_prevention(self):
        """Test XSS attack prevention."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        ]

        for payload in xss_payloads:
            response = requests.post(
                "http://localhost:8082/api/v1/consciousness/process",
                json={"input": {"content": payload}},
                headers={"Authorization": "Bearer test_token"}
            )

            # Response should escape or reject malicious input
            if response.status_code == 200:
                assert payload not in response.text
                assert "&lt;script&gt;" in response.text or "invalid input" in response.text.lower()

    def test_authentication_bypass(self):
        """Test authentication bypass attempts."""
        bypass_attempts = [
            {"Authorization": "Bearer "},
            {"Authorization": "Bearer null"},
            {"Authorization": "Bearer undefined"},
            {"Authorization": "Basic YWRtaW46YWRtaW4="},
            {},  # No auth header
        ]

        for headers in bypass_attempts:
            response = requests.get(
                "http://localhost:8082/api/v1/consciousness/state",
                headers=headers
            )

            # Should require valid authentication
            assert response.status_code == 401

    def test_api_fuzzing(self, zap):
        """Fuzz test API endpoints."""
        target = "http://localhost:8080"

        # Spider the API
        print("Spidering API...")
        zap.spider.scan(target)

        # Wait for spider to complete
        while int(zap.spider.status()) < 100:
            time.sleep(1)

        # Run active scan
        print("Running active scan...")
        zap.ascan.scan
import requests

class TestSecurityPenetration:
    """Automated penetration testing suite."""

    @pytest.fixture(scope="class")
    def zap(self):
        """Initialize ZAP proxy."""
        return ZAPv2(proxies={'http': 'http://127.0.0.1:8090'})

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities."""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL--",
            "' OR 1=1--",
        ]

        for payload in payloads:
            response = requests.post(
                "http://localhost:8081/api/v1/auth/login",
                json={"username": payload, "password": "test"}
            )

            # Should not return 500 or expose SQL errors
            assert response.status_code in [400, 401]
            assert "sql" not in response.text.lower()
            assert "syntax" not in response.text.lower()

    def test_xss_prevention(self):
        """Test XSS attack prevention."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        ]

        for payload in xss_payloads:
            response = requests.post(
                "http://localhost:8082/api/v1/consciousness/process",
                json={"input": {"content": payload}},
                headers={"Authorization": "Bearer test_token"}
            )

            # Response should escape or reject malicious input
            if response.status_code == 200:
                assert payload not in response.text
                assert "&lt;script&gt;" in response.text or "invalid input" in response.text.lower()

    def test_authentication_bypass(self):
        """Test authentication bypass attempts."""
        bypass_attempts = [
            {"Authorization": "Bearer "},
            {"Authorization": "Bearer null"},
            {"Authorization": "Bearer undefined"},
            {"Authorization": "Basic YWRtaW46YWRtaW4="},
            {},  # No auth header
        ]

        for headers in bypass_attempts:
            response = requests.get(
                "http://localhost:8082/api/v1/consciousness/state",
                headers=headers
            )

            # Should require valid authentication
            assert response.status_code == 401

    def test_api_fuzzing(self, zap):
        """Fuzz test API endpoints."""
        target = "http://localhost:8080"

        # Spider the API
        print("Spidering API...")
        zap.spider.scan(target)

        # Wait for spider to complete
        while int(zap.spider.status()) < 100:
            time.sleep(1)

        # Run active scan
        print("Running active scan...")
        zap.ascan.scan