# Real-time Translation Service

A comprehensive multilingual real-time translation service that supports Discord, Zoom, and Google Meet platforms. This service provides seamless translation capabilities for voice and text communication across multiple languages.

## Features

- **Multi-platform Support**: Discord, Zoom, and Google Meet integration
- **Real-time Translation**: Voice and text translation in real-time
- **Multiple Languages**: Support for 10+ languages including English, Russian, Spanish, French, German, Italian, Portuguese, Japanese, Korean, and Chinese
- **Web Interface**: Modern, responsive web dashboard for managing translations
- **Audio Processing**: High-quality speech-to-text and text-to-speech conversion
- **Scalable Architecture**: Docker-based deployment with monitoring and logging

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │    │   Zoom SDK      │    │  Google Meet    │
│                 │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │   Translation Service      │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │   Audio Service     │  │
                    │  │  (Speech-to-Text)   │  │
                    │  └─────────────────────┘  │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │ Translation Engine │  │
                    │  │  (Google Translate)│  │
                    │  └─────────────────────┘  │
                    │                           │
                    │  ┌─────────────────────┐  │
                    │  │   Audio Service     │  │
                    │  │  (Text-to-Speech)   │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │     Web Dashboard         │
                    │   (Management Interface)  │
                    └───────────────────────────┘
```

## Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Audio Processing**: Google Cloud Speech-to-Text, Text-to-Speech
- **Translation**: Google Cloud Translate
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Deployment**: Docker, Docker Compose
- **Monitoring**: Prometheus, Grafana
- **Reverse Proxy**: Nginx

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Cloud Platform account with enabled APIs:
  - Cloud Speech-to-Text API
  - Cloud Text-to-Speech API
  - Cloud Translate API
- Discord Bot Token (for Discord integration)
- Zoom API credentials (for Zoom integration)
- Google OAuth credentials (for Google Meet integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd translation-service
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Web Dashboard: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Grafana Monitoring: http://localhost:3000 (admin/admin)

### Configuration

#### Google Cloud Setup

1. Create a Google Cloud Project
2. Enable the required APIs:
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API
   - Cloud Translate API
3. Create a service account and download the JSON key
4. Place the key file in `credentials/service-account.json`

#### Discord Bot Setup

1. Go to Discord Developer Portal
2. Create a new application
3. Create a bot and copy the token
4. Add the bot to your server with necessary permissions
5. Set `DISCORD_BOT_TOKEN` in your `.env` file

#### Zoom Integration

1. Create a Zoom Marketplace app
2. Get API Key and Secret
3. Set `ZOOM_API_KEY` and `ZOOM_API_SECRET` in your `.env` file

#### Google Meet Integration

1. Create Google Cloud OAuth credentials
2. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in your `.env` file

## Usage

### Web Interface

1. Open http://localhost:8000 in your browser
2. Select source and target languages
3. Click "Start Translation" to begin real-time translation
4. Use the text translation feature for manual translation

### Discord Bot

1. Invite the bot to your Discord server
2. Use the following commands:
   - `!start_translation [source] [target]` - Start translation session
   - `!stop_translation` - Stop translation session
   - `!set_language [source] [target]` - Change languages
   - `!translate [text]` - Translate specific text
   - `!help_translation` - Show help

### API Endpoints

#### Translation
- `POST /api/v1/translate` - Translate text
- `GET /api/v1/languages` - Get supported languages

#### Discord
- `POST /api/v1/discord/start` - Start Discord translation
- `POST /api/v1/discord/stop` - Stop Discord translation

#### Zoom
- `POST /api/v1/zoom/meeting` - Create Zoom meeting
- `POST /api/v1/zoom/join/{meeting_id}` - Join meeting
- `POST /api/v1/zoom/audio/{meeting_id}` - Process audio

#### Google Meet
- `POST /api/v1/meet/meeting` - Create Google Meet
- `POST /api/v1/meet/join/{meeting_id}` - Join meeting
- `POST /api/v1/meet/audio/{meeting_id}` - Process audio

## Development

### Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d db redis
   
   # Run migrations
   alembic upgrade head
   ```

3. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Deployment

### Production Deployment

1. **Set up SSL certificates**
   ```bash
   # Place SSL certificates in ssl/ directory
   ssl/cert.pem
   ssl/key.pem
   ```

2. **Configure environment variables**
   ```bash
   # Set production values in .env
   DEBUG=False
   SECRET_KEY=your-secure-secret-key
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Scaling

The service is designed to be horizontally scalable:

- **Load Balancer**: Use Nginx or HAProxy for load balancing
- **Database**: Use PostgreSQL with read replicas
- **Cache**: Use Redis Cluster for distributed caching
- **Monitoring**: Use Prometheus and Grafana for monitoring

## Monitoring

### Health Checks

- Application: `GET /api/v1/health`
- Database: Connection check
- Redis: Connection check
- External APIs: Google Cloud APIs status

### Metrics

- Translation requests per second
- Audio processing latency
- Translation accuracy
- Error rates
- Resource usage

### Logging

- Application logs: `/app/logs/`
- Access logs: Nginx access logs
- Error logs: Nginx error logs

## Security

- **Authentication**: OAuth2 for Google Meet integration
- **Authorization**: Role-based access control
- **Rate Limiting**: API rate limiting with Nginx
- **SSL/TLS**: HTTPS encryption
- **Input Validation**: Pydantic models for validation
- **SQL Injection**: SQLAlchemy ORM protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Contact the development team

## Roadmap

- [ ] Additional language support
- [ ] Mobile app integration
- [ ] Advanced audio processing
- [ ] Machine learning improvements
- [ ] Enterprise features
- [ ] Multi-tenant support

## Changelog

### v1.0.0
- Initial release
- Discord, Zoom, and Google Meet integration
- Real-time translation support
- Web dashboard
- Docker deployment
- Monitoring and logging