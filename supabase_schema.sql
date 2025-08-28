-- Create market_data table
CREATE TABLE market_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    volume BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    indicators JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create trades table
CREATE TABLE trades (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL CHECK (direction IN ('BUY', 'SELL')),
    entry_price DECIMAL(10,2) NOT NULL,
    exit_price DECIMAL(10,2),
    quantity INTEGER NOT NULL,
    signal_strength DECIMAL(3,2),
    pnl DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'OPEN',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create portfolio table
CREATE TABLE portfolio (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset VARCHAR(50) NOT NULL UNIQUE,
    quantity INTEGER NOT NULL,
    average_price DECIMAL(10,2) NOT NULL,
    current_price DECIMAL(10,2),
    total_value DECIMAL(15,2),
    unrealized_pnl DECIMAL(10,2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create signals table
CREATE TABLE signals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset VARCHAR(50) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,
    strength DECIMAL(3,2),
    price_target DECIMAL(10,2),
    stop_loss DECIMAL(10,2),
    confidence DECIMAL(3,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed BOOLEAN DEFAULT FALSE
);

-- Create performance_metrics table
CREATE TABLE performance_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_trades INTEGER DEFAULT 0,
    profitable_trades INTEGER DEFAULT 0,
    total_pnl DECIMAL(10,2) DEFAULT 0,
    win_rate DECIMAL(5,2),
    sharpe_ratio DECIMAL(5,2),
    max_drawdown DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create model_predictions table
CREATE TABLE model_predictions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    asset VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    prediction VARCHAR(10) NOT NULL,
    probability DECIMAL(3,2),
    actual_outcome VARCHAR(10),
    accuracy DECIMAL(3,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_market_data_asset_timestamp ON market_data(asset, timestamp DESC);
CREATE INDEX idx_trades_asset_timestamp ON trades(asset, timestamp DESC);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_signals_asset_timestamp ON signals(asset, timestamp DESC);
CREATE INDEX idx_performance_metrics_date ON performance_metrics(date);

-- Enable Row Level Security (RLS)
ALTER TABLE market_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_predictions ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (allow all for now)
CREATE POLICY "Allow all operations" ON market_data FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON trades FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON portfolio FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON signals FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON performance_metrics FOR ALL USING (true);
CREATE POLICY "Allow all operations" ON model_predictions FOR ALL USING (true);