# Wound Care Video Guide System

A Streamlit application for healthcare providers to select wound care treatments and view appropriate instructional videos based on wound type, location, and treatment options.

## Features

- Interactive decision tree for wound care procedures
- Video playback based on selections
- Support for both local video storage and AWS S3
- Docker containerization for easy deployment
- Mobile-friendly design

## Version History

- Initial Commit on 2025-03-09:
   * Base application logic flow and local video playback implemented
   * To Do: Test S3 Integration and Feature Extensions (e.g. LLM Q&A)
   * Application Refactoring to support additional decision paths. Improve modularization.

## Project Structure

```
wound-care-guide-app/
│
├── app/                    # Application code
│   ├── app.py              # Main Streamlit application
│   ├── utils.py            # Helper functions
│   ├── config.py           # Configuration management
│   ├── generate_placeholders.py  # Script to create placeholder videos
│   └── static/             # Static assets
│       └── videos/         # Local video storage
│
├── videos/                 # Video mount point for Docker volume
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── requirements.txt        # Python dependencies
```

## Installation and Setup

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd wound-care-guide-app
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Generate placeholder videos:
```bash
python app/generate_placeholders.py
```

4. Run the application:
```bash
streamlit run app/app.py
```

### Docker Deployment

1. Build and start the Docker container:
```bash
docker-compose up -d
```

2. Access the application at http://localhost:8501

## AWS S3 Integration

To use AWS S3 for video storage:

1. Edit the environment variables in `docker-compose.yml`:
```yaml
environment:
  - USE_S3=True
  - S3_BUCKET_NAME=your-bucket-name
  - AWS_ACCESS_KEY_ID=your-access-key
  - AWS_SECRET_ACCESS_KEY=your-secret-key
  - AWS_REGION=your-region
```

2. Upload videos to your S3 bucket with the following guidelines:

   - **Naming Convention**: Files should be named as `video_X_Y_Z.mp4` or `video_X_Y_Z.mov`, where X_Y_Z corresponds to reference numbers in the flowchart
     - Example: `video_2_1_1.mp4` for reference "2.1.1" (Sheet Dressing Application)
     - Example: `video_4_0_0.mov` for reference "4.0" (Tubifast to Secure)
   
   - **Supported Formats**: Both `.mp4` and `.mov` files are supported
     - **Format Priority**: If both `.mp4` and `.mov` versions exist for the same reference, the `.mp4` version will be used
     - This priority applies to both local storage and S3 storage
   
   - **Required Video References**:
     - `2.1.1`: Sheet Dressing Application
     - `2.1.2`: Iodosorb Powder/Gels Application
     - `2.2.1`: Primary Dressing for Cavity Wounds
     - `2.3`: Webspace Wound Treatment
     - `2.4`: Multiple Toe Wounds with Inadine
     - `2.5`: Wounds for Povidone Iodine Soaked Gauze
     - `3.1`: Toes Location Treatment
     - `3.2`: Mid Foot/Ankle Location Treatment
     - `3.3`: Heel Location Treatment
     - `4.0`: Tubifast to Secure
     - `5.0`: Things to Watch Out For

## Decision Flow

The application follows a decision tree based on:

1. Type of wound:
   - Superficial Wound
   - Cavity/Concave Wound
   - Webspace Wound
   - Multiple toe wounds with inadine
   - Wounds for povidone iodine soaked gauze

2. Location of wound (for Superficial and Cavity wounds):
   - Toes
   - Mid foot/ankle
   - Heel

3. Primary dressing type (for Superficial wounds):
   - Sheet dressing
   - Iodosorb powder/Gels

4. All treatments end with:
   - Secondary dressing according to location
   - Tubifast to secure
   - Things to watch out for

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

[Specify your license]
