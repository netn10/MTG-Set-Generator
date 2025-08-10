# Deployment Guide

## 🚀 GitHub Repository
Your MTG Set Generator is now deployed at: **https://github.com/netn10/MTG-Set-Generator**

## 📋 Deployment Options

### 1. Local Development
```bash
# Clone the repository
git clone https://github.com/netn10/MTG-Set-Generator.git
cd MTG-Set-Generator

# Run setup script
./setup.sh  # Linux/Mac
setup.bat   # Windows

# Start the application
./start.sh  # Linux/Mac
start.bat   # Windows
```

### 2. Heroku Deployment

#### Prerequisites
- Heroku CLI installed
- Heroku account

#### Steps
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-mtg-generator

# Set environment variables
heroku config:set OPENAI_API_KEY=your_openai_api_key_here

# Deploy
git push heroku main

# Open your app
heroku open
```

#### Heroku Configuration Files Needed
Create `Procfile` in root:
```
web: cd backend && python app.py
```

Create `runtime.txt` in root:
```
python-3.9.18
```

### 3. Vercel Deployment (Frontend Only)

#### Prerequisites
- Vercel CLI or Vercel account

#### Steps
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

#### Backend API Routes
For full functionality, deploy backend separately and update API endpoints in frontend.

### 4. Railway Deployment

#### Prerequisites
- Railway account

#### Steps
1. Connect your GitHub repository to Railway
2. Set environment variable: `OPENAI_API_KEY`
3. Deploy automatically on push to main

### 5. DigitalOcean App Platform

#### Prerequisites
- DigitalOcean account

#### Steps
1. Create new app from GitHub repository
2. Configure build settings:
   - **Backend**: Python, `cd backend && python app.py`
   - **Frontend**: Node.js, `cd frontend && npm run build`
3. Set environment variables
4. Deploy

## 🔧 Environment Variables

### Required
- `OPENAI_API_KEY`: Your OpenAI API key for card generation

### Optional
- `PORT`: Server port (default: 5000)
- `NODE_ENV`: Environment mode (development/production)

## 📦 Build Process

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm run build  # Production build
npm start      # Development server
```

## 🔄 Continuous Deployment

GitHub Actions workflow is configured to:
1. Test backend and frontend on every push
2. Build production assets
3. Deploy to your chosen platform

## 🐛 Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

#### API connection issues
- Check OPENAI_API_KEY is set correctly
- Verify backend is running on correct port
- Update frontend API endpoints if needed

#### Build failures
- Ensure Node.js 16+ and Python 3.8+ are installed
- Clear caches: `npm cache clean --force`
- Delete node_modules and reinstall

## 📊 Monitoring

### Health Checks
- Backend: `GET /api/health`
- Frontend: Check if React app loads

### Logs
- Backend: Check server logs for API errors
- Frontend: Check browser console for client errors

## 🔒 Security

### Production Checklist
- [ ] Environment variables are secure
- [ ] API keys are not committed to repository
- [ ] HTTPS is enabled
- [ ] CORS is properly configured
- [ ] Rate limiting is implemented

## 📈 Scaling

### Performance Optimization
- Enable gzip compression
- Use CDN for static assets
- Implement caching for API responses
- Consider database for card storage

### Load Balancing
- Use multiple backend instances
- Implement Redis for session storage
- Consider microservices architecture

## 🎯 Next Steps

1. **Set up monitoring** (e.g., Sentry, LogRocket)
2. **Add analytics** (e.g., Google Analytics)
3. **Implement user authentication**
4. **Add database persistence**
5. **Create mobile-responsive design**

## 📞 Support

For deployment issues:
1. Check GitHub Issues
2. Review deployment logs
3. Verify environment configuration
4. Test locally first

Your MTG Set Generator is now ready for the world! 🎉