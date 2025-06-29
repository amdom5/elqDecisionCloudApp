# Eloqua AppCloud Decision Service Framework

A comprehensive framework for building Oracle Eloqua AppCloud Decision Services using FastAPI. This framework handles all the complexity of Eloqua AppCloud integration while providing a simple, extensible interface for implementing custom decision logic.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Custom Decision Logic](#custom-decision-logic)
- [Configuration UI](#configuration-ui)
- [Deployment and Connectivity](#deployment-and-connectivity)
- [API Reference](#api-reference)
- [Development](#development)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

### Features

- **Complete Eloqua AppCloud Integration**: Implements all required endpoints (Create, Configure, Notify, Delete)
- **OAuth 1.0a Authentication**: Proper Eloqua API authentication with signature verification
- **Bulk API Integration**: Asynchronous decision processing using Eloqua's Bulk API
- **Professional Configuration UI**: Modern interface inspired by Oracle Redwood Experience
- **Extensible Framework**: Easy-to-extend base classes for custom decision logic
- **Administrative Endpoints**: Health check and service instance management endpoints

### Architecture

#### Framework Components

- **`app.py`**: Core FastAPI application with Eloqua AppCloud endpoints
- **`decision_service_base.py`**: Abstract base class for implementing decision logic
- **`eloqua_oauth_fastapi.py`**: OAuth 1.0a authentication and signature verification
- **`eloqua_bulk_api.py`**: Eloqua Bulk API client for decision responses
- **`config.py`**: Configuration management and environment handling
- **`schemas.py`**: Pydantic models for data validation

#### Eloqua AppCloud Flow

1. **Service Creation**: When dragged onto canvas, Eloqua calls Create URL
2. **Configuration**: Marketers configure the service via Configure URL
3. **Execution**: When contacts flow through, Eloqua calls Notification URL
4. **Response**: Framework processes contacts and returns decisions via Bulk API
5. **Cleanup**: Delete URL handles service instance cleanup

## Quick Start

### Prerequisites

Before you begin, make sure you have the following installed on your computer:

- **Python 3.8 or higher**: This application is built with Python. Download from [python.org](https://www.python.org/downloads/)
- **Git**: For downloading the code. Download from [git-scm.com](https://git-scm.com/downloads)
- **Eloqua OAuth Credentials**: You'll need consumer key and secret from your Eloqua instance

### 1. Installation

Download and set up the application:

```bash
# Download the code from GitHub
git clone https://github.com/amdom5/elqDecisionCloudApp.git
cd elqDecisionCloudApp

# Install required Python packages
pip install -r requirements.txt

# Create your configuration file
cp .env.example .env
```

**What this does:**
- Downloads the application code to your computer
- Installs all the Python libraries the application needs
- Creates a configuration file where you'll add your Eloqua credentials

### 2. Configuration

Open the `.env` file (created in step 1) in any text editor and add your Eloqua credentials:

```env
ELOQUA_CONSUMER_KEY=your_consumer_key_here
ELOQUA_CONSUMER_SECRET=your_consumer_secret_here
SERVICE_NAME=My Decision Service
ENABLE_OAUTH_VERIFICATION=true
```

**Where to find your Eloqua credentials:**
- Log into your Eloqua instance
- Go to Settings → Integration → App Management
- Find your OAuth application and copy the Consumer Key and Consumer Secret
- Replace `your_consumer_key_here` and `your_consumer_secret_here` with your actual values

### 3. Running the Application Locally

Start the application on your computer for testing:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The service will be running at `http://localhost:8000` (you can open this in your web browser to test)

**Important:** When running locally, Eloqua cannot reach your application. This is only for development and testing. See the [Deployment and Connectivity](#deployment-and-connectivity) section to learn how to make it accessible to Eloqua.

### 4. Register with Eloqua

Once your application is deployed (see [Deployment section](#deployment-and-connectivity)), register it as a Decision Service in Eloqua:

**In your Eloqua instance:**
1. Go to Settings → Integration → Decision Services
2. Click "Add New Decision Service"
3. Enter these URLs (replace `your-domain.com` with your actual website domain):

- **Create URL**: `https://your-domain.com/decision/create?instanceId={InstanceId}&installId={InstallId}`
- **Configure URL**: `https://your-domain.com/decision/configure?instanceId={InstanceId}`
- **Notification URL**: `https://your-domain.com/decision/notify?instanceId={InstanceId}&executionId={ExecutionId}`
- **Delete URL**: `https://your-domain.com/decision/delete?instanceId={InstanceId}`

**Important:** 
- These URLs must be publicly accessible on the internet (not localhost)
- Must use HTTPS (secure connection)
- Replace `your-domain.com` with your actual domain name where you deployed the application

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

## API Reference

### Core Endpoints

- `POST /decision/create` - Create new service instance
- `GET /decision/configure` - Serve configuration UI
- `POST /decision/configure/save` - Save configuration
- `POST /decision/notify` - Process contact notifications
- `DELETE /decision/delete` - Delete service instance

### Administrative Endpoints

- `GET /health` - Health check
- `GET /config/instances` - List service instances
- `GET /config/settings` - View service settings

### Configuration Options

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ELOQUA_CONSUMER_KEY` | OAuth consumer key | Required |
| `ELOQUA_CONSUMER_SECRET` | OAuth consumer secret | Required |
| `SERVICE_NAME` | Service display name | "Eloqua Decision Service" |
| `ENABLE_OAUTH_VERIFICATION` | Enable OAuth signature verification | true |
| `MAX_RECORDS_PER_NOTIFICATION` | Max contacts per batch | 1000 |
| `LOG_LEVEL` | Logging level | INFO |

#### Service Settings

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

## Deployment and Connectivity

### Local Development vs Production

When running locally with `uvicorn app:app --host 0.0.0.0 --port 8000`, your service is only accessible from your local machine at `http://localhost:8000`. **Eloqua cannot reach your local development server** because:

1. **Network Isolation**: Your local machine is behind a router/firewall
2. **Private IP**: Localhost (127.0.0.1) is not accessible from the internet
3. **HTTP vs HTTPS**: Eloqua requires HTTPS, but local development typically uses HTTP

### Making Your Service Accessible to Eloqua

To connect your locally running service to Eloqua, you need to make it publicly accessible. Here are the main approaches:

#### Option 1: Cloud Deployment (Recommended)
Deploy your service to a cloud platform with a public domain:

- **AWS**: Use EC2, ECS, or Lambda with Application Load Balancer
- **Google Cloud**: Use Cloud Run, Compute Engine, or App Engine
- **Azure**: Use Container Instances, App Service, or Virtual Machines
- **DigitalOcean**: Use Droplets or App Platform
- **Heroku**: Use web dynos with custom domains

#### Option 2: Tunneling Services (Development/Testing)
Use a tunneling service to expose your local server:

- **ngrok**: `ngrok http 8000` creates a public HTTPS URL
- **Cloudflare Tunnel**: Free tunneling with custom domains
- **LocalTunnel**: `npx localtunnel --port 8000` for temporary access

#### Option 3: VPS/Dedicated Server
Deploy to a Virtual Private Server with a public IP address and domain name.

### URL Configuration Requirements

The URLs you register with Eloqua must be:

1. **Publicly Accessible**: Reachable from Eloqua's servers on the internet
2. **HTTPS Only**: SSL/TLS certificate required (HTTP will be rejected)
3. **Proper Domain**: Replace `your-domain.com` with your actual domain name
4. **Correct Endpoints**: Must match the exact paths defined in your FastAPI app

**Example with real domain:**
```
- Create URL: https://api.mycompany.com/decision/create?instanceId={InstanceId}&installId={InstallId}
- Configure URL: https://api.mycompany.com/decision/configure?instanceId={InstanceId}
- Notification URL: https://api.mycompany.com/decision/notify?instanceId={InstanceId}&executionId={ExecutionId}
- Delete URL: https://api.mycompany.com/decision/delete?instanceId={InstanceId}
```

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

#### Production Considerations

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
