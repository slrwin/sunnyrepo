# -*- coding: utf-8 -*-
from datetime import datetime
from modules.kodi_utils import local_string as ls

years_movies = range(datetime.today().year, 1899, -1)

years_tvshows = range(datetime.today().year, 1941, -1)

decades_movies = [i for i in years_movies if not i % 10]

decades_tvshows = [i for i in years_tvshows if not i % 10] + ['1940']

oscar_winners = (
		(776503, 581734, 496243, 490132, 399055, 376867, 314365, 194662, 76203, 68734, 74643, 45269, 12162, 12405, 6977, 1422, 1640, 70, 122, 1574),
		(453, 98, 14, 1934, 597, 409, 197, 13, 424, 33, 274, 581, 403, 380, 746, 792, 606, 279, 11050, 783),
		(9443, 16619, 12102, 11778, 703, 1366, 510, 240, 9277, 238, 1051, 11202, 3116, 17917, 10633, 874, 15121, 11113, 5769, 947),
		(1725, 284, 665, 17281, 826, 2897, 15919, 654, 11426, 27191, 2769, 705, 25430, 23383, 33667, 887, 28580, 17661, 27367, 289),
		(43266, 223, 770, 34106, 43278, 43277, 12311, 3078, 56164, 33680, 42861, 143, 65203, 28966, 631)
	)

movie_certifications = (
		'G',
		'PG',
		'PG-13',
		'R',
		'NC-17',
		'NR'
	)

tvshow_certifications = (
		'tv-y',
		'tv-y7',
		'tv-g',
		'tv-pg',
		'tv-14',
		'tv-ma'
	)

languages = (
		(ls(32861), 'ar'), (ls(32862), 'bs'),   (ls(32863), 'bg'),   (ls(32864), 'zh'),   (ls(32865), 'hr'),   (ls(32866), 'nl'),   (ls(32867), 'en'),
		(ls(32868), 'fi'), (ls(32869), 'fr'),   (ls(32870), 'de'),   (ls(32871), 'el'),   (ls(32872), 'he'),   (ls(32873), 'hi'),   (ls(32874), 'hu'),
		(ls(32875), 'is'), (ls(32876), 'it'),   (ls(32877), 'ja'),   (ls(32878), 'ko'),   (ls(32879), 'mk'),   (ls(32880), 'no'),   (ls(32881), 'fa'),
		(ls(32882), 'pl'), (ls(32883), 'pt'),   (ls(32884), 'pa'),   (ls(32885), 'ro'),   (ls(32886), 'ru'),   (ls(32887), 'sr'),   (ls(32888), 'sl'),
		(ls(32889), 'es'), (ls(32890), 'sv'),   (ls(32891), 'tr'),   (ls(32892), 'uk')
	)
		

meta_languages = [
		{'iso': 'zh', 'name': 'Chinese'},          {'iso': 'hr', 'name': 'Croatian'},
		{'iso': 'cs', 'name': 'Czech'},            {'iso': 'da', 'name': 'Danish'},
		{'iso': 'nl', 'name': 'Dutch'},            {'iso': 'en', 'name': 'English'},
		{'iso': 'fi', 'name': 'Finnish'},          {'iso': 'fr', 'name': 'French'},
		{'iso': 'de', 'name': 'German'},           {'iso': 'el', 'name': 'Greek'},
		{'iso': 'he', 'name': 'Hebrew'},           {'iso': 'hu', 'name': 'Hungarian'},
		{'iso': 'it', 'name': 'Italian'},          {'iso': 'ja', 'name': 'Japanese'},
		{'iso': 'ko', 'name': 'Korean'},           {'iso': 'no', 'name': 'Norwegian'},
		{'iso': 'pl', 'name': 'Polish'},           {'iso': 'pt', 'name': 'Portuguese'},
		{'iso': 'ru', 'name': 'Russian'},          {'iso': 'sl', 'name': 'Slovenian'},
		{'iso': 'es', 'name': 'Spanish'},          {'iso': 'sv', 'name': 'Swedish'},
		{'iso': 'tr', 'name': 'Turkish'},          {'iso': 'ar-SA', 'name': 'Arabic Saudi Arabia'}
	]

regions = (
		{'code': 'AF', 'name': ls(32893)},   {'code': 'AL', 'name': ls(32894)},   {'code': 'DZ', 'name': ls(32895)},   {'code': 'AQ', 'name': ls(32896)},
		{'code': 'AR', 'name': ls(32897)},   {'code': 'AM', 'name': ls(32898)},   {'code': 'AU', 'name': ls(32899)},   {'code': 'AT', 'name': ls(32900)},
		{'code': 'BD', 'name': ls(32901)},   {'code': 'BY', 'name': ls(32902)},   {'code': 'BE', 'name': ls(32903)},   {'code': 'BR', 'name': ls(32904)},
		{'code': 'BG', 'name': ls(32905)},   {'code': 'KH', 'name': ls(32906)},   {'code': 'CA', 'name': ls(32907)},   {'code': 'CL', 'name': ls(32908)},
		{'code': 'CN', 'name': ls(32909)},   {'code': 'HR', 'name': ls(32910)},   {'code': 'CZ', 'name': ls(32911)},   {'code': 'DK', 'name': ls(32912)},
		{'code': 'EG', 'name': ls(32913)},   {'code': 'FI', 'name': ls(32914)},   {'code': 'FR', 'name': ls(32915)},   {'code': 'DE', 'name': ls(32916)},
		{'code': 'GR', 'name': ls(32917)},   {'code': 'HK', 'name': ls(32918)},   {'code': 'HU', 'name': ls(32919)},   {'code': 'IS', 'name': ls(32920)},
		{'code': 'IN', 'name': ls(32921)},   {'code': 'ID', 'name': ls(32922)},   {'code': 'IR', 'name': ls(32923)},   {'code': 'IQ', 'name': ls(32924)},
		{'code': 'IE', 'name': ls(32925)},   {'code': 'IL', 'name': ls(32926)},   {'code': 'IT', 'name': ls(32927)},   {'code': 'JP', 'name': ls(32928)},
		{'code': 'MY', 'name': ls(32929)},   {'code': 'NP', 'name': ls(32930)},   {'code': 'NL', 'name': ls(32931)},   {'code': 'NZ', 'name': ls(32932)},
		{'code': 'NO', 'name': ls(32933)},   {'code': 'PK', 'name': ls(32934)},   {'code': 'PY', 'name': ls(32935)},   {'code': 'PE', 'name': ls(32936)},
		{'code': 'PH', 'name': ls(32937)},   {'code': 'PL', 'name': ls(32938)},   {'code': 'PT', 'name': ls(32939)},   {'code': 'PR', 'name': ls(32940)},
		{'code': 'RO', 'name': ls(32941)},   {'code': 'RU', 'name': ls(32942)},   {'code': 'SA', 'name': ls(32943)},   {'code': 'RS', 'name': ls(32944)},
		{'code': 'SG', 'name': ls(32945)},   {'code': 'SK', 'name': ls(32946)},   {'code': 'SI', 'name': ls(32947)},   {'code': 'ZA', 'name': ls(32948)},
		{'code': 'ES', 'name': ls(32949)},   {'code': 'LK', 'name': ls(32950)},   {'code': 'SE', 'name': ls(32951)},   {'code': 'CH', 'name': ls(32952)},
		{'code': 'TH', 'name': ls(32953)},   {'code': 'TR', 'name': ls(32954)},   {'code': 'UA', 'name': ls(32955)},   {'code': 'AE', 'name': ls(32956)},
		{'code': 'GB', 'name': ls(32957)},   {'code': 'US', 'name': ls(32958)},   {'code': 'UY', 'name': ls(32959)},   {'code': 'VE', 'name': ls(32960)},
		{'code': 'VN', 'name': ls(32961)},   {'code': 'YE', 'name': ls(32962)},   {'code': 'ZW', 'name': ls(32963)}
	)

movie_genres = {
		ls(32548): ['28', 'genre_action'],                ls(32549): ['12', 'genre_adventure'],
		ls(32550): ['16', 'genre_animation'],             ls(32551): ['35', 'genre_comedy'],
		ls(32552): ['80', 'genre_crime'],                 ls(32553): ['99', 'genre_documentary'],
		ls(32554): ['18', 'genre_drama'],                 ls(32555): ['10751', 'genre_family'],
		ls(32558): ['14', 'genre_fantasy'],               ls(32559): ['36', 'genre_history'],
		ls(32560): ['27', 'genre_horror'],                ls(32561): ['10402', 'genre_music'],
		ls(32557): ['9648', 'genre_mystery'],             ls(32562): ['10749', 'genre_romance'],
		ls(32563): ['878', 'genre_scifi'],                ls(32564): ['10770', 'genre_soap'],
		ls(32565): ['53', 'genre_thriller'],              ls(32566): ['10752', 'genre_war'], 
		ls(32567): ['37', 'genre_western']
	}

tvshow_genres = {
		'%s & %s' % (ls(32548), ls(32549)): ['10759', 'genre_action'],         ls(32550): ['16', 'genre_animation'],
		ls(32551): ['35', 'genre_comedy'],                                     ls(32552): ['80', 'genre_crime'],
		ls(32553): ['99', 'genre_documentary'],                                ls(32554): ['18', 'genre_drama'],
		ls(32555): ['10751', 'genre_family'],                                  ls(32556): ['10762', 'genre_kids'],
		ls(32557): ['9648', 'genre_mystery'],                                  ls(32568):['10763', 'genre_news'],
		ls(32569): ['10764', 'genre_reality'],                                 ls(33057): ['10765', 'genre_scifi'],
		ls(32570): ['10766', 'genre_soap'],                                    ls(32570): ['10767', 'genre_talk'],
		ls(32572): ['10768', 'genre_war'],                                     ls(32567): ['37', 'genre_western']
	}

networks = (
		{'id':54,'name':'Disney Channel','logo': 'network_disney'},                   {'id':44,'name':'Disney XD','logo': 'network_disneyxd'},
		{'id':2,'name':'ABC','logo': 'network_abc'},                                  {'id':493,'name':'BBC America','logo': 'network_bbcamerica'},
		{'id':6,'name':'NBC','logo': 'network_nbc'},                                  {'id':13,'name':'Nickelodeon','logo': 'network_nickelodeon'},
		{'id':14,'name':'PBS','logo': 'network_pbs'},                                 {'id':16,'name':'CBS','logo': 'network_cbs'},
		{'id':19,'name':'FOX','logo': 'network_fox'},                                 {'id':21,'name':'The WB','logo': 'network_thewb'},
		{'id':24,'name':'BET','logo': 'network_bet'},                                 {'id':30,'name':'USA Network','logo': 'network_usanetwork'},
		{'id':32,'name':'CBC','logo': 'network_cbc'},                                 {'id':173,'name':'AT-X','logo': 'network_atx'},
		{'id':33,'name':'MTV','logo': 'network_mtv'},                                 {'id':34,'name':'Lifetime','logo': 'network_lifetime'},
		{'id':35,'name':'Nick Junior','logo': 'network_nickjr'},                      {'id':41,'name':'TNT','logo': 'network_tnt'},
		{'id':43,'name':'National Geographic','logo': 'network_natgeo'},              {'id':47,'name':'Comedy Central','logo': 'network_comedycentral'},
		{'id':49,'name':'HBO','logo': 'network_hbo'},                                 {'id':55,'name':'Spike','logo': 'network_spike'},
		{'id':67,'name':'Showtime','logo': 'network_showtime'},                       {'id':56,'name':'Cartoon Network','logo': 'network_cartoonnetwork'},
		{'id':65,'name':'History Channel','logo': 'network_history'},                 {'id':84,'name':'TLC','logo': 'network_tlc'},
		{'id':68,'name':'TBS','logo': 'network_tbs'},                                 {'id':71,'name':'The CW','logo': 'network_thecw'},
		{'id':74,'name':'Bravo','logo': 'network_bravo'},                             {'id':76,'name':'E!','logo': 'network_e'},
		{'id':77,'name':'Syfy','logo': 'network_syfy'},                               {'id':80,'name':'Adult Swim','logo': 'network_adultswim'},
		{'id':91,'name':'Animal Planet','logo': 'network_animalplanet'},              {'id':110,'name':'CTV','logo': 'network_ctv'},
		{'id':129,'name':'A&E','logo': 'network_ane'},                                {'id':158,'name':'VH1','logo': 'network_vh1'},
		{'id':174,'name':'AMC','logo': 'network_amc'},                                {'id':928,'name':'Crackle','logo': 'network_crackle'},
		{'id':202,'name':'WGN America','logo': 'network_wgnamerica'},                 {'id':209,'name':'Travel Channel','logo': 'network_travel'},
		{'id':213, 'name':'Netflix','logo': 'network_netflix'},                       {'id':251,'name':'Audience','logo': 'network_audience'},
		{'id':270,'name':'SundanceTV','logo': 'network_sundancetv'},                  {'id':318,'name':'Starz','logo': 'network_starz'},
		{'id':359,'name':'Cinemax','logo': 'network_cinemax'},                        {'id':364,'name':'truTV','logo': 'network_trutv'},
		{'id':384,'name':'Hallmark Channel','logo': 'network_hallmark'},              {'id':397,'name':'TV Land','logo': 'network_tvland'},
		{'id':1024,'name':'Amazon','logo': 'network_amazon'},                         {'id':1267,'name':'Freeform','logo': 'network_freeform'},
		{'id':4,'name':'BBC 1','logo': 'network_bbc1'},                               {'id':332,'name':'BBC 2','logo': 'network_bbc2'},
		{'id':3,'name':'BBC 3','logo': 'network_bbc3'},                               {'id':100,'name':'BBC 4','logo': 'network_bbc4'},
		{'id':214,'name':'Sky 1','logo': 'network_sky1'},                             {'id':9,'name':'ITV','logo': 'network_itv'},
		{'id':26,'name':'Channel 4','logo': 'network_channel4'},                      {'id':99,'name':'Channel 5','logo': 'network_channel5'},
		{'id':136,'name':'E4','logo': 'network_e4'},                                  {'id':210,'name':'HGTV','logo': 'network_hgtv'},
		{'id':453,'name':'Hulu','logo': 'network_hulu'},                              {'id':1436,'name':'YouTube Red','logo': 'network_youtubered'},
		{'id':64,'name':'Discovery Channel','logo': 'network_discovery'},             {'id':2739,'name':'Disney+','logo': 'network_disneyplus'},
		{'id':2552,'name':'Apple TV +','logo': 'network_appletvplus'},                {'id':2697,'name':'Acorn TV','logo': 'network_acorntv'},
		{'id':1709,'name':'CBS All Access','logo': 'network_cbsallaccess'},           {'id':3186,'name':'HBO Max','logo': 'network_hbomax'},
		{'id':2243,'name':'DC Universe','logo': 'network_dcuniverse'},                {'id':2076,'name':'Paramount Network','logo': 'network_paramount'},
		{'id':4330,'name':'Paramount+','logo': 'network_paramountplus'},              {'id': 3353, 'name': 'Peacock', 'logo': 'network_peacock'},
		{'id':4353,'name':'Discovery+','logo': 'network_discoveryplus'}
	)

language_choices =  {
		'None': None,              'Afrikaans': 'afr',            'Albanian': 'alb',             'Arabic': 'ara',
		'Armenian': 'arm',         'Basque': 'baq',               'Bengali': 'ben',              'Bosnian': 'bos',
		'Breton': 'bre',           'Bulgarian': 'bul',            'Burmese': 'bur',              'Catalan': 'cat',
		'Chinese': 'chi',          'Croatian': 'hrv',             'Czech': 'cze',                'Danish': 'dan',
		'Dutch': 'dut',            'English': 'eng',              'Esperanto': 'epo',            'Estonian': 'est',
		'Finnish': 'fin',          'French': 'fre',               'Galician': 'glg',             'Georgian': 'geo',
		'German': 'ger',           'Greek': 'ell',                'Hebrew': 'heb',               'Hindi': 'hin',
		'Hungarian': 'hun',        'Icelandic': 'ice',            'Indonesian': 'ind',           'Italian': 'ita',
		'Japanese': 'jpn',         'Kazakh': 'kaz',               'Khmer': 'khm',                'Korean': 'kor',
		'Latvian': 'lav',          'Lithuanian': 'lit',           'Luxembourgish': 'ltz',        'Macedonian': 'mac',
		'Malay': 'may',            'Malayalam': 'mal',            'Manipuri': 'mni',             'Mongolian': 'mon',
		'Montenegrin': 'mne',      'Norwegian': 'nor',            'Occitan': 'oci',              'Persian': 'per',
		'Polish': 'pol',           'Portuguese': 'por',           'Portuguese(Brazil)': 'pob',   'Romanian': 'rum',
		'Russian': 'rus',          'Serbian': 'scc',              'Sinhalese': 'sin',            'Slovak': 'slo',
		'Slovenian': 'slv',        'Spanish': 'spa',              'Swahili': 'swa',              'Swedish': 'swe',
		'Syriac': 'syr',           'Tagalog': 'tgl',              'Tamil': 'tam',                'Telugu': 'tel',
		'Thai': 'tha',             'Turkish': 'tur',              'Ukrainian': 'ukr',            'Urdu': 'urd',
		'Vietnamese': 'vie'
	}

colors = [
		'FFFFFFE3', 'FFFFFAE6', 'FFFEF5E6', 'FFFEF0E5', 'FFFEEBE5', 'FFFFEFEF', 'FFFFE6EA', 'FFFFE6F1', 'FFFEE6F4', 'FFFFE6FB', 'FFFEE6FE', 'FFFAE6FF', 'FFF4E6FF',
		'FFF0E6FF', 'FFEAE7FC', 'FFE6E7FC', 'FFE6EBFF', 'FFE7F0FF', 'FFE7F5FF', 'FFE7FAFF', 'FFE6FFFF', 'FFE6FFFB', 'FFE7FEF4', 'FFE7FFF1', 'FFE6FFEA', 'FFE7FFE7',
		'FFEBFFF3', 'FFF1FFE6', 'FFF5FFE6', 'FFFBFFE6', 'FFFFFFFF', 'FFFFFFCB', 'FFFEFACA', 'FFFFEACB', 'FFFFE0CC', 'FFFED6CC', 'FFFFCACD', 'FFFFCCD5', 'FFFFCDE0',
		'FFFFCCEB', 'FFFFCBF5', 'FFFECCFD', 'FFF6CBFF', 'FFECCCFE', 'FFE0CCFF', 'FFD6CCFE', 'FFCCCCFE', 'FFCDD6FF', 'FFCAE1FF', 'FFCCEBFF', 'FFCEF4FD', 'FFCAFFFF',
		'FFCCFFF6', 'FFCBFEEB', 'FFCCFFE0', 'FFCCFFD6', 'FFCDFFCC', 'FFD7FFCB', 'FFE1FFCD', 'FFEBFFCC', 'FFF5FFCB', 'FFEFEFEF', 'FFFEFFB3', 'FFFFF1B2', 'FFFFE0B2',
		'FFFDD2B2', 'FFFFC2B3', 'FFFFB3B3', 'FFFFB2C2', 'FFFFB3D1', 'FFFFB3E1', 'FFFFB2F4', 'FFFFB3FE', 'FFF0B3FF', 'FFE1B2FF', 'FFD2B3FF', 'FFC1B3FE', 'FFB4B3FF',
		'FFB3C1FE', 'FFB2D1FF', 'FFB3E0FF', 'FFB2F0FF', 'FFB3FFFF', 'FFB3FFF0', 'FFB4FFE0', 'FFB3FFD1', 'FFB4FEC3', 'FFB3FFB4', 'FFC2FFB2', 'FFD1FFB4', 'FFE0FFB3',
		'FFF1FFB4', 'FFE0E0E0', 'FFFEFF99', 'FFFFEB9A', 'FFFED699', 'FFFFC299', 'FFFFAD98', 'FFFF9899', 'FFFF99AE', 'FFFF99C1', 'FFFE99D5', 'FFFF99EC', 'FFFF99FF',
		'FFEB99FF', 'FFD699FF', 'FFC299FF', 'FFAE99FF', 'FF9A99FF', 'FF98ADFE', 'FF9AC2FF', 'FF98D6FF', 'FF99EBFF', 'FF99FFFF', 'FF99FFEA', 'FF99FFD7', 'FF9AFFC3',
		'FF99FFAC', 'FF99FF99', 'FFADFF99', 'FFC2FF98', 'FFD6FF99', 'FFEAFF98', 'FFD0D0D0', 'FFFFFF80', 'FFFFE681', 'FFFFCC80', 'FFFFB381', 'FFFF9980', 'FFFE8081',
		'FFFF8199', 'FFFF80B3', 'FFFF80CD', 'FFFF80E7', 'FFFC81FE', 'FFE680FF', 'FFCC7FFF', 'FFB380FF', 'FF9980FF', 'FF807FFE', 'FF8099FE', 'FF7FB3FF', 'FF80CCFE',
		'FF80E6FF', 'FF7FFFFE', 'FF7FFEE0', 'FF80FFCC', 'FF80FFB2', 'FF80FF98', 'FF81FF81', 'FF99FF80', 'FFB3FF80', 'FFCCFF80', 'FFE6FF80', 'FFC0C0C0', 'FFFFFF6B',
		'FFFEE066', 'FFFFC267', 'FFFFA366', 'FFFF8566', 'FFFF6766', 'FFFF6685', 'FFFF66A4', 'FFFF66C1', 'FFFF66E0', 'FFFF66FF', 'FFE166FF', 'FFC366FF', 'FFA366FF',
		'FF8566FF', 'FF6665FE', 'FF6785FF', 'FF66A3FE', 'FF65C2FF', 'FF65E0FF', 'FF65FFFF', 'FF66FFE0', 'FF65FFC1', 'FF66FFA4', 'FF65FF85', 'FF66FF66', 'FF84FF66',
		'FFA2FF66', 'FFC2FF66', 'FFE0FF66', 'FFAFAFAF', 'FFFFFF4D', 'FFFFDB4E', 'FFFFB84E', 'FFFF944C', 'FFFF714D', 'FFFF4D4D', 'FFFF4D6F', 'FFFE4D93', 'FFFE4DB7',
		'FFFE4DDB', 'FFFF4DFF', 'FFDC4DFF', 'FFB84DFF', 'FF944EFF', 'FF704DFF', 'FF4D4CFF', 'FF4D70FE', 'FF4D94FE', 'FF4DB8FF', 'FF4DDBFF', 'FF4DFFFF', 'FF4DFFDB',
		'FF4EFFB9', 'FF4EFF95', 'FF4DFE70', 'FF4CFF4C', 'FF70FF4D', 'FF94FF4D', 'FFB8FE4D', 'FFDAFF4D', 'FF8C8C8C', 'FFFFFF33', 'FFFFD634', 'FFFFAD33', 'FFFF8532',
		'FFFF5C33', 'FFFF3334', 'FFFF335C', 'FFFF3287', 'FFFF33AE', 'FFFF33D6', 'FFFE33FF', 'FFD633FE', 'FFAD34FF', 'FF8534FF', 'FF5D33FF', 'FF3233FF', 'FF325CFE',
		'FF3285FF', 'FF33ADFF', 'FF33D6FF', 'FF33FFFE', 'FF32FFD6', 'FF34FFAD', 'FF33FF84', 'FF32FF5C', 'FF34FF33', 'FF5CFF34', 'FF85FE33', 'FFADFE33', 'FFD5FF33',
		'FF7C7C7C', 'FFFFFF19', 'FFFFD119', 'FFFFA418', 'FFFF751A', 'FFFF4719', 'FFFF1919', 'FFFF1947', 'FFFF1874', 'FFFF19A3', 'FFFF19D1', 'FFFF19FF', 'FFD019FF',
		'FFA219FF', 'FF751AFE', 'FF4719FF', 'FF1819FF', 'FF1947FF', 'FF1974FF', 'FF19A3FE', 'FF18D1FF', 'FF19FFFF', 'FF19FFD1', 'FF19FFA4', 'FF18FF75', 'FF19FF47',
		'FF19FF19', 'FF48FF19', 'FF76FF19', 'FFA3FE1A', 'FFD1FF19', 'FF6B6B6B', 'FFFFFF00', 'FFFFCC00', 'FFFE9900', 'FFFF6600', 'FFFF3300', 'FFFE0000', 'FFFE0032',
		'FFFF0066', 'FFFF0198', 'FFFF00CC', 'FFFF00FE', 'FFCC00FF', 'FF9A00FF', 'FF6601FF', 'FF3300FF', 'FF0000FE', 'FF0033FF', 'FF0166FF', 'FF0097FE', 'FF00CCFF',
		'FF00FFFF', 'FF01FFCD', 'FF00FF99', 'FF00FE67', 'FF00FF33', 'FF00FF01', 'FF33FF00', 'FF65FF00', 'FF99FE00', 'FFCCFF00', 'FF5D5D5D', 'FFE8E500', 'FFE6B800',
		'FFE68B00', 'FFE65C01', 'FFE72E00', 'FFE60000', 'FFE6002E', 'FFE6005B', 'FFE80183', 'FFE600B8', 'FFE600E6', 'FFB700E6', 'FF8900E6', 'FF5C01E5', 'FF2E00E6',
		'FF0000E6', 'FF012EE1', 'FF005BE7', 'FF008AE5', 'FF00B8E6', 'FF00E6E6', 'FF00E6B7', 'FF00E78B', 'FF00E65F', 'FF00E532', 'FF00E600', 'FF2FE600', 'FF5DE600',
		'FF8AE501', 'FFB8E600', 'FF4F4F4F', 'FFCDCC00', 'FFCDA301', 'FFCA7B02', 'FFCC5200', 'FFCC2900', 'FFCC0001', 'FFCD0029', 'FFCE0052', 'FFCC007B', 'FFCD00A3',
		'FFCB00CC', 'FFA300CB', 'FF7A01CC', 'FF5201CC', 'FF2A00D0', 'FF0000CC', 'FF0029CB', 'FF0052CC', 'FF007ACD', 'FF00A3CC', 'FF00CCCB', 'FF00CCA3', 'FF01CC7A',
		'FF03CB51', 'FF00CC29', 'FF01CC00', 'FF29CC01', 'FF52CB00', 'FF7ACB00', 'FFA2CC00', 'FF434343', 'FFB4B300', 'FFB38E00', 'FFB36B00', 'FFB34700', 'FFB32501',
		'FFB30101', 'FFB40025', 'FFB40047', 'FFB4006B', 'FFB5008B', 'FFB300B3', 'FF8F00B2', 'FF6B00B2', 'FF4700B4', 'FF2300B2', 'FF0000B2', 'FF0025B4', 'FF0047B3',
		'FF006BB3', 'FF008EB2', 'FF00B3B2', 'FF00B38E', 'FF00B36C', 'FF00B346', 'FF00B324', 'FF00B300', 'FF24B301', 'FF47B200', 'FF6CB201', 'FF90B301', 'FF373737',
		'FF999A00', 'FF987A00', 'FF995C01', 'FF9A3D00', 'FF9A1F00', 'FF990100', 'FF99001F', 'FF9A003E', 'FF99005B', 'FF9A007A', 'FF990099', 'FF7B0099', 'FF5D0099',
		'FF3D0099', 'FF1F0099', 'FF000098', 'FF011F99', 'FF003D98', 'FF005C99', 'FF007A99', 'FF009999', 'FF00997A', 'FF00995B', 'FF00993E', 'FF00991F', 'FF009900',
		'FF1E9900', 'FF3C9900', 'FF5C9900', 'FF7A9900', 'FF2E2E2E', 'FF7F8000', 'FF7F6601', 'FF804C00', 'FF803201', 'FF801A01', 'FF800000', 'FF800019', 'FF800033',
		'FF80004B', 'FF810065', 'FF81007F', 'FF660080', 'FF4C007F', 'FF33007F', 'FF1A0080', 'FF010080', 'FF011A7F', 'FF003480', 'FF004C80', 'FF00667F', 'FF008081',
		'FF008067', 'FF037F4B', 'FF008033', 'FF00801B', 'FF008001', 'FF1A8000', 'FF338000', 'FF4C8001', 'FF668100', 'FF242424', 'FF656600', 'FF675201', 'FF653D00',
		'FF672900', 'FF661400', 'FF660000', 'FF660015', 'FF660028', 'FF65003C', 'FF660053', 'FF660066', 'FF550069', 'FF3D0067', 'FF290066', 'FF150067', 'FF010066',
		'FF001465', 'FF012966', 'FF003D66', 'FF005267', 'FF006766', 'FF006651', 'FF00663E', 'FF01662A', 'FF006613', 'FF006600', 'FF146600', 'FF296600', 'FF3D6600',
		'FF516600', 'FF181818', 'FF4B4C00', 'FF4C3E01', 'FF4D2E00', 'FF4C1F00', 'FF4D0F00', 'FF4C0000', 'FF4C000F', 'FF4B001F', 'FF4C002E', 'FF4C003E', 'FF4C004B',
		'FF3D004D', 'FF2E004B', 'FF1F004C', 'FF0E004B', 'FF01004C', 'FF000E4B', 'FF001F4D', 'FF012E4D', 'FF003D4C', 'FF004C4C', 'FF004D3D', 'FF004C2E', 'FF004C1E',
		'FF004C0E', 'FF004C01', 'FF0F4C00', 'FF204C01', 'FF2D4C00', 'FF3E4C01', 'FF000000'
	]

media_lists = (
		"'tmdb_movies%'",
		"'tmdb_tv%'",
		"'tmdb_popular_people%'",
		"'tmdb_images_person%'",
		"'tmdb_media%'",
		"'tmdb_company%'",
		"'trakt_movies%'",
		"'trakt_tv%'",
		"'trakt_trending_user_lists%'",
		"'trakt_popular_user_lists%'",
		"'imdb_%'",
		"'tmdb_people%'",
		"'imdb_keyword%'",
		"'imdb_blunders%'",
		"'fen_discover%'",
		"'fen_FURK_T_FILE%'",
		"'fen_pm_instant_transfer%'",
		"'fen_rd_check_hash%'",
		"'FEN_AD_%'",
		"'FEN_RD_%'",
		"'FEN_FOLDER_%'",
		"'https%'"
	)