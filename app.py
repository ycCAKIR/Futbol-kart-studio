import os
import io
import base64
from flask import Flask, request, jsonify, send_file, render_template_string
from PIL import Image, ImageDraw, ImageFont
from rembg import remove

app = Flask(__name__, static_folder="static", static_url_path="/static")

CONFIG_DB = {
    "bigtime": {"path": "static/kartlar/big time.jpg", "img_box": (140, 25, 305, 260), "rating_pos": (32, 65), "pos_pos": (34, 110), "flag_pos": (37, 140), "logo_pos": (32, 168), "name_y": 275, "stats_start": (42, 350), "text_color": "white"},
    "cark": {"path": "static/kartlar/çark.jpg", "img_box": (145, 28, 305, 258), "rating_pos": (35, 60), "pos_pos": (37, 105), "flag_pos": (40, 135), "logo_pos": (35, 162), "name_y": 280, "stats_start": (40, 355), "text_color": "white"},
    "epic": {"path": "static/kartlar/epic.jpg", "img_box": (140, 25, 305, 260), "rating_pos": (32, 65), "pos_pos": (34, 110), "flag_pos": (37, 140), "logo_pos": (32, 168), "name_y": 278, "stats_start": (42, 352), "text_color": "black"},
    "showtime": {"path": "static/kartlar/show time.jpg", "img_box": (140, 26, 305, 261), "rating_pos": (34, 62), "pos_pos": (36, 108), "flag_pos": (39, 138), "logo_pos": (34, 164), "name_y": 282, "stats_start": (40, 354), "text_color": "white"},
    "fc25icon": {"path": "static/kartlar/fc25-icon.png", "img_box": (120, 68, 288, 270), "rating_pos": (42, 75), "pos_pos": (45, 118), "flag_pos": (48, 145), "logo_pos": (43, 172), "name_y": 282, "stats_start": (52, 345), "text_color": "black"},
    "fifagold": {"path": "static/kartlar/fifa gold.png", "img_box": (123, 68, 285, 270), "rating_pos": (45, 75), "pos_pos": (48, 118), "flag_pos": (51, 145), "logo_pos": (46, 172), "name_y": 282, "stats_start": (54, 345), "text_color": "white"}
}

html_content = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ultimate Kart Tasarım Stüdyosu v15.0 Pro</title>
    <style>
        :root { --bg-color: #0b0c10; --panel-color: #1f2833; --accent-color: #45f3ff; --text-color: #ffffff; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-color); display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 30px 20px; }
        h1 { margin-bottom: 5px; font-size: 28px; text-transform: uppercase; background: linear-gradient(45deg, #45f3ff, #a045ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #66757f; font-size: 14px; margin-bottom: 25px; font-weight: 600; }
        .tab-container { display: flex; gap: 15px; margin-bottom: 25px; width: 100%; max-width: 1000px; }
        .tab-btn { flex: 1; padding: 16px; font-size: 16px; font-weight: 800; text-transform: uppercase; border: 2px solid #1f2833; background-color: #151a21; color: #66757f; cursor: pointer; border-radius: 10px; transition: all 0.2s ease-in-out; }
        .tab-btn.active { border-color: var(--accent-color); color: var(--text-color); background-color: var(--panel-color); box-shadow: 0 0 20px rgba(69, 243, 255, 0.2); }
        .studio-container { display: flex; gap: 40px; width: 100%; max-width: 1000px; justify-content: center; align-items: flex-start; }
        .control-panel { background-color: var(--panel-color); padding: 30px; border-radius: 16px; width: 480px; display: flex; flex-direction: column; gap: 18px; box-shadow: 0 20px 40px rgba(0,0,0,0.6); border: 1px solid rgba(255,255,255,0.05); overflow-y: auto; max-height: 85vh; }
        
        .label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
        .form-group label { font-size: 13px; color: #95a5a6; font-weight: 700; text-transform: uppercase; }
        
        .info-btn { background-color: #2c3e50; color: #45f3ff; border: 1px solid rgba(69, 243, 255, 0.3); border-radius: 50%; width: 22px; height: 22px; font-size: 12px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        .info-btn:hover { background-color: #45f3ff; color: #000; box-shadow: 0 0 8px #45f3ff; }
        
        .help-box { display: none; background-color: #0f141c; border-left: 3px solid var(--accent-color); padding: 10px 12px; margin-top: 6px; border-radius: 4px; font-size: 11px; color: #b3c1cd; line-height: 1.5; }
        .help-box a { color: var(--accent-color); text-decoration: none; font-weight: bold; }
        .help-box a:hover { text-decoration: underline; }
        .help-box ul { list-style-type: none; margin-top: 4px; }
        .help-box ul li { margin-bottom: 2px; position: relative; padding-left: 10px; }
        .help-box ul li::before { content: "•"; color: var(--accent-color); position: absolute; left: 0; }
        
        .form-group input, .form-group select { padding: 12px; background-color: #0f141c; border: 1px solid #2c3e50; border-radius: 8px; color: white; font-size: 14px; outline: none; width: 100%; }
        
        .checkbox-row { display: flex; align-items: center; gap: 8px; margin-top: 6px; font-size: 13px; color: #00ff88; font-weight: bold; }
        .checkbox-row input[type="checkbox"] { width: auto; cursor: pointer; scale: 1.2; accent-color: #00ff88; }

        .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .download-btn { background: linear-gradient(135deg, #00ff88, #00b0ff); color: #000; padding: 15px; border: none; border-radius: 8px; font-size: 16px; font-weight: 800; text-transform: uppercase; cursor: pointer; margin-top: 10px; }
        .preview-area { position: sticky; top: 30px; display: flex; flex-direction: column; align-items: center; gap: 20px; width: 360px; }
        
        .card { position: relative; width: 320px; height: 450px; border-radius: 14px; background-size: 100% 100%; background-position: center; background-repeat: no-repeat; box-shadow: 0 20px 50px rgba(0,0,0,0.8); user-select: none; overflow: hidden; transition: background-image 0.2s ease-in-out; }
        .player-img-container { position: absolute; z-index: 2; overflow: hidden; pointer-events: none; }
        .player-img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .player-rating { position: absolute; font-size: 42px; font-weight: 900; color: #fff; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); z-index: 3; line-height: 1; }
        .player-position { position: absolute; font-size: 16px; font-weight: 800; color: #fff; z-index: 3; text-transform: uppercase; }
        .player-nation, .player-team-logo { position: absolute; z-index: 3; object-fit: contain; }
        .player-nation { width: 30px; height: 20px; }
        .player-team-logo { width: 42px; height: 42px; border-radius: 50%; }
        
        .player-name { position: absolute; width: 100%; text-align: center; font-weight: 900; text-transform: uppercase; z-index: 3; letter-spacing: 1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); }
        
        .card-stats { position: absolute; width: 240px; display: grid; grid-template-columns: repeat(2, 1fr); row-gap: 5px; column-gap: 25px; z-index: 3; }
        .stat-item { display: flex; justify-content: space-between; font-size: 16px; font-weight: 800; }
        
        .ai-status { font-size: 11px; color: #00ff88; margin-top: 4px; font-weight: bold; display: none; }
    </style>
</head>
<body>
    <h1>Ultimate Kart Tasarım Stüdyosu v15.0 Pro</h1>
    <div class="subtitle">Gelişmiş Kırpma Seçenekleri Devrede</div>
    
    <div class="tab-container">
        <button class="tab-btn active" id="btn-efootball" onclick="switchGame('efootball')">eFootball Studio</button>
        <button class="tab-btn" id="btn-fifa" onclick="switchGame('fifa')">FIFA Studio</button>
    </div>

    <div class="studio-container">
        <div class="control-panel">
            <div class="form-group"><label>Kart Tasarımı</label><select id="cardTemplate" onchange="updateCardTemplate()"></select></div>
            <div class="form-group"><label>Oyuncu Adı</label><input type="text" id="nameInput" value="GOAT" oninput="updateCardText()"></div>
            <div class="form-group"><label>Genel Derece (OVR)</label><input type="number" id="ratingInput" value="97" oninput="updateCardText()"></div>
            <div class="form-group"><label>Pozisyon</label><input type="text" id="posInput" value="ST" oninput="updateCardText()"></div>
            <div class="form-group"><label>Ülke Bayrağı</label><select id="nationSelect" onchange="updateNation()"></select></div>
            
            <div class="form-group">
                <div class="label-row">
                    <label>Takım Logosu Yükle</label>
                    <button class="info-btn" onclick="toggleHelp('logoHelp')">i</button>
                </div>
                <input type="file" id="logoLoader" accept="image/*" onchange="handleTeamLogo(event)">
                <div id="logoHelp" class="help-box">
                    <strong>⚽ Takım Logosu Ekleme Rehberi:</strong>
                    <ul>
                        <li><a href="https://football-logos.cc/collections/" target="_blank">football-logos.cc</a> sitesine gidin.</li>
                        <li>Sitede istediğiniz takımın logosunu aratın.</li>
                        <li>Logonun indirme seçeneklerinden <strong>64x64 PNG</strong> formatını seçip indirin.</li>
                        <li>Yukarıdaki butona basarak dosyalarınızdan logoyu seçip ekleyin.</li>
                    </ul>
                </div>
            </div>
            
            <div class="form-group">
                <div class="label-row">
                    <label>Oyuncu Fotoğrafı Yükle</label>
                    <button class="info-btn" onclick="toggleHelp('playerHelp')">i</button>
                </div>
                <input type="file" id="imageLoader" accept="image/*" onchange="handlePlayerImage(event)">
                
                <div class="checkbox-row">
                    <input type="checkbox" id="aiCropToggle" checked>
                    <label for="aiCropToggle">Yapay Zeka ile Arka Planı Otomatik Sil (Kırp)</label>
                </div>
                
                <div id="aiStatus" class="ai-status">⚡ Yapay Zeka arka planı temizliyor, lütfen bekleyin...</div>
                <div id="playerHelp" class="help-box">
                    <strong>👤 Oyuncu Fotoğrafı Ekleme Rehberi:</strong>
                    <ul>
                        <li><strong>Kırpma Aktifken:</strong> Herhangi bir fotoğraf yükleyin, arka plan otomatik temizlenir.</li>
                        <li><strong>Kırpma Kapalıyken:</strong> Fotoğrafınız arka planı silinmeden, orijinal haliyle karta yerleştirilir.</li>
                    </ul>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="form-group"><label>HIZ</label><input type="number" id="s1" value="98" oninput="updateCardText()"></div>
                <div class="form-group"><label>ŞUT</label><input type="number" id="s2" value="95" oninput="updateCardText()"></div>
                <div class="form-group"><label>PAS</label><input type="number" id="s3" value="91" oninput="updateCardText()"></div>
                <div class="form-group"><label>DRİ</label><input type="number" id="s4" value="96" oninput="updateCardText()"></div>
                <div class="form-group"><label>DEF</label><input type="number" id="s5" value="42" oninput="updateCardText()"></div>
                <div class="form-group"><label>FİZ</label><input type="number" id="s6" value="84" oninput="updateCardText()"></div>
            </div>
            <button class="download-btn" onclick="downloadCardServer()">Kartı HD İndir 🚀</button>
        </div>

        <div class="preview-area">
            <div class="card efootball-mode" id="playerCard">
                <div class="player-rating" id="cardRating">97</div>
                <div class="player-position" id="cardPosition">ST</div>
                <img id="cardNation" class="player-nation" src="">
                <img id="cardTeamLogo" class="player-team-logo" src="">
                <div id="cardImageContainer" class="player-img-container"><img id="cardImage" class="player-img" src=""></div>
                <div class="player-name" id="cardName">GOAT</div>
                <div class="card-stats" id="cardStats">
                    <div class="stat-item"><span class="stat-label">HIZ</span><span class="stat-value" id="val1">98</span></div>
                    <div class="stat-item"><span class="stat-label">ŞUT</span><span class="stat-value" id="val2">95</span></div>
                    <div class="stat-item"><span class="stat-label">PAS</span><span class="stat-value" id="val3">91</span></div>
                    <div class="stat-item"><span class="stat-label">DRİ</span><span class="stat-value" id="val4">96</span></div>
                    <div class="stat-item"><span class="stat-label">DEF</span><span class="stat-value" id="val5">42</span></div>
                    <div class="stat-item"><span class="stat-label">FİZ</span><span class="stat-value" id="val6">84</span></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const countryCodes = {"TR": "Türkiye", "BR": "Brezilya", "PT": "Portekiz", "AR": "Arjantin", "FR": "Fransa", "DE": "Almanya", "IT": "İtalya"};
        
        // Renkler ve İsim Boyutları (Epic ve Showtime büyütüldü, Renkler güncellendi)
        const cardDatabase = {
            efootball: [
                { id: "bigtime", name: "Big Time", file: "/static/kartlar/big time.jpg", config: { imgTop: "25px", imgRight: "15px", imgWidth: "165px", imgHeight: "235px", ratingTop: "65px", ratingLeft: "32px", posTop: "110px", posLeft: "34px", flagTop: "140px", flagLeft: "37px", logoTop: "168px", logoLeft: "32px", nameTop: "276px", nameSize: "25px", statsBottom: "48px", statsLeft: "42px", color: "white" }},
                { id: "cark", name: "Çark", file: "/static/kartlar/çark.jpg", config: { imgTop: "28px", imgRight: "15px", imgWidth: "160px", imgHeight: "230px", ratingTop: "60px", ratingLeft: "35px", posTop: "105px", posLeft: "37px", flagTop: "135px", flagLeft: "40px", logoTop: "162px", logoLeft: "35px", nameTop: "280px", nameSize: "26px", statsBottom: "45px", statsLeft: "40px", color: "white" }},
                { id: "epic", name: "Epic", file: "/static/kartlar/epic.jpg", config: { imgTop: "25px", imgRight: "15px", imgWidth: "165px", imgHeight: "235px", ratingTop: "65px", ratingLeft: "32px", posTop: "110px", posLeft: "34px", flagTop: "140px", flagLeft: "37px", logoTop: "168px", logoLeft: "32px", nameTop: "275px", nameSize: "29px", statsBottom: "46px", statsLeft: "42px", color: "black" }},
                { id: "showtime", name: "Show Time", file: "/static/kartlar/show time.jpg", config: { imgTop: "26px", imgRight: "15px", imgWidth: "165px", imgHeight: "235px", ratingTop: "62px", ratingLeft: "34px", posTop: "108px", posLeft: "36px", flagTop: "138px", flagLeft: "39px", logoTop: "164px", logoLeft: "34px", nameTop: "280px", nameSize: "30px", statsBottom: "44px", statsLeft: "40px", color: "white" }}
            ],
            fifa: [
                { id: "fc25icon", name: "FC25 Icon", file: "/static/kartlar/fc25-icon.png", config: { imgTop: "68px", imgRight: "32px", imgWidth: "168px", imgHeight: "202px", ratingTop: "75px", ratingLeft: "42px", posTop: "118px", posLeft: "45px", flagTop: "145px", flagLeft: "48px", logoTop: "172px", logoLeft: "43px", nameTop: "283px", nameSize: "26px", statsBottom: "55px", statsLeft: "52px", color: "black" }},
                { id: "fifagold", name: "FIFA Gold", file: "/static/kartlar/fifa gold.png", config: { imgTop: "68px", imgRight: "35px", imgWidth: "162px", imgHeight: "202px", ratingTop: "75px", ratingLeft: "45px", posTop: "118px", posLeft: "48px", flagTop: "145px", flagLeft: "51px", logoTop: "172px", logoLeft: "46px", nameTop: "283px", nameSize: "26px", statsBottom: "55px", statsLeft: "54px", color: "white" }}
            ]
        };
        
        let currentMode = 'efootball'; let rawPlayerData = null; let rawLogoData = null;

        function toggleHelp(id) {
            const el = document.getElementById(id);
            el.style.display = (el.style.display === "block") ? "none" : "block";
        }

        function switchGame(game) {
            currentMode = game;
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`btn-${game}`).classList.add('active');
            
            const select = document.getElementById('cardTemplate'); select.innerHTML = '';
            cardDatabase[game].forEach(t => { let opt = document.createElement('option'); opt.value = t.id; opt.innerText = t.name; select.appendChild(opt); });
            updateCardTemplate();
        }

        function updateCardTemplate() {
            const select = document.getElementById('cardTemplate'); const currentCard = cardDatabase[currentMode].find(c => c.id === select.value); if (!currentCard) return;
            document.getElementById('playerCard').style.backgroundImage = `url('${currentCard.file}')`;
            const cfg = currentCard.config; const container = document.getElementById('cardImageContainer');
            
            container.style.top = cfg.imgTop; container.style.right = cfg.imgRight; container.style.width = cfg.imgWidth; container.style.height = cfg.imgHeight;
            document.getElementById('cardRating').style.top = cfg.ratingTop; document.getElementById('cardRating').style.left = cfg.ratingLeft;
            document.getElementById('cardPosition').style.top = cfg.posTop; document.getElementById('cardPosition').style.left = cfg.posLeft;
            document.getElementById('cardNation').style.top = cfg.flagTop; document.getElementById('cardNation').style.left = cfg.flagLeft;
            document.getElementById('cardTeamLogo').style.top = cfg.logoTop; document.getElementById('cardTeamLogo').style.left = cfg.logoLeft;
            
            const nameEl = document.getElementById('cardName');
            nameEl.style.top = cfg.nameTop; 
            nameEl.style.fontSize = cfg.nameSize;
            nameEl.style.color = cfg.color;
            
            const statsEl = document.getElementById('cardStats');
            statsEl.style.bottom = cfg.statsBottom; 
            statsEl.style.left = cfg.statsLeft;
            statsEl.style.color = cfg.color;
        }

        function handlePlayerImage(e) {
            const file = e.target.files[0]; if (!file) return;
            const isAiEnabled = document.getElementById('aiCropToggle').checked;
            const statusEl = document.getElementById('aiStatus');

            const reader = new FileReader();
            reader.onload = function(event) {
                const base64Raw = event.target.result.split(',')[1];
                if (!isAiEnabled) {
                    document.getElementById('cardImage').src = event.target.result;
                    rawPlayerData = base64Raw;
                    return;
                }

                statusEl.style.display = 'block';
                fetch('/api/remove-bg', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image: base64Raw })
                })
                .then(res => res.json())
                .then(data => {
                    statusEl.style.display = 'none';
                    if(data.success) {
                        document.getElementById('cardImage').src = 'data:image/png;base64,' + data.image;
                        rawPlayerData = data.image;
                    } else {
                        document.getElementById('cardImage').src = event.target.result;
                        rawPlayerData = base64Raw;
                    }
                })
                .catch(() => {
                    statusEl.style.display = 'none';
                    document.getElementById('cardImage').src = event.target.result;
                    rawPlayerData = base64Raw;
                });
            };
            reader.readAsDataURL(file);
        }

        function handleTeamLogo(e) {
            const file = e.target.files[0]; const reader = new FileReader();
            reader.onload = function(event) { document.getElementById('cardTeamLogo').src = event.target.result; rawLogoData = event.target.result.split(',')[1]; };
            if(file) reader.readAsDataURL(file);
        }

        function updateNation() { const code = document.getElementById('nationSelect').value; document.getElementById('cardNation').src = `https://flagcdn.com/w40/${code.toLowerCase()}.png`; }
        function updateCardText() { document.getElementById('cardName').innerText = document.getElementById('nameInput').value; document.getElementById('cardRating').innerText = document.getElementById('ratingInput').value; document.getElementById('cardPosition').innerText = document.getElementById('posInput').value; for (let i = 1; i <= 6; i++) { document.getElementById(`val${i}`).innerText = document.getElementById(`s${i}`).value; } }

        function downloadCardServer() {
            const select = document.getElementById('cardTemplate');
            const payload = { template_id: select.value, name: document.getElementById('nameInput').value, rating: document.getElementById('ratingInput').value, position: document.getElementById('posInput').value, nation: document.getElementById('nationSelect').value, player_img: rawPlayerData, logo_img: rawLogoData, stats: [document.getElementById('s1').value, document.getElementById('s2').value, document.getElementById('s3').value, document.getElementById('s4').value, document.getElementById('s5').value, document.getElementById('s6').value] };
            fetch('/api/download-card', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }).then(res => res.blob()).then(blob => { const link = document.createElement('a'); link.download = `${payload.name}-Card.png`; link.href = URL.createObjectURL(blob); link.click(); });
        }

        window.onload = function() { const select = document.getElementById('nationSelect'); for (let key in countryCodes) { let opt = document.createElement('option'); opt.value = key; opt.innerText = countryCodes[key]; select.appendChild(opt); } switchGame('efootball'); updateNation(); updateCardText(); };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_content)

@app.route('/api/remove-bg', methods=['POST'])
def remove_background_api():
    try:
        data = request.json
        img_b64 = data.get('image')
        if not img_b64:
            return jsonify({"success": False, "error": "Resim verisi bulunamadı"})
        
        img_bytes = base64.b64decode(img_b64)
        input_image = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        output_image = remove(input_image)
        
        buffered = io.BytesIO()
        output_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return jsonify({"success": True, "image": img_str})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/download-card', methods=['POST'])
def download_card():
    data = request.json
    t_id = data.get('template_id', 'bigtime')
    cfg = CONFIG_DB.get(t_id, CONFIG_DB["bigtime"])
    
    base_card = Image.open(cfg["path"]).convert("RGBA")
    draw = ImageDraw.Draw(base_card)
    
    if data.get('player_img'):
        p_bytes = base64.b64decode(data['player_img'])
        p_img = Image.open(io.BytesIO(p_bytes)).convert("RGBA")
        box = cfg["img_box"]
        p_img = p_img.resize((box[2]-box[0], box[3]-box[1]))
        base_card.paste(p_img, (box[0], box[1]), p_img)

    if data.get('logo_img'):
        l_bytes = base64.b64decode(data['logo_img'])
        l_img = Image.open(io.BytesIO(l_bytes)).convert("RGBA")
        l_img = l_img.resize((42, 42))
        base_card.paste(l_img, cfg["logo_pos"], l_img)

    try:
        nat_code = data.get('nation', 'TR').lower()
        import requests
        nat_resp = requests.get(f"https://flagcdn.com/w40/{nat_code}.png")
        flag_img = Image.open(io.BytesIO(nat_resp.content)).convert("RGBA")
        flag_img = flag_img.resize((30, 20))
        base_card.paste(flag_img, cfg["flag_pos"], flag_img)
    except: pass

    try:
        font_main = ImageFont.load_default()
        draw.text(cfg["rating_pos"], data.get('rating', '97'), fill="white", font=font_main)
        draw.text(cfg["pos_pos"], data.get('position', 'ST'), fill="white", font=font_main)
        
        fill_color = cfg["text_color"]
        name = data.get('name', 'GOAT').upper()
        draw.text((160 - len(name)*3, cfg["name_y"]), name, fill=fill_color, font=font_main)
    except: pass
    
    img_io = io.BytesIO()
    base_card.save(img_io, 'PNG', quality=100)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)