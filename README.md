# Eloqua Decision Service Cloud App Framework

A comprehensive framework for building Oracle Eloqua AppCloud Decision Services using FastAPI. This framework handles all the complexity of Eloqua AppCloud integration while providing a simple, extensible interface for implementing custom decision logic.

## Features

- **Complete Eloqua AppCloud Integration**: Implements all required endpoints (Create, Configure, Notify, Delete)
- **OAuth 1.0a Authentication**: Proper Eloqua API authentication with signature verification
- **Bulk API Integration**: Asynchronous decision processing using Eloqua's Bulk API
- **Professional Configuration UI**: Modern Bootstrap 5-based configuration interface with real-time validation
- **Extensible Framework**: Easy-to-extend base classes for custom decision logic
- **Configuration Management**: Environment-based configuration with validation
- **Production Ready**: Logging, error handling, and monitoring endpoints included

## Architecture

### Framework Components

- **`app.py`**: Core FastAPI application with Eloqua AppCloud endpoints
- **`decision_service_base.py`**: Abstract base class for implementing decision logic
- **`eloqua_oauth_fastapi.py`**: OAuth 1.0a authentication and signature verification
- **`eloqua_bulk_api.py`**: Eloqua Bulk API client for decision responses
- **`config.py`**: Configuration management and environment handling
- **`schemas.py`**: Pydantic models for data validation

### Eloqua AppCloud Flow

1. **Service Creation**: When dragged onto canvas, Eloqua calls Create URL
2. **Configuration**: Marketers configure the service via Configure URL
3. **Execution**: When contacts flow through, Eloqua calls Notification URL
4. **Response**: Framework processes contacts and returns decisions via Bulk API
5. **Cleanup**: Delete URL handles service instance cleanup

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/eloqua-decision-framework.git
cd eloqua-decision-framework

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 2. Configuration

Edit the `.env` file with your Eloqua OAuth credentials:

```env
ELOQUA_CONSUMER_KEY=your_consumer_key_here
ELOQUA_CONSUMER_SECRET=your_consumer_secret_here
SERVICE_NAME=My Decision Service
ENABLE_OAUTH_VERIFICATION=true
```

### 3. Run the Application

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`

### 4. Register with Eloqua

In your Eloqua instance, register a new Decision Service with these URLs:

- **Create URL**: `https://your-domain.com/decision/create?instanceId={InstanceId}&installId={InstallId}`
- **Configure URL**: `https://your-domain.com/decision/configure?instanceId={InstanceId}`
- **Notification URL**: `https://your-domain.com/decision/notify?instanceId={InstanceId}&executionId={ExecutionId}`
- **Delete URL**: `https://your-domain.com/decision/delete?instanceId={InstanceId}`

## Custom Decision Logic

### Extending the Framework

Create your own decision service by extending `DecisionServiceBase`:

```python
from decision_service_base import DecisionServiceBase
from typing import Dict, Any

class MyCustomDecisionService(DecisionServiceBase):
    def __init__(self):
        super().__init__(
            service_name="My Custom Decision Service",
            service_description="Custom logic for contact decisions"
        )
    
    def make_decision(self, contact: Dict[str, Any], instance_config: Dict[str, Any]) -> str:
        """
        Implement your custom decision logic here
        Returns: "yes", "no", or "errored"
        """
        # Example: Check if contact has valid email domain
        email = contact.get("EmailAddress", "")
        if "@company.com" in email:
            return "yes"
        return "no"
    
    def get_record_definition(self, instance_config: Dict[str, Any] = None) -> Dict[str, str]:
        """Define which Eloqua fields you need"""
        return {
            "ContactID": "{{Contact.Id}}",
            "EmailAddress": "{{Contact.Field(C_EmailAddress)}}",
            "Company": "{{Contact.Field(C_Company)}}"
        }
```

### Using Your Custom Service

Replace the default service in `app.py`:

```python
# Replace this line in app.py
decision_service: DecisionServiceBase = SimpleEmailValidationService()

# With your custom service
decision_service: DecisionServiceBase = MyCustomDecisionService()
```

## API Reference

### Core Endpoints

- `POST /decision/create` - Create new service instance
- `GET /decision/configure` - Serve configuration UI
- `POST /decision/configure/save` - Save configuration
- `POST /decision/notify` - Process contact notifications
- `DELETE /decision/delete` - Delete service instance

### Monitoring Endpoints

- `GET /health` - Health check
- `GET /config/instances` - List service instances
- `GET /config/settings` - View service settings

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ELOQUA_CONSUMER_KEY` | OAuth consumer key | Required |
| `ELOQUA_CONSUMER_SECRET` | OAuth consumer secret | Required |
| `SERVICE_NAME` | Service display name | "Eloqua Decision Service" |
| `ENABLE_OAUTH_VERIFICATION` | Enable OAuth signature verification | true |
| `MAX_RECORDS_PER_NOTIFICATION` | Max contacts per batch | 1000 |
| `LOG_LEVEL` | Logging level | INFO |

### Service Settings

Configure decision service behavior:

```python
from config import get_settings

settings = get_settings()
settings.requires_configuration = True
settings.max_records_per_notification = 500
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=.
```

### Code Quality

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking
mypy .
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **HTTPS Required**: Eloqua requires SSL/TLS for all endpoints
2. **OAuth Verification**: Keep OAuth verification enabled in production
3. **CDN Access**: Configuration UI uses Bootstrap 5 and Bootstrap Icons from CDN
4. **Logging**: Configure appropriate log levels and monitoring
5. **Scaling**: Use multiple workers for high-volume deployments
6. **Storage**: Consider Redis or database for persistent service instance storage

## Troubleshooting

### Common Issues

**OAuth Signature Verification Fails**
- Verify consumer key and secret are correct
- Check that system time is synchronized
- Ensure URLs match exactly with Eloqua registration

**Contacts Not Processing**
- Check notification URL is accessible from Eloqua
- Verify record definition matches contact data
- Review logs for processing errors

**Configuration UI Not Loading**
- Ensure X-Frame-Options is not set to DENY
- Check JavaScript console for errors
- Verify configure URL parameters

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
ENABLE_DEBUG=true
```

## Configuration UI

The framework provides professional, production-ready configuration interfaces:

### Default Configuration UI
- Modern Bootstrap 5 design with responsive layout
- Service status controls and timeout settings
- Debug mode toggle and configuration notes
- Real-time form validation and user feedback
- Professional navigation with tabs for Config, Stats, Help, and Support

### Email Validation Configuration UI
- Specialized interface for email validation rules
- Domain validation controls and blocked domain management
- Live preview of validation rules
- Real-time email testing functionality
- Visual feedback and error handling

### Customizing Configuration UI

Override the `get_configuration_ui()` method in your decision service:

```python
class MyDecisionService(DecisionServiceBase):
    def get_configuration_ui(self, instance_id: str, instance_config: Dict[str, Any]) -> str:
        # Return your custom HTML configuration interface
        return self._get_default_configuration_ui(instance_id, instance_config)
```

## Examples

The framework includes a complete email validation example (`SimpleEmailValidationService`) that demonstrates:

- Custom decision logic
- Professional configuration UI
- Field validation
- Error handling
- Real-time testing capabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review Eloqua AppCloud documentation
- Open an issue in the repository
