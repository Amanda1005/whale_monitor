import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID  # 從 config 導入

class TelegramBot:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"  # 使用變數！
    
    def send_alert(self, alert):
        """發送 OI 變化 alert"""
        
        if alert["signal"] == "Bullish":
            title = "✅ Large Position Opening - BULLISH"
        elif alert["signal"] == "Bearish":
            title = "⚠️ Large Position Opening - BEARISH"
        else:
            title = "📊 Open Interest Change"
        
        change_m = abs(alert['oi_change']) / 1e6
        prev_b = alert['previous_oi'] / 1e9
        curr_b = alert['current_oi'] / 1e9
        
        message = f"""<b>{title}</b>

🪙 Asset: {alert['coin']}
{alert['emoji']} OI Change: ${change_m:,.0f}M ({alert['oi_change_pct']:+.2f}%)

📊 Open Interest:
  Previous: ${prev_b:.2f}B
  Current: ${curr_b:.2f}B

💹 Market Signal: {alert['signal']}
📍 {alert['bias']}

💰 Price: ${alert['price']:,.2f}
⏰ {alert['timestamp']}
"""
        
        if alert.get('ls_ratio'):
            ls = alert['ls_ratio']
            message += f"\n🎯 Long/Short: {ls['long_pct']:.1f}% / {ls['short_pct']:.1f}%"
        
        params = {
            "chat_id": TELEGRAM_CHAT_ID,  # 使用變數！
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=params, timeout=10)
            if response.status_code == 200:
                print(f"✅ Sent alert: {alert['coin']} OI change")
                return True
            else:
                print(f"❌ Failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    bot = TelegramBot()
    
    test_alert = {
        "coin": "BTC",
        "trend": "increasing",
        "emoji": "📈",
        "signal": "Bullish",
        "bias": "Long-biased (58.5% longs)",
        "previous_oi": 45_000_000_000,
        "current_oi": 45_650_000_000,
        "oi_change": 650_000_000,
        "oi_change_pct": 1.44,
        "price": 89_322.5,
        "ls_ratio": {"long": 0.585, "short": 0.415, "long_pct": 58.5, "short_pct": 41.5},
        "timestamp": "2026-01-21 21:00:00"
    }
    
    bot.send_alert(test_alert)