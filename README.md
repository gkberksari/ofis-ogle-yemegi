# 🍽️ Ofis Yemek Menüsü Bot

GitHub Actions ile çalışan otomatik yemek menüsü bildirimi botu.

## 🎯 Özellikler

- **Otomatik**: Her gün saat 11:00'da çalışır
- **Akıllı**: Hafta sonu ve resmi tatil mesajları
- **Zengin içerik**: Çorba, ana yemek, yan yemek, salata, tatlı detayları
- **Kalori bilgisi**: Her menü için kalori hesabı
- **Ücretsiz**: GitHub Actions ile tamamen bedava

## ⏰ Çalışma Programı

- **Hafta içi 11:00**: Günlük menü bildirimi
- **Hafta sonu**: "İyi hafta sonları" mesajı
- **Resmi tatil**: "Resmi tatil" bildirimi

## 🔧 Kurulum

1. Bu repository'yi fork edin
2. Slack webhook URL'nizi `SLACK_WEBHOOK_URL` secret'ı olarak ekleyin
3. `#yemek` kanalı oluşturun
4. Actions otomatik çalışacak!

## 🧪 Test

**Actions** → **Ofis Yemek Menüsü Bot** → **Run workflow**
- Test tarihi: `2025-08-01`
- **Run workflow**

## 📊 Örnek Mesaj

```
🍽️ 01.08.2025 Cuma - Bugünün Menüsü

🍖 Ana Yemekler:
• Terbiyeli Köfte

🥬 Yan Yemekler:
• Su Böreği

🥗 Salatalar:
• Çoban Salata

🍰 Tatlılar:
• Karpuz

⚡ Kalori: 1390 kcal

🤖 Ofis Yemek Bot | Afiyet olsun! 😋
```

## 🔄 Güncelleme

Yeni ay menüsü geldiğinde `yemek_menusu.json` dosyasını güncelleyin.

## 📞 Destek

GitHub Issues ile sorularınızı sorabilirsiniz.
