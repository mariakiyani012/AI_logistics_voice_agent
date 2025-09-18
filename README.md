# AI Voice Agent for Logistics

A full-stack web application that allows administrators to configure, test, and review calls made by an adaptive AI voice agent for logistics operations. The system handles driver check-ins, emergency protocols, and provides structured data extraction from call transcripts.

## Features

- **Agent Configuration**: Create and manage AI voice agents with custom prompts and voice settings
- **Call Triggering**: Initiate test calls to drivers with load-specific context
- **Call History**: Review completed calls with transcripts and structured summaries
- **Real-time Processing**: Live conversation handling with dynamic response generation
- **Emergency Detection**: Automatic escalation for emergency situations
- **Structured Data Extraction**: AI-powered analysis of call outcomes and driver status

## Technology Stack

**Backend:**
- FastAPI (Python)
- Supabase (PostgreSQL)
- OpenAI GPT-4 for conversation logic
- Retell AI for voice calling
- Pydantic for data validation

**Frontend:**
- React 18
- Axios for API communication
- Lucide React for icons
- Custom CSS (Tailwind-compatible classes)

## Project Structure

```
AI_logistics_voice_agent/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings and environment
│   │   ├── database.py          # Supabase client and operations
│   │   ├── models.py            # Pydantic data models
│   │   ├── routers/
│   │   │   ├── agent.py         # Agent CRUD endpoints
│   │   │   ├── calls.py         # Call management endpoints
│   │   │   └── webhook.py       # Retell AI webhooks
│   │   └── services/
│   │       ├── retell_service.py    # Retell AI integration
│   │       ├── openai_service.py    # OpenAI conversation logic
│   │       └── data_processor.py    # Post-call processing
│   └── requirements.txt
├── frontend/
|   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── AgentConfig.jsx      # Agent configuration UI
│   │   │   ├── CallTrigger.jsx      # Call initiation form
│   │   │   ├── CallHistory.jsx      # Call results display
│   │   │   └── Dashboard.jsx        # Main layout
│   │   ├── services/
│   │   │   └── api.js               # API client
|   |   ├── App.jsx
|   |   ├── index.css
│   │   └── index.js
│   └── package.json
└── database/
    └── schema.sql               # Database schema
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Supabase account
- OpenAI API key
- Retell AI account

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment configuration:**
   ```bash
   cp .env.example .env
   ```
   
   Update `.env` with your API keys:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   OPENAI_API_KEY=your_openai_key
   RETELL_API_KEY=your_retell_key
   WEBHOOK_BASE_URL=http://localhost:8000
   ```

3. **Database setup:**
   - Create a new Supabase project
   - Run the SQL commands from `database/schema.sql` in your Supabase SQL editor

4. **Start the backend:**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the frontend:**
   ```bash
   npm start
   ```
   
   Frontend will be available at `http://localhost:3000`

## Usage

### 1. Configure an Agent

Navigate to the "Agent Config" tab and create a new agent:
- **Name**: Descriptive name for your agent
- **System Prompt**: Must include `{driver_name}` and `{load_number}` placeholders
- **Scenario Type**: Choose between "dispatch" or "emergency"
- **Voice Settings**: Configure voice characteristics

### 2. Trigger a Call

Use the "Trigger Call" tab to start a test call:
- Select an agent configuration
- Enter driver details (name, phone, load number)
- Click "Start Test Call"

### 3. Review Results

Check the "Call History" tab to:
- View all completed calls
- Access full transcripts
- See structured data summaries
- Review call outcomes and driver status

## API Endpoints

### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{id}` - Get specific agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Calls
- `POST /api/calls/trigger` - Start new call
- `GET /api/calls` - List call history
- `GET /api/calls/{id}` - Get call details
- `GET /api/calls/{id}/summary` - Get structured summary

### Webhooks
- `POST /webhook/retell` - Retell AI webhook handler

## Data Models

### Agent Configuration
```json
{
  "name": "Dispatch Agent",
  "system_prompt": "Hi {driver_name}, calling about load {load_number}...",
  "scenario_type": "dispatch",
  "voice_settings": {
    "voice": "female",
    "speed": 1.0,
    "interruption_sensitivity": 0.5
  }
}
```

### Structured Call Summary
```json
{
  "call_outcome": "In-Transit Update",
  "driver_status": "Driving",
  "current_location": "I-10 near Indio, CA",
  "eta": "Tomorrow, 8:00 AM",
  "structured_data": { ... }
}
```

## Development

### Testing Backend
Visit `http://localhost:8000/docs` for interactive API documentation.

### Testing Database Connection
```bash
curl http://localhost:8000/test-db
```

### Viewing Logs
Backend logs provide detailed information about:
- API requests and responses
- Database operations
- External service calls (Retell AI, OpenAI)
- Error handling

## Supported Scenarios

### Scenario 1: Driver Check-in
- Agent asks for status update
- Collects location and ETA information
- Handles delayed or arrived statuses

### Scenario 2: Emergency Protocol
- Detects emergency keywords
- Immediately switches to emergency mode
- Collects emergency type and location
- Flags for human dispatcher escalation

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify Supabase URL and service role key
   - Check database schema is properly created

2. **OpenAI API Errors**
   - Ensure API key has sufficient credits
   - Check rate limits

3. **Retell AI Integration**
   - Verify webhook URL is publicly accessible
   - Check Retell AI dashboard configuration

4. **Frontend API Errors**
   - Ensure backend is running on port 8000
   - Check CORS configuration

### Development Tips

- Use `/docs` endpoint for API testing
- Monitor backend logs for debugging
- Test database operations with `/test-db` endpoint
- Use browser dev tools to inspect API calls

## Architecture Decisions

### Modular Backend Structure
- Separate routers for different API concerns
- Service layer for external integrations
- Database abstraction for easy testing

### Real-time Processing
- Webhook-based integration with Retell AI
- Asynchronous processing of call transcripts
- Structured data extraction using OpenAI

### Error Handling
- Comprehensive logging throughout the system
- Graceful fallbacks for external service failures
- User-friendly error messages in the UI

## Future Enhancements

- Real-time call status updates
- Advanced analytics dashboard
- Multiple agent configurations per scenario
- Call recording playback
- Integration with dispatch management systems

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for demonstration purposes and uses various third-party services. Ensure you comply with the terms of service for OpenAI, Retell AI, and Supabase when deploying.