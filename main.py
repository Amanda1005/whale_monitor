# main.py (正確版本)

import time
from monitor import OpenInterestMonitor
from telegram_bot import TelegramBot
from config import CHECK_INTERVAL, OI_CHANGE_THRESHOLD

def main():
    print("🚀 Open Interest Monitor Started!")
    print(f"⏱️  Check interval: {CHECK_INTERVAL}s")
    print(f"💰 OI change threshold: ${OI_CHANGE_THRESHOLD/1e6:,.0f}M")
    print("-" * 50)
    
    monitor = OpenInterestMonitor()
    bot = TelegramBot()
    
    # Warm-up
    print("\n🔄 Establishing baseline...")
    monitor.scan()
    print(f"✅ Baseline established\n")
    
    while True:
        try:
            alerts = monitor.scan()
            
            if alerts:
                print(f"\n🔔 Found {len(alerts)} OI changes!")
                for alert in alerts:
                    bot.send_alert(alert)
                    time.sleep(1)
            else:
                print(f"✅ No significant OI changes")
            
            print(f"😴 Sleeping {CHECK_INTERVAL}s...\n")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()