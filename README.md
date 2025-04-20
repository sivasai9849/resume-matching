# Resume Ranking System

An AI-powered recruitment platform that automates candidate-job matching with WhatsApp integration.

## Project Overview

The Resume Ranking System streamlines the recruitment process by leveraging artificial intelligence to analyze job descriptions and candidate resumes, automatically matching candidates with suitable job opportunities. The system features WhatsApp integration for seamless communication, allowing candidates to receive job notifications and submit resumes directly through WhatsApp.

### Key Features

- **AI-Powered Matching**: Automatically rank candidates based on skill compatibility, experience, and qualifications
- **WhatsApp Integration**: Send job notifications and receive resumes via WhatsApp
- **Resume Parsing**: Extract structured information from PDF and DOCX resumes
- **Job Analysis**: Process job descriptions to identify key requirements and skills
- **Candidate Management**: Track and manage candidate profiles and interactions
- **Recruiter Dashboard**: Visualize matching results and recruitment metrics

## System Architecture

The application is built on a microservices architecture with four main components:

```
┌─────────────────────────────────┐
│         Frontend (Next.js)      │
│                                 │
│  - Job listings                 │
│  - Candidate management         │
│  - Resume uploads               │
│  - Matching results             │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│       Backend API (Flask)       │
│                                 │
│  - Job management               │
│  - Candidate management         │
│  - Matching processing          │
│  - WhatsApp notifications       │
└──────┬──────────────────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────────┐
│  MongoDB     │   │ Analysis Service │
│  Database    │   │    (FastAPI)     │
│              │   │                  │
│ - Jobs       │   │ - Resume parsing │
│ - Candidates │   │ - Job analysis   │
│ - Matches    │   │ - AI matching    │
└──────────────┘   └──────────────────┘
```

## Technology Stack

### Frontend
- **Next.js**: React framework for server-side rendering
- **Material UI**: Component library for UI design
- **TanStack Query**: Data fetching and state management
- **Axios**: HTTP client for API communication

### Backend API
- **Flask**: Python web framework
- **Flask-RESTful**: Extension for building REST APIs
- **PyMongo**: MongoDB client for Python
- **Twilio**: WhatsApp messaging integration
- **JWT**: Authentication and authorization

### Analysis Service
- **FastAPI**: High-performance Python web framework
- **OpenAI/Azure AI**: Natural language processing for analysis
- **PyPDF2/python-docx**: Document parsing libraries
- **Scikit-learn**: Machine learning for matching algorithm

### Database
- **MongoDB**: NoSQL database for flexible data storage

### DevOps
- **Docker**: Container platform for consistent deployment
- **GitHub Actions**: CI/CD pipeline
- **Nginx**: Web server and reverse proxy

## Application Flow

1. **Candidate Journey**:
   - Candidates register in the system by admin
   - Upload resumes through WhatsApp
   - Receive WhatsApp notifications about new job opportunities
   - Can send updated resumes via WhatsApp for new job applications

2. **Job Posting Process**:
   - Recruiters create job listings with details and requirements
   - System analyzes job descriptions using NLP
   - System notifies candidates about new jobs via WhatsApp
   - Custom message removes HTML tags from job descriptions for clean WhatsApp display

3. **Resume Processing**:
   - Resumes uploaded via web UI or WhatsApp are analyzed
   - Analysis service extracts key information and skills
   - System stores parsed candidate data in MongoDB
   - Flags candidates with "has_resume" status

4. **Matching Algorithm**:
   - When matching is requested, backend calls analysis service
   - AI-powered analysis compares job requirements with candidate skills
   - Generates compatibility scores and rankings
   - Results stored in database and displayed in UI
   - Sends shortlisted messages to candidates on trigger

5. **WhatsApp Integration**:
   - Twilio handles WhatsApp communication
   - Candidates can receive notifications about new jobs
   - Candidates can submit resumes directly via WhatsApp
   - System recognizes existing candidates by phone number
   - WhatsApp webhook processes incoming messages and files

## Getting Started

### Prerequisites

- Node.js (v16+)
- Python (v3.8+)
- MongoDB (v4.4+)
- Docker and Docker Compose
- Twilio Account with WhatsApp Business API access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resume-ranking.git
   cd resume-ranking
   ```

2. Start the services using Docker Compose:
   ```bash
   docker-compose up
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - Analysis Service: http://localhost:8000

### Configuration

Create a `.env` file in the root directory with the following variables:

```
# MongoDB
MONGO_URI=mongodb://mongodb:27017/resume_ranking

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_whatsapp_number

# OpenAI/Azure
OPENAI_API_KEY=your_openai_api_key

# JWT
JWT_SECRET=your_jwt_secret
JWT_EXPIRATION=3600
```

## Documentation

For detailed documentation, see the [docs](./docs) directory:

- [System Documentation](./docs/Resume_Ranking_System_Documentation.md)
- [Presentation Slides](./docs/Resume_Ranking_System_Presentation.md)

## Project Structure

```
resume-ranking/
├── frontend/                 # Next.js frontend application
├── backend/                  # Flask backend API
├── analysis/                 # FastAPI analysis service
├── docker/                   # Docker configuration files
├── docs/                     # Documentation
├── docker-compose.yml        # Multi-container Docker configuration
├── .github/                  # GitHub Actions workflows
└── README.md                 # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAI](https://openai.com/) for NLP capabilities
- [Twilio](https://www.twilio.com/) for WhatsApp Business API
- All contributors to the open source libraries used in this project 