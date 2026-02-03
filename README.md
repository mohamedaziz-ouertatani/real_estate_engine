# 🏠 Tunisia Real Estate AI Predictor

An intelligent real estate pricing engine for the Tunisian market, powered by machine learning and natural language processing. This system scrapes listings from popular Tunisian real estate platforms, extracts features using NLP, and predicts market values using trained ML models.

## 🌟 Features

- **Multi-Platform Scraping**: Supports Facebook Marketplace, Tayara, and Tunisie-Annonce
- **AI-Powered Price Prediction**: Machine learning models trained on Tunisian real estate data
- **Smart Category Detection**: Automatically classifies properties (Residential, Land, Rental, Commercial)
- **NLP Feature Extraction**: Extracts property details from unstructured text descriptions
- **Interactive Web UI**: Beautiful Streamlit interface with dark theme
- **Deal Analysis**: Identifies overpriced and great deals based on market data
- **Explainable AI**: Feature importance visualization to understand pricing factors
- **Performance Optimized**: Model caching, pre-compiled patterns, and efficient data processing

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/mohamedaziz-ouertatani/real_estate_engine.git
cd real_estate_engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers (for web scraping):
```bash
playwright install
```

### Usage

#### Option 1: Full-Featured UI (Recommended)
```bash
streamlit run app.py
```

Features:
- Complete explainability dashboard
- Feature importance visualization
- Raw metadata inspection
- Advanced styling and dark theme

#### Option 2: Simple UI
```bash
streamlit run main.py
```

A simplified interface for quick price predictions.

### How to Use

1. Launch the Streamlit app
2. Paste a listing URL from:
   - Facebook Marketplace
   - Tayara.tn
   - Tunisie-Annonce.com
3. (Optional) Select a market model override
4. Click "Run AI Analysis"
5. View the AI-predicted market value vs listing price

## 📁 Project Structure

```
real_estate_engine/
├── app.py                  # Full-featured Streamlit UI
├── main.py                 # Simple Streamlit UI
├── config.yaml             # Configuration settings
├── requirements.txt        # Python dependencies
├── pytest.ini             # Test configuration
│
├── engine/                 # Core prediction engine
│   ├── engine.py          # Main UnifiedPredictionEngine
│   ├── features.py        # Feature engineering
│   ├── router.py          # Model routing logic
│   ├── category.py        # Category detection
│   └── deal.py            # Deal quality assessment
│
├── scrapers/              # Web scraping modules
│   ├── base.py           # Base scraper class
│   ├── facebook.py       # Facebook Marketplace scraper
│   ├── tayara.py         # Tayara.tn scraper
│   └── tunisie_annonce.py # Tunisie-Annonce scraper
│
├── models/                # Trained ML models (joblib)
│   ├── residential_*.pkl
│   ├── land_*.pkl
│   ├── rental_*.pkl
│   └── commercial_*.pkl
│
├── utils/                 # Utility functions
│   ├── amenities.py      # Centralized amenity detection
│   ├── nlp.py            # NLP entity extraction
│   ├── text.py           # Text processing utilities
│   ├── feature_importance.py  # Model explainability
│   └── visualization.py  # Plotting utilities
│
├── data/                  # Training data
├── train/                 # Training scripts
└── tests/                 # Unit tests
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
paths:
  dataset: data/checkpoint_page_730.csv
  models_dir: models/

model:
  bedroom_cap: 10
  rental_price_threshold: 20000
  min_samples_per_category: 10

defaults:
  missing_value: "Missing"
  currency: "TND"
```

## 🧪 Testing

Run the test suite:
```bash
pytest
```

Run specific test files:
```bash
pytest tests/test_engine_load.py
pytest tests/test_optimizations.py
```

## 🔧 Technical Stack

### Core Technologies
- **Python 3.8+**: Main programming language
- **Streamlit**: Interactive web interface
- **scikit-learn**: Machine learning models
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing

### Web Scraping
- **Playwright**: Browser automation
- **BeautifulSoup4**: HTML parsing

### Visualization
- **Plotly**: Interactive charts and graphs

### Model Persistence
- **joblib**: Efficient model serialization

## 🤖 How It Works

1. **URL Detection**: Identifies the platform (Facebook, Tayara, Tunisie-Annonce)
2. **Web Scraping**: Extracts listing data using Playwright and BeautifulSoup
3. **NLP Processing**: Extracts entities (location, surface, rooms) from descriptions
4. **Feature Engineering**: Constructs feature vectors for ML models
5. **Category Detection**: Classifies property type (Residential/Land/Rental/Commercial)
6. **Model Selection**: Routes to appropriate trained model
7. **Price Prediction**: Generates AI market value estimate
8. **Deal Analysis**: Compares predicted vs listed price

## 📊 Model Categories

- **Residential**: Houses, apartments, villas for sale
- **Land**: Plots, terrains, agricultural land
- **Rental**: Properties for rent
- **Commercial**: Offices, warehouses, commercial spaces

## 🎯 Performance Features

The engine includes several optimizations (see `OPTIMIZATION_SUMMARY.md`):

- **Model Caching**: Models loaded once per process
- **Pre-compiled Regex**: 20x faster text processing
- **Centralized Amenity Detection**: DRY principle applied
- **Lazy NLP Evaluation**: Only when needed
- **Pre-sorted Geo-Mapping**: Faster location matching
- **Optimized DataFrame Operations**: Single-pass construction

## 🛠️ Development

### Adding a New Scraper

1. Create a new file in `scrapers/`
2. Inherit from `BaseScraper`
3. Implement `scrape()` method
4. Update URL pattern detection in `UnifiedPredictionEngine`

### Training Models

Place your dataset in `data/` and run training scripts in `train/` directory.

## 🐛 Troubleshooting

### Playwright Browser Issues
```bash
playwright install chromium
```

### Windows Async Issues
The app automatically handles Windows async policy. No action needed.

### Scraping Failures
- Check internet connection
- Verify URL format
- Some sites may block automated access

## 📝 License

This project is for educational and research purposes.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Trained on Tunisian real estate market data
- Optimized for Tunisia-specific location names and property types
- 2026 Edition with latest Streamlit features

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ for the Tunisian Real Estate Market**
