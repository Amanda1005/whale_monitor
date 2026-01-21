import requests
import time
from datetime import datetime
from config import WATCH_COINS, OI_CHANGE_THRESHOLD

class OpenInterestMonitor:
    def __init__(self):
        self.binance_api = "https://fapi.binance.com/fapi/v1"
        self.oi_history = {}  # 記錄歷史 OI
        
    def get_symbol_map(self, coin):
        """幣種映射到 Binance 合約代號"""
        mapping = {
            "BTC": "BTCUSDT",
            "ETH": "ETHUSDT",
            "SOL": "SOLUSDT"
        }
        return mapping.get(coin, f"{coin}USDT")
    
    def get_open_interest(self, symbol):
        """獲取 Open Interest"""
        try:
            # 獲取 OI（以合約數量）
            url = f"{self.binance_api}/openInterest"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            oi_amount = float(data.get("openInterest", 0))
            
            # 獲取當前價格
            price = self.get_price(symbol)
            
            # 計算 OI 美元價值
            oi_value = oi_amount * price
            
            return {
                "amount": oi_amount,
                "value": oi_value,
                "price": price
            }
        except Exception as e:
            print(f"❌ OI Error for {symbol}: {e}")
            return None
    
    def get_price(self, symbol):
        """獲取當前價格"""
        try:
            url = f"{self.binance_api}/ticker/price"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return float(data.get("price", 0))
        except:
            return 0
    
    def get_long_short_ratio(self, symbol):
        """獲取多空比"""
        try:
            url = f"{self.binance_api}/globalLongShortAccountRatio"
            params = {
                "symbol": symbol,
                "period": "5m"  # 5 分鐘數據
            }
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data and len(data) > 0:
                latest = data[-1]
                long_ratio = float(latest.get("longAccount", 0.5))
                short_ratio = float(latest.get("shortAccount", 0.5))
                return {
                    "long": long_ratio,
                    "short": short_ratio,
                    "long_pct": long_ratio * 100,
                    "short_pct": short_ratio * 100
                }
            return None
        except Exception as e:
            print(f"⚠️ Long/Short ratio not available for {symbol}")
            return None
    
    def analyze_oi_change(self, coin, current_oi):
        """分析 OI 變化"""
        symbol = self.get_symbol_map(coin)
        
        # 第一次記錄，不推送
        if coin not in self.oi_history:
            self.oi_history[coin] = current_oi
            return None
        
        previous_oi = self.oi_history[coin]
        oi_change = current_oi["value"] - previous_oi["value"]
        if previous_oi["value"] == 0:
            print(f"⚠️ Previous OI is zero for {coin}, skipping")
            self.oi_history[coin] = current_oi
            return None

        oi_change_pct = (oi_change / previous_oi["value"]) * 100
        
        # 更新歷史
        self.oi_history[coin] = current_oi
        
        # 變化不大，不推送
        if abs(oi_change) < OI_CHANGE_THRESHOLD:
            return None
        
        # 獲取多空比
        ls_ratio = self.get_long_short_ratio(symbol)
        
        # 判斷信號
        if oi_change > 0:
            trend = "increasing"
            emoji = "📈"
            if ls_ratio and ls_ratio["long"] > 0.55:
                signal = "Bullish"
                bias = f"Long-biased ({ls_ratio['long_pct']:.1f}% longs)"
            elif ls_ratio and ls_ratio["short"] > 0.55:
                signal = "Bearish"
                bias = f"Short-biased ({ls_ratio['short_pct']:.1f}% shorts)"
            else:
                signal = "Neutral"
                bias = "Balanced positioning"
        else:
            trend = "decreasing"
            emoji = "📉"
            signal = "Position Closing"
            bias = "Traders closing positions"
        
        return {
            "coin": coin,
            "trend": trend,
            "emoji": emoji,
            "signal": signal,
            "bias": bias,
            "previous_oi": previous_oi["value"],
            "current_oi": current_oi["value"],
            "oi_change": oi_change,
            "oi_change_pct": oi_change_pct,
            "price": current_oi["price"],
            "ls_ratio": ls_ratio,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def scan(self):
        """掃描所有幣種的 OI"""
        print(f"🔍 Scanning Open Interest...")
        alerts = []
        
        for coin in WATCH_COINS:
            symbol = self.get_symbol_map(coin)
            print(f"Checking {coin}...")
            
            oi_data = self.get_open_interest(symbol)
            if oi_data:
                print(f"  OI: ${oi_data['value']/1e9:.2f}B at ${oi_data['price']:,.2f}")
                
                alert = self.analyze_oi_change(coin, oi_data)
                if alert:
                    alerts.append(alert)
            
            time.sleep(0.5)
        
        return alerts

if __name__ == "__main__":
    monitor = OpenInterestMonitor()
    
    print("=== Testing Open Interest Monitor ===\n")
    
    # 第一次掃描（建立基線）
    print("First scan (baseline):")
    monitor.scan()
    
    print("\n⏳ Waiting 10 seconds...\n")
    time.sleep(10)
    
    # 第二次掃描（檢測變化）
    print("Second scan (check changes):")
    results = monitor.scan()
    
    print(f"\n📊 Found {len(results)} alerts:")
    for alert in results:
        print(f"\n{alert['emoji']} {alert['coin']} OI {alert['trend']}")
        print(f"Change: ${alert['oi_change']/1e6:,.1f}M ({alert['oi_change_pct']:+.2f}%)")
        print(f"Signal: {alert['signal']}")