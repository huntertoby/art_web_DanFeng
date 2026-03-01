from flask import Flask, render_template

app = Flask(__name__)

# 完整的展覽核心資料，圖片路徑對應 static 目錄下的本機檔案
EXHIBITION_DATA = {
    "超級比一比": [
        {
            "id": "B-02", "title": "聖母與聖子 Icon of the Virgin and Child", "artist": "佚名", "year": "約1203",
            "location": "Basilica di San Marco, Venice, Italy",
            "desc": "畫中表情莊嚴的聖母與聖子，襯上金光閃閃的背景，是不是讓人感受到中世紀畫家想強調對宗教人物的敬仰呢？",
            "question": "中世紀畫家如何表現對宗教人物的敬仰？",
            "img": "/static/04聖母與聖子.jpg"
        },
        {
            "id": "B-03", "title": "聖母子與天使 Madonna Enthroned", "artist": "奇馬布伊 Cimabue", "year": "約1290",
            "location": "Galleria degli Uffizi, Florence, Italy",
            "desc": "坐在椅子上的聖母與聖子與身旁圍繞的天使與聖徒，讓畫面呈現空間感，但人物大小與位置安排有點奇怪，找找看有哪些不合理的地方？",
            "question": "畫面中有哪些不合理的地方？",
            "img": "/static/05聖母子與天使.jpg"
        },
        {
            "id": "B-04", "title": "大公爵聖母 The Grand Duke's Madonna", "artist": "拉斐爾 Raphael Santi", "year": "1504-05",
            "location": "Palazzo Pitti, Florence, Italy",
            "desc": "文藝復興時期的畫家拉斐爾所畫的聖母與聖子，比起中世紀同樣的聖母題材繪畫有何不同呢？",
            "question": "拉斐爾的聖母與中世紀的聖母有何不同？",
            "img": "/static/大公爵聖母.jpg"
        }
    ],
    "完美無所不在": [
        {
            "id": "C-02", "title": "哀悼耶穌 The Lamentation of Christ", "artist": "喬托 Giotto", "year": "1305",
            "location": "Scrovegni(Arena) Chapel, Padua, Italy",
            "desc": "喬托試圖表現出耶穌逝去的戲劇性時刻，讓人深深感受到畫中人物們的悲痛與哀悽。",
            "question": "喬托如何表現悲痛與哀悽？",
            "img": "/static/08哀悼耶穌.jpg"
        },
        {
            "id": "C-03", "title": "聖三位一體 The Trinity", "artist": "馬薩奇歐 Masaccio", "year": "1425-28",
            "location": "Santa Maria Novella, Florence, Italy",
            "desc": "這幅壁畫真實的就像牆面上鑿出一個空間，透視技法可以表現視覺上的幻象，在平面上創造出空間與距離感。",
            "question": "這幅畫如何創造出空間感？",
            "img": "/static/09聖三位一體.jpg"
        },
        {
            "id": "C-04", "title": "聖馬諾之戰 The Battle of San Romano", "artist": "烏切羅 Uccello", "year": "1438-40",
            "location": "National Gallery, London, UK",
            "desc": "烏切羅為了追求真實，窮其一生都在鑽研透視技法，在這幅畫中他是如何運用的呢？仔細觀察地上的線索吧！",
            "question": "找找看地上的透視線索！",
            "img": "/static/10聖羅馬諾之戰.jpg"
        },
        {
            "id": "C-05", "title": "維納斯的誕生 The Birth of Venus", "artist": "波提切利 Botticelli", "year": "1484-86",
            "location": "Galleria degli Uffizi, Florence, Italy",
            "desc": "維納斯是希臘神話中代表「愛與美」的女神，這幅畫中波提切利描繪的維納斯形象，是不是顯得優雅又迷人呢？",
            "question": "你覺得維納斯優雅迷人嗎？",
            "img": "/static/11維納斯的誕生.jpg"
        },
        {
            "id": "C-06", "title": "天堂之門（局部） Porta del Paradiso", "artist": "吉貝爾蒂 Ghiberti", "year": "1425-52",
            "location": "Battistero di San Giovanni, Florence, Italy",
            "desc": "吉貝爾蒂以透視技法將場景及人物表現得很真實；他花了近30年才完成《天堂之門》的浮雕作品，是不是很驚人呢？",
            "question": "這件作品花了多久完成？",
            "img": "/static/12天堂之門(局部).jpg"
        },
        {
            "id": "C-07", "title": "大衛像 David", "artist": "多那太羅 Donatello", "year": "1440",
            "location": "Museo Nazionale del Bargello, Florence, Italy",
            "desc": "多那太羅表現《聖經》故事中大衛取得勝利踩著巨人哥利亞的樣子，為了準確呈現人體構造，他還研究解剖學呢！",
            "question": "為了準確呈現人體，藝術家做了什麼？",
            "img": "/static/13大衛像.jpg"
        },
        {
            "id": "C-08", "title": "聖喬治像 St. George", "artist": "多那太羅 Donatello", "year": "1416-17",
            "location": "Museo Nazionale del Bargello, Florence, Italy",
            "desc": "「聖喬治屠龍」是西方流傳的古老傳說；聖喬治即將出發拯救被惡龍攻擊的村莊，你感受到他臉上那股意氣風發的自信嗎？",
            "question": "你感受到他的自信了嗎？",
            "img": "/static/14聖喬治像.jpg"
        },
        {
            "id": "C-09", "title": "聖母百花大教堂(圓頂)", "artist": "布魯內利奇 Filippo Brunelleschi", "year": "1419-36",
            "location": "Florence, Italy",
            "desc": "圓頂是文藝復興建築的代表象徵，這可是當時最創新的建築方法。想一想，這樣的圓頂是如何蓋出來的？",
            "question": "這樣的圓頂是如何蓋出來的？",
            "img": "/static/15聖母百花大教堂(圓頂).jpg"
        },
        {
            "id": "C-10", "title": "聖安德烈教堂 Basilica of Sant’ Andrea", "artist": "阿爾伯蒂 Leon Battista Alberti", "year": "1472-1790",
            "location": "Mantua, Italy",
            "desc": "仔細觀察這棟建築正面的左右兩邊，是不是像照鏡子一樣？這樣的對稱形式，是不是有一種穩定的感覺呢？",
            "question": "對稱形式帶來什麼感覺？",
            "img": "/static/16聖安德烈教堂.jpg"
        }
    ],
    "大師工作坊": [
        {
            "id": "D-02", "title": "聖殤 The Pieta", "artist": "米開朗基羅 Michelangelo", "year": "1498-99",
            "location": "St. Peter's Basilica, Vatican City",
            "desc": "這件作品表現出藝術家細膩的情感與高超技巧，為了讓大家記住，藝術家還刻上自己的大名，找找看在哪裡呢？",
            "question": "找找看藝術家的名字在哪裡？",
            "img": "/static/21聖殤.jpg"
        },
        {
            "id": "D-03", "title": "大衛 David", "artist": "米開朗基羅 Michelangelo", "year": "1501-04",
            "location": "Galleria dell'Accademia, Florence, Italy",
            "desc": "米開朗基羅擅長以完美的肌肉線條來表現人體的力量感，大衛側身站立，迎面而戰巨人哥利亞，隨著他的眼神看去，氣勢凌人。",
            "question": "米開朗基羅擅長表現什麼？",
            "img": "/static/23大衛.jpg"
        },
        {
            "id": "D-04", "title": "聖彼得教堂圓頂設計草稿", "artist": "米開朗基羅 Michelangelo", "year": "1546",
            "location": "Study for St. Peter’s Dome",
            "desc": "米開朗基羅繪製了許多圓頂建築草圖，比比看和聖母百花大教堂有何不同？",
            "question": "和聖母百花大教堂有何不同？",
            "img": "/static/25聖彼得教堂圓頂設計草稿.jpg"
        }
    ],
    "天才達人大集合": [
        {
            "id": "E-02", "title": "維特魯威人", "artist": "達文西 Leonardo da Vinci", "year": "1492",
            "location": "Galleria dell’Accademia, Venice, Italy",
            "desc": "這是達文西所畫的人體比例圖，找找看其中藏著什麼完美比例呢？下方的筆記文字，又有何特別之處？",
            "question": "其中藏著什麼完美比例？",
            "img": "/static/28維特魯威人.jpg"
        },
        {
            "id": "E-03", "title": "蒙娜麗莎 Mona Lisa", "artist": "達文西 Leonardo da Vinci", "year": "1503-06",
            "location": "Louvre, Paris, France",
            "desc": "蒙娜麗莎的那一抹淺淺微笑，你知道藝術家施了什麼樣的魔法嗎？你可以說出這幅畫還蘊藏了多少精采故事呢？",
            "question": "藝術家施了什麼魔法？",
            "img": "/static/29蒙娜麗莎.jpg"
        },
        {
            "id": "E-04", "title": "最後的晚餐 The Last Supper", "artist": "達文西 Leonardo da Vinci", "year": "1495-98",
            "location": "Santa Maria della Grazie, Milan, Italy",
            "desc": "你知道「最後的晚餐」這個聖經故事嗎？達文西描繪這個極富戲劇性的情節，找找看誰是那個出賣耶穌的人呢？",
            "question": "找找看誰是出賣耶穌的人？",
            "img": "/static/30最後的晚餐.jpg"
        },
        {
            "id": "E-05", "title": "飛行器 Macchina Volante", "artist": "達文西 Leonardo da Vinci", "year": "1505",
            "location": "Draft Design",
            "desc": "達文西懷抱著飛行夢，所以他花了許多時間設計草稿，你是否也有什麼天馬行空的想像與發明呢？",
            "question": "你也有天馬行空的想像嗎？",
            "img": "/static/31飛行器.jpg"
        },
        {
            "id": "E-06", "title": "聖母與聖嬰習作", "artist": "米開朗基羅 Michelangelo", "year": "1530-32",
            "location": "British Museum, London, UK",
            "desc": "聖子與聖母身體的親密交疊是文藝復興時期突破性的表現，這種表現方法，是不是給人更生動親切的感受呢？",
            "question": "這種表現方法給人什麼感受？",
            "img": "/static/32聖母與聖嬰習作.jpg"
        },
        {
            "id": "E-07", "title": "摩西 Moses", "artist": "米開朗基羅 Michelangelo", "year": "1513-15",
            "location": "San Pietro in Vincoli, Rome, Italy",
            "desc": "摩西是猶太民族的英雄領袖。米開朗基羅以一位智者的形象描繪他，栩栩如生的樣貌，可看出藝術家純熟的雕刻技術。",
            "question": "米開朗基羅如何描繪摩西？",
            "img": "/static/33摩西.jpg"
        },
        {
            "id": "E-08", "title": "創造亞當 The Creation of Adam", "artist": "米開朗基羅 Michelangelo", "year": "1511",
            "location": "Sistine Chapel Ceiling, Musei Vaticani",
            "desc": "畫面中兩隻手交會的一瞬間，象徵上帝為人類注入滿滿的生命、智慧與力量，你是否感受到了那股能量呢？",
            "question": "兩隻手交會象徵什麼？",
            "img": "/static/34創造亞當.jpg"
        },
        {
            "id": "E-09", "title": "最後的審判 The Last Judgment", "artist": "米開朗基羅 Michelangelo", "year": "1537-41",
            "location": "Sistine Chapel , Musei Vaticani",
            "desc": "「最後的審判」是聖經故事，描繪末日來臨的景象，仔細觀察畫面中蘊藏了多少故事？找找看，米開朗基羅也將自己畫在裡面喔！",
            "question": "找找看，米開朗基羅在哪裡？",
            "img": "/static/35最後的審判.jpg"
        },
        {
            "id": "E-10", "title": "雅典學院 School of Athens", "artist": "拉斐爾 Raphael Santi", "year": "1510-11",
            "location": "Apostolic Palace, Musei Vaticani",
            "desc": "這幅畫中的人物有許多不同時代、不同學術領域的偉大著名學者，他們正在專注討論著各種重要事情，你知道有誰嗎？",
            "question": "你知道畫中有哪些學者嗎？",
            "img": "/static/36雅典學院.jpg"
        },
        {
            "id": "E-11", "title": "草地上的聖母 Madonna del Prato", "artist": "拉斐爾 Raphael Santi", "year": "1506",
            "location": "Kunsthistorisches Museum, Vienna, Austria",
            "desc": "拉斐爾總能將聖母祥和、溫暖的氣質表現得淋漓盡致，而小耶穌與小施洗者約翰，則如一般孩子般調皮活潑。",
            "question": "拉斐爾如何表現聖母？",
            "img": "/static/37草地上的聖母.jpg"
        }
    ]
}

@app.route('/')
def index():
    return render_template('index.html', exhibition_data=EXHIBITION_DATA)

if __name__ == '__main__':
    app.run(debug=True, port=5000)