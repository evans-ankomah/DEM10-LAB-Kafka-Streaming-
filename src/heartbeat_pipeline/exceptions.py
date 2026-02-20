"""Custom exceptions for the heartbeat pipeline."""


class HeartbeatPipelineError(Exception):
    """Base exception for all heartbeat pipeline errors."""

    pass


class ConfigurationError(HeartbeatPipelineError):
    """Raised when configuration is invalid or missing."""

    pass


class ValidationError(HeartbeatPipelineError):
    """Raised when data validation fails."""

    pass


class DatabaseError(HeartbeatPipelineError):
    """Raised when database operations fail."""

    pass


class KafkaError(HeartbeatPipelineError):
    """Raised when Kafka operations fail."""

    pass
