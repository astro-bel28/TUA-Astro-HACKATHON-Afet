import sys
import os
import random
import folium
import networkx as nx
import osmnx as ox
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFrame, QScrollArea, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QStackedWidget, 
                             QRadioButton, QGridLayout, QCheckBox, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont, QPixmap

def resource_path(relative_path):
    """ PyInstaller paketlemesi için dosya yollarını ayarlar. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AfetSistemi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bursa Afet Komuta & Tam Entegre Analiz Sistemi")
        self.setGeometry(10, 10, 1580, 980)
        self.setStyleSheet("background-color: #D3D3D3;") 

        # Dosya Yolları (Resimleri resource_path ile çağırıyoruz)
        self.PATH_HEADER = resource_path("header.jpeg").replace('\\', '/')
        self.PATH_RIGHT = resource_path("rightlayout.jpeg").replace('\\', '/')
        self.DEPREM_MAP_PATH = resource_path("image_d4df62.png")
        self.SEL_MAP_PATH = resource_path("image_d4dc7b.png")

        # Sabit Koordinatlar ve Renkler
        self.AFAD_RENK, self.ITFAIYE_RENK, self.AMBULANS_RENK = '#FF8C00', '#00E5FF', '#39FF14'
        self.AFAD_MERKEZ = (40.2100, 29.0088)
        self.ITFAIYE_IHSANIYE = (40.2236, 28.9918)
        self.HASTANE = (40.2018, 29.0145)
        
        self.active_afet_merkez = None 
        self.road_graph = None

        self.init_ui()
        self.show_plain_map_page()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # --- ÜST HEADER ---
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(f"QFrame {{ background-image: url('{self.PATH_HEADER}'); background-size: cover; border-bottom: 4px solid #000; }}")
        h_layout = QHBoxLayout(header)
        
        title = QLabel("🛡️ Afet Uydu İzleme Sistemi")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100); padding: 5px;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        btn_style = "QPushButton { background-color: rgba(224, 224, 224, 180); border-left: 2px solid #000; font-size: 16px; font-weight: bold; padding: 0 40px; height: 90px; } QPushButton:hover { background-color: white; }"
        self.btn_harita = QPushButton("HARİTA")
        self.btn_analiz = QPushButton("AFET ANALİZİ")
        self.btn_harita.setStyleSheet(btn_style)
        self.btn_analiz.setStyleSheet(btn_style)
        
        self.btn_harita.clicked.connect(self.go_to_map)
        self.btn_analiz.clicked.connect(self.go_to_analysis)
        
        h_layout.addWidget(self.btn_harita)
        h_layout.addWidget(self.btn_analiz)
        main_layout.addWidget(header)

        # --- ORTA ALAN (İÇERİK) ---
        content_area = QHBoxLayout()
        self.content_stack = QStackedWidget()
        
        self.map_view = QWebEngineView()
        self.content_stack.addWidget(self.map_view)               # Index 0
        self.content_stack.addWidget(self.create_analysis_page())   # Index 1
        self.content_stack.addWidget(self.create_project_info_page())# Index 2
        self.content_stack.addWidget(self.create_erken_uyari_page()) # Index 3
        
        content_area.addWidget(self.content_stack, stretch=8)

        # --- SAĞ KOMUTA PANELİ ---
        self.side_panel = QFrame()
        self.side_panel.setFixedWidth(290)
        self.side_panel.setStyleSheet(f"QFrame {{ background-image: url('{self.PATH_RIGHT}'); background-size: cover; border-left: 2px solid #000; }}")
        self.side_layout = QVBoxLayout(self.side_panel)
        
        self.btn_komuta_start = QPushButton("🚀 KOMUTA MERKEZİ\n(HESAPLA)")
        self.btn_komuta_start.setStyleSheet("background-color: #1B5E20; color: white; font-weight: bold; height: 80px; border-radius: 10px; font-size: 14px;")
        self.btn_komuta_start.clicked.connect(self.activate_command_center)
        self.side_layout.addWidget(self.btn_komuta_start)

        self.control_group = QFrame()
        self.control_group.setVisible(False)
        ctrl_vbox = QVBoxLayout(self.control_group)
        box_style = "background-color: rgba(255, 255, 255, 210); border: 2px solid #333; border-radius: 8px; padding: 10px; margin-top:5px;"
        
        # Senaryo Seçimi
        afet_box = QFrame(); afet_box.setStyleSheet(box_style); af_vbox = QVBoxLayout(afet_box)
        af_vbox.addWidget(QLabel("<b>⚡ SENARYO SEÇİMİ</b>"))
        self.radio_deprem = QRadioButton("Deprem Senaryosu")
        self.radio_sel = QRadioButton("Sel Senaryosu")
        self.radio_deprem.setChecked(True)
        self.radio_deprem.toggled.connect(self.update_map_render)
        self.radio_sel.toggled.connect(self.update_map_render)
        af_vbox.addWidget(self.radio_deprem); af_vbox.addWidget(self.radio_sel)
        ctrl_vbox.addWidget(afet_box)
        
        # Rota Kontrolleri
        route_box = QFrame(); route_box.setStyleSheet(box_style); r_vbox = QVBoxLayout(route_box)
        r_vbox.addWidget(QLabel("<b>🛣️ ROTA KONTROLLERİ</b>"))
        self.chk_itf = QCheckBox("🚒 İtfaiye Ringi")
        self.chk_amb = QCheckBox("🚑 Ambulans Hattı")
        self.chk_afd = QCheckBox("🟠 AFAD Lojistik")
        self.chk_bks = QCheckBox("🏢 BKS Riskli Binalar")
        for chk in [self.chk_itf, self.chk_amb, self.chk_afd, self.chk_bks]: 
            chk.setChecked(True)
            chk.stateChanged.connect(self.update_map_render)
            r_vbox.addWidget(chk)
        ctrl_vbox.addWidget(route_box)
        self.side_layout.addWidget(self.control_group)

        # Alt Butonlar
        self.btn_info_page = QPushButton("SİSTEM BİLGİLERİ")
        self.btn_info_page.setStyleSheet("background-color: #37474F; color: white; height: 50px; font-weight: bold; border-radius:10px; margin-top:10px;")
        self.btn_info_page.clicked.connect(self.go_to_info)
        self.side_layout.addWidget(self.btn_info_page)
        
        self.btn_erken_uyari_nav = QPushButton("🚨 ERKEN UYARI")
        self.btn_erken_uyari_nav.setStyleSheet("background-color: #C62828; color: white; height: 50px; font-weight: bold; border-radius:10px; margin-top:10px;")
        self.btn_erken_uyari_nav.clicked.connect(self.go_to_erken_uyari)
        self.side_layout.addWidget(self.btn_erken_uyari_nav)
        
        self.side_layout.addStretch()
        content_area.addWidget(self.side_panel)
        main_layout.addLayout(content_area)

    def activate_command_center(self):
        """ Komuta merkezini tetikler ve rotaları hesaplar. """
        QMessageBox.warning(self, "ACİL DURUM SİNYALİ", "🚨 Analiz başlatılıyor ve ekipler yönlendiriliyor...")
        self.active_afet_merkez = (40.21, 29.02) # Örnek afet koordinatı
        self.content_stack.setCurrentIndex(0)
        self.control_group.setVisible(True)
        self.update_map_render()

    def create_analysis_page(self):
        """ Görseldeki 'Afet Analizi' sayfasını oluşturur. """
        scroll = QScrollArea(); container = QWidget(); layout = QVBoxLayout(container)
        container.setStyleSheet("background-color: #D3D3D3;")
        
        main_header = QLabel("Afet Analizi")
        main_header.setFont(QFont("Arial", 22, QFont.Bold))
        layout.addWidget(main_header)
        
        risk_l = QLabel("Risk Seviyesi Göstergeleri")
        risk_l.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(risk_l)
        
        # Sel Bölümü
        s_cont = QHBoxLayout(); s_img = QLabel(); s_img.setFixedSize(300, 200); s_img.setScaledContents(True)
        if os.path.exists(self.SEL_MAP_PATH): s_img.setPixmap(QPixmap(self.SEL_MAP_PATH))
        s_v = QVBoxLayout(); s_t = QLabel("Sel Risk Seviyesi Göstergeleri")
        s_t.setStyleSheet("background: #778899; color: white; padding: 10px; font-weight: bold;")
        s_v.addWidget(s_t)
        tw_s = QTableWidget(5, 2); tw_s.setFixedHeight(220); tw_s.setHorizontalHeaderLabels(["Risk", "Açıklama"])
        tw_s.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        s_d = [("⚪ Düşük Risk", "Normal yağış rejimi; drenaj yeterli."), ("🔵 Orta Risk", "Yoğun yağış; alt geçitlerde su birikintisi."), ("⚫ Yüksek Risk", "Ekstrem hava; geniş çaplı baskın.")]
        for i, (r, a) in enumerate(s_d): tw_s.setItem(i, 0, QTableWidgetItem(r)); tw_s.setItem(i, 1, QTableWidgetItem(a))
        s_v.addWidget(tw_s); s_cont.addWidget(s_img); s_cont.addLayout(s_v); layout.addLayout(s_cont)

        # Deprem Bölümü
        d_cont = QHBoxLayout(); d_v = QVBoxLayout(); d_t = QLabel("Deprem Risk Seviyesi Göstergeleri")
        d_t.setStyleSheet("background: #778899; color: white; padding: 10px; font-weight: bold;")
        d_v.addWidget(d_t)
        tw_d = QTableWidget(5, 2); tw_d.setFixedHeight(220); tw_d.setHorizontalHeaderLabels(["Risk", "Açıklama"])
        tw_d.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        d_d = [("⚪ Düşük Risk", "Sismik aktivite normal."), ("🔴 Orta Risk", "Aktif sismik enerji birikimi."), ("⚫ Yüksek Risk", "Maksimum sismik tehlike; acil durum.")]
        for i, (r, a) in enumerate(d_d): tw_d.setItem(i, 0, QTableWidgetItem(r)); tw_d.setItem(i, 1, QTableWidgetItem(a))
        d_v.addWidget(tw_d); d_img = QLabel(); d_img.setFixedSize(300, 200); d_img.setScaledContents(True)
        if os.path.exists(self.DEPREM_MAP_PATH): d_img.setPixmap(QPixmap(self.DEPREM_MAP_PATH))
        d_cont.addLayout(d_v); d_cont.addWidget(d_img); layout.addLayout(d_cont)
        
        scroll.setWidget(container); scroll.setWidgetResizable(True); return scroll

    def create_erken_uyari_page(self):
        """ Görseldeki 'Erken Uyarı Paneli'ni oluşturur. """
        page = QWidget(); layout = QHBoxLayout(page); layout.setContentsMargins(40,40,40,40)
        left = QFrame(); left.setStyleSheet("background-color: #E57373; border: 3px solid black;"); l_lay = QVBoxLayout(left)
        l_lay.addWidget(QLabel("Erken Uyarı Paneli", font=QFont("Arial", 22, QFont.Bold)))
        l_lay.addWidget(QLabel("Sistem Durumu: Aktif 🟢 / Pasif 🔴", font=QFont("Arial", 12)))
        l_lay.addWidget(QLabel("Afet durumlarında yapay zeka destekli tespit sistemimiz ile gerçek zamanlı uyarı al!", font=QFont("Arial", 16, QFont.Bold), wordWrap=True))
        l_lay.addStretch(); btn = QPushButton("Erken Uyarı Al"); btn.setFixedSize(220, 70); l_lay.addWidget(btn, alignment=Qt.AlignCenter); l_lay.addSpacing(20)
        right = QFrame(); right.setStyleSheet("background-color: #BDBDBD; border: 3px solid black;"); r_lay = QVBoxLayout(right)
        r_lay.addWidget(QLabel("Yapay Zeka Destekli Gerçek Zamanlı Uyarı Sistemi", font=QFont("Arial", 18, QFont.Bold), wordWrap=True))
        r_lay.addWidget(QLabel("Anlık sarsıntı tespiti ve uydu verileri yapay zeka ile işlenerek anlık uyarı verilmektedir.", wordWrap=True))
        layout.addWidget(left, 1); layout.addWidget(right, 1); return page

    def create_project_info_page(self):
        """ Görseldeki 'Sistem Bilgileri' grid yapısını oluşturur. """
        scroll = QScrollArea(); container = QWidget(); grid = QGridLayout(container)
        items = [("📍 HARİTA PANELİ", "Uydu verilerinden elde edilen analiz sonuçları harita üzerinde gösterilir.", "🗺️"), 
                 ("⚠️ RİSK ANALİZİ PANELİ", "Bölgeler değişimlere göre risk seviyelerine ayrılmıştır.", "⚠️"), 
                 ("🌊 SEL ANALİZİ PANELİ", "Taşkın alanları ve su birikimi otomatik tespit edilir.", "🌊"), 
                 ("🏠 DEPREM ANALİZİ PANELİ", "Yüzey değişimleri karşılaştırılarak hasar tespiti yapılır.", "🏠"),
                 ("⚙️ SİSTEM NASIL ÇALIŞIR", "Veriler işlenir ve en güvenli güzergah sunulur.", "⚙️"), 
                 ("🧭 YÖNLENDİRME PANELİ", "Afet durumunda en hızlı ve güvenli rota hesaplanır.", "🧭"),
                 ("🧠 YAPAY ZEKA PANELİ", "Makine öğrenmesi ile risk seviyeleri otomatik belirlenir.", "🧠"), 
                 ("📡 VERİ PANELİ", "Radar tabanlı uydu verileriyle 7/24 kesintisiz analiz.", "📡")]
        for i, (t, d, ic) in enumerate(items):
            f = QFrame(); f.setStyleSheet("background: white; border: 1px solid black; padding: 15px;"); fl = QVBoxLayout(f)
            h = QHBoxLayout(); h.addWidget(QLabel(ic)); h.addWidget(QLabel(t, font=QFont("Arial", 12, QFont.Bold))); h.addStretch()
            fl.addLayout(h); fl.addWidget(QLabel(d, wordWrap=True)); grid.addWidget(f, i // 2, i % 2)
        scroll.setWidget(container); scroll.setWidgetResizable(True); return scroll

    def update_map_render(self):
        """ Haritayı, çemberleri ve rotaları günceller. """
        if not self.active_afet_merkez: return
        
        # Harita Alt Yapısı (Esri Satellite)
        m = folium.Map(location=self.active_afet_merkez, zoom_start=14, 
                       tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")
        
        # Sabit Nokta İkonları
        folium.Marker(self.AFAD_MERKEZ, icon=folium.Icon(color='orange', icon='university', prefix='fa')).add_to(m)
        folium.Marker(self.ITFAIYE_IHSANIYE, icon=folium.Icon(color='blue', icon='fire', prefix='fa')).add_to(m)
        folium.Marker(self.HASTANE, icon=folium.Icon(color='green', icon='plus', prefix='fa')).add_to(m)
        
        # Deprem Çemberi ve Afet Rengi
        if self.radio_deprem.isChecked():
            afet_renk = 'red'
            folium.Circle(location=self.active_afet_merkez, radius=500, color='red', fill=True, fill_color='red', fill_opacity=0.3).add_to(m)
        else:
            afet_renk = 'darkblue'

        folium.Marker(self.active_afet_merkez, icon=folium.Icon(color=afet_renk, icon='bolt', prefix='fa')).add_to(m)

        # Rota Çizimi (Güçlendirilmiş try-except)
        try:
            if self.road_graph is None: 
                self.road_graph = ox.graph_from_point((40.21, 29.01), dist=3000, network_type='drive')
            
            G = self.road_graph
            target_node = ox.distance.nearest_nodes(G, self.active_afet_merkez[1], self.active_afet_merkez[0])
            
            def draw_route(start_coord, route_color):
                try:
                    start_node = ox.distance.nearest_nodes(G, start_coord[1], start_coord[0])
                    path = nx.shortest_path(G, start_node, target_node, weight='length')
                    path_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in path]
                    folium.PolyLine(path_coords, color=route_color, weight=7, opacity=0.8).add_to(m)
                except Exception as e: print(f"Rota hatası: {e}")

            if self.chk_itf.isChecked(): draw_route(self.ITFAIYE_IHSANIYE, self.ITFAIYE_RENK)
            if self.chk_amb.isChecked(): draw_route(self.HASTANE, self.AMBULANS_RENK)
            if self.chk_afd.isChecked(): draw_route(self.AFAD_MERKEZ, self.AFAD_RENK)
        except Exception as e:
            print(f"OSMNx Veri Yükleme Hatası: {e}")

        # BKS Riskli Binalar
        if self.chk_bks.isChecked():
            for _ in range(43):
                loc = [self.active_afet_merkez[0]+random.uniform(-0.005,0.005), self.active_afet_merkez[1]+random.uniform(-0.005,0.005)]
                folium.Marker(loc, icon=folium.Icon(color='darkred', icon='home')).add_to(m)

        m.save("map.html")
        self.map_view.setUrl(QUrl.fromLocalFile(os.path.abspath("map.html")))

    def show_plain_map_page(self): 
        """ İlk açılışta temiz harita gösterir. """
        m = folium.Map(location=[40.21, 29.00], zoom_start=13, 
                       tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri")
        m.save("map.html")
        self.map_view.setUrl(QUrl.fromLocalFile(os.path.abspath("map.html")))

    # Navigasyon Fonksiyonları
    def go_to_map(self): self.content_stack.setCurrentIndex(0)
    def go_to_analysis(self): self.content_stack.setCurrentIndex(1); self.control_group.setVisible(False)
    def go_to_info(self): self.content_stack.setCurrentIndex(2); self.control_group.setVisible(False)
    def go_to_erken_uyari(self): self.content_stack.setCurrentIndex(3); self.control_group.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AfetSistemi()
    win.show()
    sys.exit(app.exec_())