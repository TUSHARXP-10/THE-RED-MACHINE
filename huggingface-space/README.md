---
sdk: docker
app_file: app.py
---

# Cash Flow Prediction API - Hugging Face Space

This is a FastAPI-based cash flow prediction API deployed as a Hugging Face Space. It provides real-time predictions based on financial market features.

## 🚀 Quick Start

### Deploy to Hugging Face Spaces

1. **Create Hugging Face Account**: Sign up at [huggingface.co](https://huggingface.co)

2. **Create New Space**:
   - Go to [huggingface.co/spaces](https://huggingface.co/spaces)
   - Click "Create New Space"
   - Choose:
     - **Space name**: `cashflow-prediction-api`
     - **Space template**: Docker
     - **Visibility**: Public (for demo) or Private

3. **Upload Files**:
   - Upload all files from this directory to your Space
   - Or connect to GitHub repository

4. **Deploy**:
   - Space will automatically build and deploy
   - Wait 2-3 minutes for build to complete

### 🧪 Testing the API

Once deployed, test with these endpoints:

**Health Check**:
```bash
curl https://your-username-cashflow-prediction-api.hf.space/health
```

**Get Sample Input**:
```bash
curl https://your-username-cashflow-prediction-api.hf.space/sample
```

**Make Prediction**:
```bash
curl -X POST "https://your-username-cashflow-prediction-api.hf.space/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "data": {
         "stock_price": 150.0,
         "volatility": 0.15,
         "volume": 1000000,
         "sma_20": 145.0,
         "rsi": 65.0
       }
     }'
```

### 📊 API Endpoints

- `GET /` - API information and status
- `GET /health` - Health check endpoint
- `GET /sample` - Get sample input data
- `POST /predict` - Make predictions with financial features

### 🛠️ Development

**Local Testing**:
```bash
cd huggingface-space
docker build -t cashflow-api .
docker run -p 7860:7860 cashflow-api
```

**Access locally**: http://localhost:7860

### 🔧 Configuration

The API uses a fallback RandomForest model by default. To use your production model:

1. Upload your trained model as `models/rf_model.pkl`
2. The API will automatically use it instead of the fallback

### 📈 Features

- **Real-time predictions** for cash flow based on market features
- **Risk assessment** with risk flags and position sizing
- **Health monitoring** with dedicated health check endpoint
- **Sample data** for easy testing
- **Production-ready** with fallback model support

### 🚨 Limitations

- **Model**: Uses fallback RandomForest model if no production model provided
- **Storage**: Limited to Hugging Face Space constraints (2GB)
- **Compute**: Free tier CPU only (upgrade available)
- **Persistence**: No persistent database storage

### 🤝 Support

For issues or questions:
1. Check the logs in your Hugging Face Space dashboard
2. Test locally with Docker first
3. Verify model files are correctly placed in `models/` directory