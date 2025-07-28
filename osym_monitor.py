import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import hashlib

class GitHubActionsOSYMMonitor:
    def __init__(self):
        # Environment variables
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.slack_channel = os.getenv('SLACK_CHANNEL', '#yks-takip')
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
        
        # Cache directory
        self.cache_dir = 'cache'
        self.cache_file = os.path.join(self.cache_dir, 'osym_data.json')
        
        # URLs to monitor
        self.urls = [
            "https://www.osym.gov.tr/TR,33351/2025.html",  # Duyurular
            "https://www.osym.gov.tr/TR,33007/2025.html"   # Belgeler
        ]
        
        # Create cache directory
        os.makedirs(self.cache_dir, exist_ok=True)
        
        print(f"🤖 ÖSYM Monitor başlatıldı (Test modu: {self.test_mode})")
        print(f"📁 Cache dizini: {self.cache_dir}")
        print(f"📋 Takip edilen URL sayısı: {len(self.urls)}")
    
    def get_table_row_count(self, url):
        """URL'deki tablo satır sayısını döndür"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            print(f"🔍 Kontrol ediliyor: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # tbody içindeki tr elementlerini say
            tbody = soup.find('tbody')
            if tbody:
                rows = tbody.find_all('tr', class_='row')
                count = len(rows)
                print(f"   ✅ {count} satır bulundu (tbody)")
                return count
            
            # tbody yoksa table içindeki tr'ları say
            table = soup.find('table', id='list')
            if table:
                rows = table.find_all('tr', class_='row')
                count = len(rows)
                print(f"   ✅ {count} satır bulundu (table)")
                return count
            
            print(f"   ⚠️ Tablo bulunamadı")
            return 0
            
        except requests.RequestException as e:
            print(f"   ❌ İstek hatası: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Parse hatası: {e}")
            return None
    
    def load_cache(self):
        """Cache dosyasını yükle"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"📂 Cache yüklendi: {len(data)} kayıt")
                    return data
            print("📂 Cache dosyası bulunamadı, yeni oluşturulacak")
            return {}
        except Exception as e:
            print(f"⚠️ Cache yükleme hatası: {e}")
            return {}
    
    def save_cache(self, data):
        """Cache dosyasını kaydet"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 Cache kaydedildi: {len(data)} kayıt")
        except Exception as e:
            print(f"❌ Cache kaydetme hatası: {e}")
    
    def send_slack_notification(self, url, old_count, new_count):
        """Slack'e bildirim gönder"""
        if not self.slack_webhook:
            print("⚠️ Slack webhook URL bulunamadı!")
            return False
        
        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        
        # Sayfa isimlerini belirle
        page_names = {
            "https://www.osym.gov.tr/TR,33351/2025.html": "YKS Duyurular",
            "https://www.osym.gov.tr/TR,33007/2025.html": "YKS Belgeler"
        }
        
        page_name = page_names.get(url, "ÖSYM Sayfası")
        difference = new_count - old_count
        
        # GitHub Actions URL'i (workflow run)
        github_run_url = f"https://github.com/{os.getenv('GITHUB_REPOSITORY', 'repo')}/actions/runs/{os.getenv('GITHUB_RUN_ID', '0')}"
        
        payload = {
            "channel": self.slack_channel,
            "username": "ÖSYM YKS Bot (GitHub)",
            "icon_emoji": ":rotating_light:",
            "attachments": [
                {
                    "color": "good",
                    "title": f"🚨 {page_name} - Yeni İçerik Tespit Edildi!",
                    "fields": [
                        {
                            "title": "📄 Sayfa",
                            "value": page_name,
                            "short": True
                        },
                        {
                            "title": "🕐 Tarih",
                            "value": current_time,
                            "short": True
                        },
                        {
                            "title": "📊 Önceki Sayı",
                            "value": str(old_count),
                            "short": True
                        },
                        {
                            "title": "📈 Yeni Sayı",
                            "value": str(new_count),
                            "short": True
                        },
                        {
                            "title": "🔥 Yeni Eklenen",
                            "value": f"+{difference} öğe",
                            "short": False
                        }
                    ],
                    "actions": [
                        {
                            "type": "button",
                            "text": "🔗 ÖSYM Sayfasını Aç",
                            "url": url,
                            "style": "primary"
                        },
                        {
                            "type": "button", 
                            "text": "📊 GitHub Actions",
                            "url": github_run_url
                        }
                    ],
                    "footer": "ÖSYM Takip Sistemi (GitHub Actions)",
                    "footer_icon": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                    "ts": int(datetime.now().timestamp())
                }
            ]
        }
        
        try:
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"✅ Slack bildirimi gönderildi: {page_name} ({old_count} → {new_count})")
                return True
            else:
                print(f"❌ Slack hatası: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Slack gönderim hatası: {e}")
            return False
    
    def check_updates(self):
        """Tüm URL'leri kontrol et"""
        cache = self.load_cache()
        updates_found = False
        
        print(f"\n🔍 URL kontrolü başlatıldı ({datetime.now().strftime('%H:%M:%S')})")
        print("=" * 50)
        
        for url in self.urls:
            current_count = self.get_table_row_count(url)
            
            if current_count is None:
                print(f"   ⚠️ Sayfa okunamadı, devam ediliyor...")
                continue
            
            # URL'yi cache key'e çevir
            url_key = hashlib.md5(url.encode()).hexdigest()[:8]
            old_count = cache.get(url_key, {}).get('count', 0)
            
            print(f"   📊 Önceki: {old_count}, Şu anki: {current_count}")
            
            # Değişiklik kontrolü
            if True:
                print(f"   🚨 DEĞİŞİKLİK TESPİT EDİLDİ! (+{current_count - old_count})")
                
                if not self.test_mode:
                    success = self.send_slack_notification(url, old_count, current_count)
                    if success:
                        updates_found = True
                else:
                    print("   🧪 Test modu - bildirim gönderilmedi")
                    updates_found = True
            elif old_count == current_count:
                print(f"   ✅ Değişiklik yok")
            elif old_count > current_count:
                print(f"   📉 Sayı azalmış ({old_count} → {current_count})")
            else:
                print(f"   🆕 İlk kayıt")
            
            # Cache'i güncelle
            cache[url_key] = {
                'url': url,
                'count': current_count,
                'last_check': datetime.now().isoformat(),
                'page_name': "YKS Duyurular" if "33351" in url else "YKS Belgeler"
            }
        
        # Cache'i kaydet
        self.save_cache(cache)
        
        print("=" * 50)
        if updates_found:
            print("🎉 Değişiklik tespit edildi ve bildirim gönderildi!")
        else:
            print("ℹ️ Herhangi bir değişiklik bulunamadı")
        
        return updates_found
    
    def run(self):
        """Ana çalıştırma fonksiyonu"""
        try:
            # GitHub Actions ortam bilgilerini yazdır
            if os.getenv('GITHUB_ACTIONS'):
                print(f"🏃 GitHub Actions Runner: {os.getenv('RUNNER_OS')}")
                print(f"📦 Repository: {os.getenv('GITHUB_REPOSITORY')}")
                print(f"🔄 Run ID: {os.getenv('GITHUB_RUN_ID')}")
            
            # Kontrolü yap
            result = self.check_updates()
            
            # Sonuç
            if result:
                print("\n✅ Monitoring tamamlandı - Değişiklik tespit edildi")
                return 0
            else:
                print("\n✅ Monitoring tamamlandı - Değişiklik yok")
                return 0
                
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")
            return 1

if __name__ == "__main__":
    monitor = GitHubActionsOSYMMonitor()
    exit_code = monitor.run()
    exit(exit_code)
