# TUA-Astro-HACKATHON-Afet
TUA (Türkiye Uzay Ajansı) Hackathonu kapsamında geliştirdiğin bu proje, sadece bir "yol tarifi" uygulaması değil; uzay teknolojilerini yereldeki hayati verilerle birleştiren bir Afet Yönetim ve Karar Destek Mekanizması.

Projeni teknik detaylarla süsleyerek, jüriye veya bir sunuma hazır hale getirecek şekilde şöyle detaylandırabiliriz:

🛰️ TUA-Astro-HACKATHON: Akıllı Afet Koordinasyon Sistemi
Projemiz, afet anındaki "altın saatlerde" (ilk müdahale süreci) kaosun önüne geçmek ve kurtarma ekiplerine gerçek zamanlı durumsal farkındalık sağlamak amacıyla geliştirilmiş bütünleşik bir platformdur.

1. Uzaydan Gelen Göz: Uydu Verisi ve Entegrasyon
Sistemimiz, sadece statik haritaları kullanmaz. TUA ve ilgili uydu ağlarından gelen verileri işleyerek:

Optik ve Radar Görüntüleme: Bulutlu havalarda bile (SAR uyduları sayesinde) sel veya deprem sonrası yüzey değişikliklerini tespit eder.

Gerçek Zamanlı Altlık: Bursa Nilüfer Çayı gibi kritik bölgelerden alınan koordinat verileriyle, sahadaki fiziksel değişimi (yol çökmesi, su taşkını) anında haritaya yansıtır.

2. Yapay Zeka Destekli Risk Analizi
Geliştirdiğimiz Python tabanlı algoritmalar (Q-Learning ve Reinforcement Learning tecrübelerimizle harmanlanmış) şu işlevleri görür:

Dinamik Rota Optimizasyonu: osmnx ve networkx kütüphanelerini kullanarak, sadece en kısa yolu değil, afetten etkilenmemiş "en güvenli" yolu hesaplar. Bir yol kapalıysa, yapay zeka alternatif rotayı saniyeler içinde çizer.

Bina Kimlik Sistemi (BKS) Entegrasyonu: 2021 yılında devreye giren BKS verilerini sisteme gömerek, ekiplerin müdahale edeceği binanın yaşını, yapı tipini ve risk durumunu tabletlerinde görmesini sağlar.

3. Erken Uyarı ve Müdahale Hızı
Sistemimiz sadece olay anını değil, olay öncesini de yönetir:

Sensör Entegrasyonu: Dere yataklarındaki su seviyesi sensörleri veya sismik veriler, erken uyarı modülümüzü tetikler.

Otomatik Bilgilendirme: Ekipler daha afet gerçekleşmeden, riskli bölgeden uzaklaşmaları veya o bölgeye intikal etmeleri için otomatik olarak uyarılır.

4. Teknik Altyapı ve Kararlılık
Arayüz: PyQt5 ile geliştirilen profesyonel komuta merkezi arayüzü sayesinde, tüm karmaşık veriler sade ve anlaşılır bir panelde toplanır.

Görselleştirme: Folium ve Google Satellite katmanları ile sahadaki ekiplere "gerçek arazi görünümü" sunulur, böylece bina girişleri ve çevre engelleri net bir şekilde seçilebilir.

💡 Özetle Farkımız Nedir?
Geleneksel sistemler sadece yolu gösterir. Bizim sistemimiz ise yolu analiz eder. Bir sokağın su altında kaldığını veya bir binanın çökme riskinin yüksek olduğunu yapay zeka ile öngörüp, kurtarma ekibini o sokağa sokmadan en güvenli arka yoldan hedefe ulaştırır.

Sonuç: Daha hızlı müdahale, daha güvenli operasyon ve kurtarılan daha fazla hayat.
![komuta](https://github.com/user-attachments/assets/07bfa0c1-c45a-420c-af49-54a066ccaf7e)
![proje bilgi](https://github.com/user-attachments/assets/d5b03dbe-4184-47c2-b8c5-738a62687279)
![bks](https://github.com/user-attachments/assets/e52a1a22-88dc-43e7-8253-0490a10ca7e8)
![analiz](https://github.com/user-attachments/assets/ed97d5d8-a853-42cd-959f-11c1466163a2)
![kod1](https://github.com/user-attachments/assets/b38bf0aa-53c7-42b9-a68e-f51535c4eac2)
![kod2](https://github.com/user-attachments/assets/bd6e0c74-f17c-41a1-be96-7aba7bc9b5be)



