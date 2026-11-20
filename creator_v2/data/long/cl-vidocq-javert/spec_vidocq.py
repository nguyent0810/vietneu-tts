"""Ghi spec.json (youtube, credits, mix, look...) cho cl-vidocq-javert. Gọi từ gen_scenes.py sau khi ghi cảnh.

Tác giả/giấy phép lấy từ API Wikimedia Commons ngày 18/11/2026 (bảng CREDITS). Ảnh không có tác giả ghi rõ không dùng
(đã loại: bản Bertillon, ảnh minh họa "Mysteries of Police and Crime", Balzac Old Goriot, các ảnh Gallica/BnF không tác giả).
publish_at đặt theo ticket GH-476; `approved` để trống (Lead/chủ kênh quyết).
"""
import json
import urllib.parse
from pathlib import Path

D = Path(__file__).resolve().parent

TITLES = ['Vidocq: Tù Khổ Sai Tám Năm Thành Sếp Mật Vụ Paris',
          'Javert Có Thật: Gã Tù Vượt Ngục Cầm Đầu Mật Vụ Paris',
          'Vidocq: Từ Xích Khổ Sai Đến Ghế Sếp, Rồi Bị Xóa Tên']
TITLE = TITLES[0]
LOOK = 'sulfur'    # CL gần đây: amber (Sarin), steel, classic, rose; sulfur lần cuối 22/11 (dong-lang)

CREDITS = {
    'File:20. Mort de Jean Valjean Nuit derrière laquelel il y a le jour, 2019.4.5.3.jpg': ('Alphonse de Neuville', 'CC0'),
    'File:27. Les Misérables, partie V, livre IV Javert déraillé, 2013.7.3g.jpg': ('Ricardo de los Rios / After François Flameng', 'CC0'),
    'File:5. Jean Valjean au bagne Le Numéro 24,601 devient le numéro 9,436, 2019.4.2.2.jpg': ('Alphonse de Neuville', 'CC0'),
    'File:569 Brest musée beaux-arts Jules Noël Attelage de forçats.jpg': ('Jules Achille Noël', 'Public domain'),
    'File:580 Brest musée beaux-arts Jules Noël Le travail dans le port.jpg': ('Jules Achille Noël', 'Public domain'),
    'File:7. Javert sur les traces de Jean Valjean Où il est expliqué comment Javert a fait buisson creux Les Misérables, 2017.0.2927.7.jpg': ('Jean Outhwaite / After Alphonse de Neuville', 'CC0'),
    'File:A. FAYARD Editr. 78, Bould. St. Michel, PARIS LES NUITS DU BOULEVARD PAR PIERRE ZACONNE DESSINS de P. KAUFFMANN G, AFF2560.jpg': ('Kauffmann, Paul Adolphe (Belfort, en 08–07–1849 - Grimault, en 20–02–1940), dessinateur', 'CC0'),
    'File:Achille Devéria - Vidocq.jpg': ('Achille Devéria', 'Public domain'),
    "File:Anastay en cour d'assises (Univers illustré, 1892-03-05).jpeg": ('Paul Destez', 'Public domain'),
    'File:Antoine Choquet de Lindu - élévation du bagne de Brest du côté du port.jpg': ('Antoine Choquet de Lindu', 'Public domain'),
    'File:Bagne de Brest extrait registre 1792.jpg': ('TigH', 'Public domain'),
    'File:Bagne de Toulon.jpg': ('Pierre Zaccone', 'Public domain'),
    'File:Balzac Boulanger.jpg': ('Louis Boulanger', 'CC BY-SA 3.0'),
    'File:Balzac Gérard-Séguin.jpg': ('Jean Alfred Gérard-Séguin', 'Public domain'),
    'File:BalzacSplendorsMiseries02.jpg': ('Gaston Bussière', 'Public domain'),
    'File:Bazar Bagne de Toulon.jpg': ('Pierre Zaccone', 'Public domain'),
    'File:Bonnat Hugo001z.jpg': ('Léon Bonnat', 'Public domain'),
    'File:Charles Hugo Portrait of Victor Hugo c1853.jpg': ('Charles Hugo', 'Public domain'),
    'File:Charles Marville, Rue de Harlay au Palais, ca. 1853–70.jpg': ('Charles Marville', 'Public domain'),
    'File:Choquet De Lindu P1 - Le plan et les profils de la forme de Brest.jpg': ('Antoine Choquet de Lindu', 'Public domain'),
    'File:Choquet De Lindu P10 - Plan du bagne et le profil en long en quatre parties.jpg': ('Antoine Choquet de Lindu', 'Public domain'),
    'File:Choquet De Lindu P3 - Plan des trois formes.jpg': ('Antoine Choquet de Lindu', 'Public domain'),
    "File:Choquet De Lindu P4 - élévation de l'entrée des formes.jpg": ('Antoine Choquet de Lindu', 'Public domain'),
    'File:Choquet De Lindu P5 - Profil en long de la seconde et troisième forme.jpg': ('Antoine Choquet de Lindu', 'Public domain'),
    "File:Choquet De Lindu P6 - Profil de la première forme et d'un vaisseau de 100 canons.jpg": ('Antoine Choquet de Lindu', 'Public domain'),
    "File:Choquet De Lindu P9 - Plan des fondemens du bagne et l'élévation du côté du port.jpg": ('Antoine Choquet de Lindu', 'Public domain'),
    'File:Choses vues, 1846, Visite à la Conciergerie La grande galerie, 2017.0.2000.4.jpg': ('Anonyme, graveur', 'CC0'),
    'File:Choses vues, 1846, Visite à la Conciergerie La porte du quai, 2017.0.2005.jpg': ('Anonyme, graveur', 'CC0'),
    'File:Choses vues, 1846, Visite à la Conciergerie La salle des cheminées, 2017.0.2004.2.jpg': ('Charles Fichot', 'CC0'),
    'File:Choses vues, 1846, Visite à la Conciergerie Le préau des hommes, 2017.0.2001.2.jpg': ('Anonyme, graveur', 'CC0'),
    "File:Collection d'autographes, de dessins et de portraits de personnages célèbres, français et étrangers, du XVIe au XIXe siècle, formée par Alexandre Bixio. XVIe-XIXe siècle. VIII. S - Z - btv1b10028242b (591 of 618).jpg": ('Sacchi, Andrea (1599-1661). Dessinateur Saint-Aubin, Augustin de (1736-1807). Graveur Quenedey, Edme (1756-183', 'Public domain'),
    'File:DIV CondamnationBagne.jpg': ('unknown, but probably a court clerk or prison official; scan by Defosse Philippe (author of the website http:/', 'Public domain'),
    'File:Emile Bayard - Cosette.jpg': ('Émile Bayard', 'Public domain'),
    'File:Escape attempt in Bagne de Toulon.jpg': ('Pierre Zaccone', 'Public domain'),
    'File:FMIB 36944 Galere Ordinaire la Dauphine (1690-1715).jpeg': ('Georges Clerc-Rampal', 'Public domain'),
    'File:Forçats au travail 2001-34-20.jpg': ('Alfred Bernier', 'Public domain'),
    "File:Frank Boggs, La Conciergerie et le marché aux fleurs, vers 1906, Musée d'art et d'histoire de la ville de Meudon.jpg": ('Armande Béjart', 'CC BY-SA 4.0'),
    'File:George Cruikshank - Vidocq and the hump-back.jpg': ('George Cruikshank', 'Public domain'),
    'File:George Cruikshank - Vidocq and the old gallery guard.jpg': ('George Cruikshank', 'Public domain'),
    'File:George Cruikshank - Vidocq arresting Pons.jpg': ('George Cruikshank', 'Public domain'),
    'File:George Cruikshank - Vidocq discovers the doctor.jpg': ('George Cruikshank', 'Public domain'),
    'File:George Cruikshank - Vidocq escaping by means of the Fosse Family.jpg': ('George Cruikshank', 'Public domain'),
    'File:George Cruikshank - Vidocq pursued by gendarmes.jpg': ('George Cruikshank', 'Public domain'),
    'File:Grundriss der Statt Douay mit dem ungefähr 800 Ruthen davon entlegene... - CBT 6626057.jpg': ('Joseph Friedrich Leopold', 'Public domain'),
    'File:Gustave Brion, Javert, 1862 - Les Misérables, G. Routledge and Sons.jpeg': ('Gustave Brion', 'Public domain'),
    'File:Honoré Daumier 026.jpg': ('Honoré Daumier', 'Public domain'),
    'File:Honoré de Balzac (1842).jpg': ('Louis-Auguste Bisson', 'Public domain'),
    'File:Hôpital du Kremlin-Bicêtre.jpg': ('Eugène Atget', 'Public domain'),
    'File:Hôtel ville St Mandé 13.jpg': ('Chabe01', 'CC BY-SA 4.0'),
    'File:Jan van Grevenbroeck - Galley slave.jpg': ('Jan van Grevenbroeck (1731-1807)', 'Public domain'),
    'File:Javert.jpg': ('Gustave Brion', 'Public domain'),
    'File:Kaart van Arras, 1712 Plan de la Ville, et Citadelle de Arras etc. (titel op object), RP-P-OB-83.434.jpg': ('Rijksmuseum', 'CC0'),
    "File:La Bienfaisance à Paris. L'Œuvre de l'Hospitalité de nuit. Le refuge de la rue de Tocqueville, n° 59, siège de l'Œuvre, G.37761(1).jpg": ('Régnier, Isidore, graveur', 'CC0'),
    "File:La Bienfaisance à Paris. L'Œuvre de l'Hospitalité de nuit. Le refuge de la rue de Tocqueville, n° 59, siège de l'Œuvre, G.37761(2).jpg": ('Régnier, Isidore, graveur', 'CC0'),
    'File:La prison de Bicêtre à Gentilly - la toilette des forçats avant le départ de la chaîne.jpg': ('Gabriel Cloquemin', 'Public domain'),
    'File:La prison de Bicêtre à Gentilly - le ferrement des forçats.jpg': ('Gabriel Cloquemin', 'Public domain'),
    'File:La prison de Bicêtre à Gentilly - le sermon avant le départ de la chaîne des forçats.jpg': ('Gabriel Cloquemin', 'Public domain'),
    'File:La prison de Bicêtre à Gentilly la toilette des forçats avant le départ de la chaîne. D.3172.jpg': ('Cloquemin, Gabriel, dessinateur', 'CC0'),
    'File:La prison de Bicêtre à Gentilly le départ de la chaîne des forçats. D.3173.jpg': ('Cloquemin, Gabriel, dessinateur', 'CC0'),
    'File:La prison de Bicêtre à Gentilly le ferrement des foçats. D.3171.jpg': ('Cloquemin, Gabriel, dessinateur', 'CC0'),
    'File:La prison de Bicêtre à Gentilly le sermon avant le départ de la chaîne des forçats. D.3170.jpg': ('Cloquemin, Gabriel, dessinateur', 'CC0'),
    'File:La prison de Bicêtre à Gentilly. Le départ de la chaîne des forçats - Gabriel Cloquemin.jpg': ('Gabriel Cloquemin', 'Public domain'),
    'File:La prison du Prince Napoléon à la Conciergerie. G.23537.jpg': ('Tilly, Auguste (Toul, en 1840 - en 1898), graveur', 'CC0'),
    'File:La queue devant le spectacle, BAL2002.75.jpg': ('Daumier, Honoré (Marseille, 26–02–1808 - Valmondois, 10–02–1879), dessinateur-lithographe', 'CC0'),
    'File:LaForcePrisonParis.jpg': ('Marlet', 'Public domain'),
    "File:Le Pont au Change, le palais (conciergerie) et la Seine vers l'aval, actuel 1er arrondissement, D.464.jpg": ('Garbizza, Angelo (Italie, en 1777 - Trévise, 04–05–1813), dessinateur', 'CC0'),
    'File:Le vol au renfoncement, BAL2002.563.jpg': ('Daumier, Honoré (Marseille, 26–02–1808 - Valmondois, 10–02–1879), dessinateur-lithographe', 'CC0'),
    'File:Les Misérables - Cab roule en anglais.jpg': ('Fernand Desmoulin / After Pierre-Georges Jeanniot', 'Public domain'),
    'File:Les Misérables - Le désœuvrement de M. Bamatabois - Pierre Georges Jeanniot.jpg': ('Pierre-Georges Jeanniot', 'Public domain'),
    'File:Les Misérables - L’autorité reprend ses droits.jpg': ('Pierre-Georges Jeanniot', 'Public domain'),
    "File:Les Misérables, Cinquième partie, Livre troisième, chapitre IX Javert l'examina et le reconnut, 2017.0.2889.jpg": ('Edmond Yon / After Gustave Brion', 'CC0'),
    'File:Les Misérables, Première partie Fantine Fantine aux pieds de Javert, 2017.0.1539.jpg': ('Fortuné Méaulle / After Alphonse de Neuville', 'CC0'),
    'File:Les Misérables, Première partie Fantine Javert le regardait toujours, 2017.0.1536.1.jpg': ('Inconnu, graveur', 'CC0'),
    'File:Les Misérables, Première partie, Livre sixième, chapitre I Javert, 2017.0.2760.jpg': ('After Gustave Brion', 'CC0'),
    'File:Lille Douai Louvain Bruxelles Paris 1786.JPG': ('William Robert Shepherd', 'Public domain'),
    'File:Livret pour Les Misérables, édition Jules Rouff et Cie. 2017.0.29012.jpg': ('Albert Bellenger / After Émile Bayard', 'CC0'),
    'File:Margaret Bernardine Hall - Fantine - Google Art Project.jpg': ('Margaret Bernadine Hall', 'Public domain'),
    'File:Marine France conge du bagne.jpg': ('TigH', 'Public domain'),
    'File:Monsieur Madeleine par Gustave Brion.jpg': ('Gustave Brion', 'Public domain'),
    "File:PRETRES CONDUITS A LA CONCIERGERIE. - Leur arrivée dans la cour d'entrée. Paris Musées 20230515125409.jpg": ('Burn-Smeeton, Joseph, graveur', 'CC0'),
    "File:Palais de Justice - tribunal de Commerce - Préfecture de Police - St Germain l'Auxerrois, Louvre - dessin - Jules-Adolphe Chauvet - btv1b8456008m.jpg": ('Clerget, Hubert (1818-1899). Dessinateur', 'Public domain'),
    'File:Paris. La rue de la Montagne Ste Geneviève, G.5293(2).jpg': ('Lepère, Auguste (Montmartre (ancienne commune), 30–11–1849 - Domme, 20–11–1918), graveur', 'CC0'),
    'File:Paris. La rue de la Montagne Ste Geneviève, G.5293.jpg': ('Lepère, Auguste (Montmartre (ancienne commune), 30–11–1849 - Domme, 20–11–1918), graveur', 'CC0'),
    'File:Permission-de-travestissement 1862.jpg': ('Préfecture de Paris', 'Public domain'),
    "File:Pierre-Jean David d'Angers - Honoré de Balzac (1799-1850) - Walters 54838.jpg": ("David d'Angers", 'Public domain'),
    "File:Plan de Paris, avec indication des rues nouvelles et des travaux en cours d'exécution.jpg": ('Paniconography by Firmin Gillot (b 1820, d 1872). Engraving by F. Delamare.', 'Public domain'),
    "File:Plattegronden van Arras, Béthune en Hesdin, 1726 Arras Bethune Citadelle d'Arras Hesdin (titel op object) Les Forces de l'Europe, Asie, Afrique et Amerique Comme aussi les Cartes des Côtes de France, RP-P-OB-83.035-223.jpg": ('Rijksmuseum', 'CC0'),
    'File:Pont des Saints Peres a Paris - Les Travaux Publics de la France.jpg': ('Auguste Hippolyte Collard', 'Public domain'),
    "File:Portrait d'Eugène Vidocq (1775-1857), aventurier et chef de la police de sûreté. G.12180 (1 of 4).jpg": ('Devéria, Achille (Paris, 06–02–1800 - Paris, 23–12–1857), dessinateur-lithographe', 'CC0'),
    "File:Portrait d'Eugène Vidocq (1775-1857), aventurier et chef de la police de sûreté. G.12180 (3 of 4).jpg": ('Devéria, Achille (Paris, 06–02–1800 - Paris, 23–12–1857), dessinateur-lithographe', 'CC0'),
    "File:Portrait d'Honoré de Balzac (1799-1850), écrivain, S632.jpg": ("David d'Angers, Pierre-Jean (Angers, 12–03–1788 - Paris, 05–01–1856), sculpteur", 'CC0'),
    'File:Portret van Eugène François Vidocq, RP-P-1911-787.jpg': ('Rijksmuseum', 'CC0'),
    "File:Sont-ils fade regarde donc comme ils s'en sauvent , BAL2002.54.jpg": ('Daumier, Honoré (Marseille, 26–02–1808 - Valmondois, 10–02–1879), dessinateur-lithographe', 'CC0'),
    'File:Sortie du Bagne.jpg': ('Rouger', 'Public domain'),
    'File:The Chaine to Bagne of Toulon.jpg': ('Pierre Zaccone', 'Public domain'),
    'File:The Princess Elizabeth taken from the ConciergerieLa Princesse Elizabeth fortant de la Concergerie. G.29620.jpg': ('Schiavonetti, Luigi (Bassano del Grappa, 01–04–1765 - Londres, 07–06–1810), graveur', 'CC0'),
    'File:Toulon- Bagnard.jpg': ('Jules Achille Noël', 'Public domain'),
    'File:Valmy Battle painting.jpg': ('Horace Vernet', 'Public domain'),
    'File:Victor Hugo Charles Hugo François-Victor Hugo.png': ('Henry Mulling', 'Public domain'),
    'File:Victor Hugo by Étienne Carjat 1876 - full.jpg': ('Étienne Carjat', 'Public domain'),
    'File:Victor Hugo portrait by Charles Hugo in Jersey.jpg': ('Charles Hugo', 'Public domain'),
    'File:Victor Hugo-Brooding.jpg': ('Charles Hugo', 'Public domain'),
    'File:Vidocq (1775-1857).jpg': ('Achille Devéria', 'Public domain'),
    'File:Vidocq (BM 1901,1022.926).jpg': ('Print made by: Cäcilie Brandt Print made by: August Kneisel', 'Public domain'),
    'File:Vidocq (cropped).jpg': ('Marie Gabrielle Coignet (1793-?) [1]', 'Public domain'),
    'File:Vidocq - Mémoires - Tome 4 (page 4 crop).jpg': ('François Vidocq', 'Public domain'),
    'File:Vidocq, le roi des voleurs, le roi des policiers.jpg': ('A. Bonnard', 'Public domain'),
    'File:Vidocq.jpg': ('Marie Gabrielle Coignet (1793-?) [1]', 'Public domain'),
    'File:Weg naar Toulon Route de Toulon (titel op object) Allerlei soorten voertuigen (3) (serietitel) Panidochème ou toutes sortes de voitures (3) (serietitel), RP-P-1905-3377.jpg': ('Rijksmuseum', 'CC0'),
    'File:Émile Bayard - Il lui ferma les yeux.jpg': ('Émile Bayard', 'Public domain'),
}


SOURCES = [
    'https://en.wikipedia.org/wiki/Eug%C3%A8ne_Fran%C3%A7ois_Vidocq',
    'https://fr.wikipedia.org/wiki/Eug%C3%A8ne-Fran%C3%A7ois_Vidocq',
    'https://en.wikipedia.org/wiki/Javert',
    'https://en.wikisource.org/wiki/Memoirs_of_Vidocq',
    'https://herodote.net/Un_reprouve_au_coeur_du_pouvoir-synthese-3499-609.php',
    'https://www.retronews.fr/justice/interview/2018/12/18/eugene-francois-vidocq-xavier-mauduit',
    'https://en.wikipedia.org/wiki/Jean_Valjean',
    'https://en.wikipedia.org/wiki/Les_Mis%C3%A9rables',
    'https://en.wikipedia.org/wiki/Bagne_of_Toulon',
    'https://en.wikipedia.org/wiki/Bic%C3%AAtre_Hospital',
    'https://en.wikipedia.org/wiki/Vautrin',
    'https://en.wikipedia.org/wiki/Auguste_Dupin',
]

# Phiên âm cho TTS (spec["say"]; phụ đề vẫn giữ chữ gốc). CHƯA NGHE THỬ: Lead nghe lại CH00-CH01 so với bản chủ kênh đã duyệt.
SAY = {
    'vidocq': 'Vi-đốc', 'javert': 'Gia-ve', 'valjean': 'Van-giăng', 'jean': 'Giăng', 'douai': 'Đu-ê', 'arras': 'A-rát', 'toulon': 'Tu-lông',
    'brest': 'Brét', 'bicêtre': 'Bi-xê-tơ', 'sûreté': 'Xuy-rơ-tê', 'hugo': 'Huy-gô', 'balzac': 'Ban-dắc', 'paris': 'Pa-ri', 'lille': 'Lin',
    'rouen': 'Ru-ăng', 'versailles': 'Vẹc-xây', 'scarpe': 'Xcạp', 'ostende': 'Ốt-xtăng-đơ', 'normandy': 'Noóc-măng-đi', 'london': 'Luân Đôn',
    'pasquier': 'Pát-ki-ê', 'henry': 'Hăng-ri', 'henri': 'Hăng-ri', 'gisquet': 'Gít-kê', 'duplessis': 'Đuy-plê-xi', 'lacour': 'La-cua',
    'coco': 'Cô-cô', 'wettu': 'Vê-tuy', 'herbaux': 'Éc-bô', 'fleuride': 'Phlơ-ri-đơ', 'maniez': 'Ma-ni-ê', 'lamarque': 'La-mác',
    'morice': 'Mô-rít', 'vautrin': 'Vô-trăng', 'dupin': 'Đuy-păng', 'brutus': 'Bờ-ru-tút', 'poe': 'Pô', 'edgar': 'Éch-ga', 'allan': 'A-lân',
    'auguste': 'Ô-guýt', 'charles': 'Sạc', 'jules': 'Duyn', 'louis': 'Lu-i', 'marc': 'Mác', 'victor': 'Vích-to', 'xviii': 'mười tám',
    'amiral': 'A-mi-ran', 'brigade': 'bờ-ri-gát', 'bureau': 'Bu-rô', 'renseignements': 'Răng-xê-nhơ-măng', 'force': 'Phoóc-xơ',
    'galerie': 'Ga-lơ-ri', 'vivienne': 'Vi-vi-en', 'lachaise': 'La-sê', 'lezen': 'Lơ-dăng', 'tour': 'Tua', 'saint-pierre': 'Xanh Pi-e',
    'saint-pierre-popincourt': 'Xanh Pi-e Pô-păng-cua', 'pont-à-lezen': 'Pông-a-lơ-dăng', 'saint-mandé': 'Xanh Măng-đê',
    'sainte-pélagie': 'Xanh Pê-la-gi', 'père-lachaise': 'Pe La-sê',
}


def apply(CH, chapter_titles, used, IMGS):
    path = D / 'spec.json'
    spec = json.loads(path.read_text(encoding='utf-8'))
    used_files = sorted({IMGS[k] for k in used if not str(IMGS[k]).startswith('EXT:')})
    missing = [f for f in used_files if f not in CREDITS or not CREDITS[f][0] or not CREDITS[f][1]]
    if missing:
        raise SystemExit('Thiếu ghi công cho: ' + '; '.join(missing))
    credits = []
    for f in used_files:
        author, lic = CREDITS[f]
        name = f.removeprefix('File:')
        url = 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(f.replace(' ', '_'))
        credits.append(f'{name} — {author} — {lic} — {url}')
    credits.append('Cảnh PHỎNG DỰNG: ảnh tranh do AI tạo dựa trên tư liệu (chân dung Devéria, Hugo, mô tả trong hồi ký), có chip PHỎNG DỰNG trên hình; không phải ảnh chụp hay tranh gốc.')
    credits.append('Clip minh họa chung: một số clip do AI tạo (MINH HỌA CHUNG), một số clip stock Pexels (pexels.com), giấy phép Pexels.')
    for t in TITLES:
        assert len(t) <= 60, (len(t), t)
    spec.pop('_stub', None)
    spec.update({
        'title': TITLE, 'channel': 'CL', 'theme': 'noir', 'look': LOOK, 'autoTr': True, 'master': True, 'craft': True, 'ai_faces': True,
        'endcard': 9, 'endcardSub': 'HỒ SƠ TIẾP THEO',
        'acc': ['vidocq', 'javert', 'valjean', 'sûreté'], 'say': SAY, 'chapters': list(CH),
        'mix_levels': {'CL': {'gain': 0.27, 'threshold': 0.08, 'ratio': 3.0}},
    })
    spec.pop('accent', None)
    yt = spec.setdefault('youtube', {})
    yt.update({
        'titles': TITLES,
        'summary': 'Eugène-François Vidocq (1775–1857): tù khổ sai ba lần vượt ngục, rồi thành người đứng đầu mật vụ Paris và là thám tử tư đầu tiên. '
                   'Victor Hugo xé đôi ông thành hai nhân vật kẻ thù của nhau trong Những người khốn khổ: Jean Valjean và Javert. '
                   'Một bản giao kèo với cảnh sát, một đội quân cựu tù, và cái giá của việc bị cả hai phía ruồng bỏ.',
        'more': [],
        'sources': SOURCES,
        'tags': ['vidocq', 'javert có thật', 'jean valjean', 'những người khốn khổ', 'victor hugo', 'thám tử đầu tiên', 'cảnh sát pháp', 'hồ sơ lịch sử', 'ngoài đời thật'],
        'hashtags': ['Vidocq', 'Javert', 'HoSo'],
        'category': '24', 'playlist': 'Ngoài Đời Thật',
        'chapter_titles': chapter_titles, 'video_credits': credits,
    })
    yt['publish_at'] = '2026-12-03T14:00:00Z'
    spec['approved'] = ''
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print('spec.json:', len(used_files), 'ảnh có ghi công,', len(SOURCES), 'nguồn')
