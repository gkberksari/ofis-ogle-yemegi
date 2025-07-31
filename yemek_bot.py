import requests
import json
import os
from datetime import datetime
from typing import Dict, Optional

class OfisYemekBot:
    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.slack_channel = os.getenv('SLACK_CHANNEL', '#yemek')
        self.test_date = os.getenv('TEST_DATE', '')
        
        # Bugünün tarihini al (veya test tarihi)
        if self.test_date:
            self.today = datetime.strptime(self.test_date, '%Y-%m-%d')
        else:
            self.today = datetime.now()
            
        print(f"🍽️ Ofis Yemek Bot başlatıldı - {self.today.strftime('%d.%m.%Y %A')}")
        
    def load_menu_data(self) -> Dict:
        """JSON'dan yemek menüsü verilerini yükle"""
        try:
            json_files = [
                'data/yemek_menusu.json',
                'yemek_menusu.json'
            ]
            
            for json_file in json_files:
                if os.path.exists(json_file):
                    print(f"📂 Menü dosyası bulundu: {json_file}")
                    with open(json_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            print("❌ Yemek menüsü JSON dosyası bulunamadı!")
            return {}
                
        except Exception as e:
            print(f"❌ Menü yükleme hatası: {e}")
            return {}
    
    def get_today_menu(self) -> Optional[Dict]:
        """Bugünün menüsünü al"""
        menu_data = self.load_menu_data()
        today_key = self.today.strftime('%Y-%m-%d')
        
        print(f"🔍 Aranan tarih: {today_key}")
        print(f"📋 Mevcut menü tarihleri: {len(menu_data)} gün")
        
        if today_key in menu_data:
            menu = menu_data[today_key]
            print(f"✅ {today_key} için menü bulundu!")
            return menu
        
        # Hafta sonu kontrolü
        if self.today.weekday() >= 5:  # Cumartesi=5, Pazar=6
            print("📅 Hafta sonu - normal yemek servisi yok")
            return None
        
        print(f"❌ {today_key} için menü bulunamadı")
        return None
    
    def send_slack_notification(self, menu: Dict) -> bool:
        """Slack'e menü gönder"""
        if not self.slack_webhook:
            print("❌ Slack webhook URL bulunamadı!")
            return False
        
        # Özel durum kontrolü (resmi tatil)
        if menu.get('ozel_durum'):
            return self.send_special_message(menu)
        
        # Normal menü mesajı
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🍽️ {menu['tarih']} - Bugünün Menüsü",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Çorbalar
        if menu.get('corbalar') and any(menu['corbalar']):
            corbalar_text = '\n'.join([f"• {c}" for c in menu['corbalar'] if c])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🥣 *Çorbalar:*\n{corbalar_text}"
                }
            })
        
        # Ana yemekler
        if menu.get('ana_yemekler') and any(menu['ana_yemekler']):
            ana_yemekler_text = '\n'.join([f"• {a}" for a in menu['ana_yemekler'] if a])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🍖 *Ana Yemekler:*\n{ana_yemekler_text}"
                }
            })
        
        # Yan yemekler
        if menu.get('yan_yemekler') and any(menu['yan_yemekler']):
            yan_yemekler_text = '\n'.join([f"• {y}" for y in menu['yan_yemekler'] if y])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🥬 *Yan Yemekler:*\n{yan_yemekler_text}"
                }
            })
        
        # Salatalar
        if menu.get('salatalar') and any(menu['salatalar']):
            salatalar_text = '\n'.join([f"• {s}" for s in menu['salatalar'] if s])
            blocks.append({
                "type": "section", 
                "text": {
                    "type": "mrkdwn",
                    "text": f"🥗 *Salatalar:*\n{salatalar_text}"
                }
            })
        
        # Tatlılar
        if menu.get('tatlilar') and any(menu['tatlilar']):
            tatlilar_text = '\n'.join([f"• {t}" for t in menu['tatlilar'] if t])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn", 
                    "text": f"🍰 *Tatlılar:*\n{tatlilar_text}"
                }
            })
        
        # Kalori bilgisi
        if menu.get('kalori'):
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚡ *Kalori:* {menu['kalori']}"
                }
            })
        
        # Footer
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 Ofis Yemek Bot | Afiyet olsun! 😋"
                    }
                ]
            }
        ])
        
        payload = {
            "channel": self.slack_channel,
            "username": "Yemek Bot 🍽️",
            "icon_emoji": ":fork_and_knife:",
            "blocks": blocks
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Yemek menüsü Slack'e gönderildi!")
                return True
            else:
                print(f"❌ Slack hatası: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Slack gönderim hatası: {e}")
            return False
    
    def send_special_message(self, menu: Dict) -> bool:
        """Özel durum mesajı gönder (resmi tatil vs.)"""
        if menu.get('ozel_durum') == "RESMİ TATİL":
            message = f"🏛️ *{menu['tarih']}*\n\n🎉 Bugün resmi tatil!\nYemek servisi bulunmamaktadır.\n\n🏡 İyi tatiller!"
        else:
            message = f"ℹ️ *{menu['tarih']}*\n\n{menu.get('ozel_durum', 'Özel durum')}"
        
        payload = {
            "channel": self.slack_channel,
            "username": "Yemek Bot 🍽️",
            "icon_emoji": ":calendar:",
            "text": message
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def send_no_menu_message(self) -> bool:
        """Menü yoksa bilgi mesajı gönder"""
        if not self.slack_webhook:
            return False
        
        day_name = self.today.strftime('%A')
        turkish_days = {
            'Monday': 'Pazartesi',
            'Tuesday': 'Salı', 
            'Wednesday': 'Çarşamba',
            'Thursday': 'Perşembe',
            'Friday': 'Cuma',
            'Saturday': 'Cumartesi',
            'Sunday': 'Pazar'
        }
        
        day_tr = turkish_days.get(day_name, day_name)
        
        if self.today.weekday() >= 5:  # Hafta sonu
            message = f"📅 *{self.today.strftime('%d.%m.%Y')} {day_tr}*\n\n🏡 Hafta sonu, yemek servisi bulunmamaktadır.\n\nİyi hafta sonları! 🌸"
        else:
            message = f"❓ *{self.today.strftime('%d.%m.%Y')} {day_tr}*\n\n🤔 Bu tarih için menü bulunamadı.\n\n🍕 Dışarıdan sipariş günü olabilir!"
        
        payload = {
            "channel": self.slack_channel,
            "username": "Yemek Bot 🍽️",
            "icon_emoji": ":question:",
            "text": message
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        try:
            print(f"🔍 {self.today.strftime('%d.%m.%Y %A')} için menü aranıyor...")
            
            menu = self.get_today_menu()
            
            if menu:
                success = self.send_slack_notification(menu)
                if success:
                    print("✅ Yemek bot'u başarıyla çalıştı!")
                    return 0
                else:
                    print("❌ Slack bildirimi gönderilemedi")
                    return 1
            else:
                # Menü yoksa bilgi mesajı gönder
                self.send_no_menu_message()
                print("ℹ️ Menü bulunamadı, bilgi mesajı gönderildi")
                return 0
                
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            return 1

if __name__ == "__main__":
    bot = OfisYemekBot()
    exit_code = bot.run()
    exit(exit_code)
