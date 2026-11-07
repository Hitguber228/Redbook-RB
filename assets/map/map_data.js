// Данные Красной книги Беларуси для интерактивной карты
const REDBOOK_SPECIES = [
  {
    "id": "bison-bonasus",
    "name_ru": "Европейский зубр",
    "name_be": "Еўрапейскі зубр",
    "name_lat": "Bison bonasus",
    "category": "II",
    "kingdom": "animals",
    "taxon_group": "mammals",
    "image_url": "/images/species/bison-bonasus.jpg",
    "habitat": "Широколиственные и смешанные равнинные леса с развитым подлеском, пойменные луга и лесные поляны.",
    "coordinates": [
      [
        52.5724,
        23.8016
      ],
      [
        53.985,
        26.354
      ],
      [
        52.0512,
        28.0245
      ]
    ]
  },
  {
    "id": "ciconia-nigra",
    "name_ru": "Чёрный аист",
    "name_be": "Чорны бусел",
    "name_lat": "Ciconia nigra",
    "category": "III",
    "kingdom": "animals",
    "taxon_group": "birds",
    "image_url": "/images/species/ciconia-nigra.jpg",
    "habitat": "Старовозрастные глухие широколиственные и смешанные леса, глухие ольсы, примыкающие к верховым и переходным болотам.",
    "coordinates": [
      [
        52.021,
        27.81
      ],
      [
        54.712,
        28.32
      ],
      [
        52.61,
        23.95
      ]
    ]
  },
  {
    "id": "acrocephalus-paludicola",
    "name_ru": "Вертлявая камышевка",
    "name_be": "Вяртлявая чаротаўка",
    "name_lat": "Acrocephalus paludicola",
    "category": "I",
    "kingdom": "animals",
    "taxon_group": "birds",
    "image_url": "/images/species/acrocephalus-paludicola.jpg",
    "habitat": "Открытые осоковые низинные болота с умеренным уровнем грунтовых вод и низкой растительностью.",
    "coordinates": [
      [
        52.4167,
        25.1667
      ],
      [
        52.05,
        24.8333
      ]
    ]
  },
  {
    "id": "lynx-lynx",
    "name_ru": "Европейская рысь",
    "name_be": "Еўрапейская рысь",
    "name_lat": "Lynx lynx",
    "category": "II",
    "kingdom": "animals",
    "taxon_group": "mammals",
    "image_url": "/images/species/lynx-lynx.jpg",
    "habitat": "Глухие спелые высокоствольные леса с буреломом и густым подлеском, окраины лесных болот.",
    "coordinates": [
      [
        54.73,
        28.35
      ],
      [
        52.65,
        23.85
      ],
      [
        54.91,
        26.7
      ]
    ]
  },
  {
    "id": "ursus-arctos",
    "name_ru": "Бурый медведь",
    "name_be": "Буры мядзведзь",
    "name_lat": "Ursus arctos",
    "category": "II",
    "kingdom": "animals",
    "taxon_group": "mammals",
    "image_url": "/images/species/ursus-arctos.jpg",
    "habitat": "Крупные сплошные лесные массивы с глухими буреломами, моховыми болотами и обилием ягодников (черника, брусника, клюква).",
    "coordinates": [
      [
        54.75,
        28.33
      ],
      [
        55.2,
        29.4
      ]
    ]
  },
  {
    "id": "meles-meles",
    "name_ru": "Обыкновенный барсук",
    "name_be": "Барсук",
    "name_lat": "Meles meles",
    "category": "III",
    "kingdom": "animals",
    "taxon_group": "mammals",
    "image_url": "/images/species/meles-meles.jpg",
    "habitat": "Холмистые участки смешанных и широколиственных лесов вблизи воды с супесчаными почвами для рытья нор.",
    "coordinates": [
      [
        54.68,
        28.25
      ],
      [
        52.55,
        23.9
      ]
    ]
  },
  {
    "id": "spermophilus-suslicus",
    "name_ru": "Крапчатый суслик",
    "name_be": "Крапчаты хоўлік",
    "name_lat": "Spermophilus suslicus",
    "category": "I",
    "kingdom": "animals",
    "taxon_group": "mammals",
    "image_url": "/images/species/spermophilus-suslicus.jpg",
    "habitat": "Суходольные ненарушенные луга, пастбища и остепненные склоны холмов на карбонатных почвах.",
    "coordinates": [
      [
        53.22,
        26.68
      ],
      [
        53.15,
        27.05
      ]
    ]
  },
  {
    "id": "strix-nebulosa",
    "name_ru": "Бородатая неясыть",
    "name_be": "Барадатая Baykasa",
    "name_lat": "Strix nebulosa",
    "category": "II",
    "kingdom": "animals",
    "taxon_group": "birds",
    "image_url": "/images/species/strix-nebulosa.jpg",
    "habitat": "Старые сырые хвойные и смешанные леса вблизи верховых и переходных болот.",
    "coordinates": [
      [
        52.65,
        25.75
      ],
      [
        55.85,
        28.5
      ]
    ]
  },
  {
    "id": "haliaeetus-albicilla",
    "name_ru": "Орлан-белохвост",
    "name_be": "Арлан-белахвост",
    "name_lat": "Haliaeetus albicilla",
    "category": "II",
    "kingdom": "animals",
    "taxon_group": "birds",
    "image_url": "/images/species/haliaeetus-albicilla.jpg",
    "habitat": "Высокоствольные леса вблизи крупных водоемов, рыбхозов и пойм рек (Припять, Днепр).",
    "coordinates": [
      [
        52.1,
        28.1
      ],
      [
        55.7,
        27.2
      ]
    ]
  },
  {
    "id": "acipenser-ruthenus",
    "name_ru": "Стерлядь",
    "name_be": "Сцерлядзь",
    "name_lat": "Acipenser ruthenus",
    "category": "II",
    "kingdom": "animals",
    "taxon_group": "fish",
    "image_url": "/images/species/acipenser-ruthenus.jpg",
    "habitat": "Глубокие участки рек с быстрым течением, галечным или каменистым дном (бассейны рек Днепр, Припять, Сож).",
    "coordinates": [
      [
        52.4,
        31.0
      ],
      [
        52.12,
        28.25
      ]
    ]
  },
  {
    "id": "epidalea-calamita",
    "name_ru": "Камышовая жаба",
    "name_be": "Камышовая рапуха",
    "name_lat": "Epidalea calamita",
    "category": "III",
    "kingdom": "animals",
    "taxon_group": "amphibians",
    "image_url": "/images/species/epidalea-calamita.jpg",
    "habitat": "Песчаные карьеры, дюны, сосновые посадки на песках, сухие луга вблизи неглубоких временных водоемов.",
    "coordinates": [
      [
        52.2,
        24.3
      ],
      [
        53.4,
        24.1
      ]
    ]
  },
  {
    "id": "emys-orbicularis",
    "name_ru": "Европейская болотная черепаха",
    "name_be": "Балотная чарапаха",
    "name_lat": "Emys orbicularis",
    "category": "III",
    "kingdom": "animals",
    "taxon_group": "reptiles",
    "image_url": "/images/species/emys-orbicularis.jpg",
    "habitat": "Старицы рек, лесные пруды, мелиоративные каналы с медленным течением и илистым дном в бассейне Припяти и Сожа.",
    "coordinates": [
      [
        51.98,
        27.65
      ],
      [
        51.85,
        26.2
      ]
    ]
  },
  {
    "id": "coronella-austriaca",
    "name_ru": "Обыкновенная медянка",
    "name_be": "Мядзянка",
    "name_lat": "Coronella austriaca",
    "category": "III",
    "kingdom": "animals",
    "taxon_group": "reptiles",
    "image_url": "/images/species/coronella-austriaca.jpg",
    "habitat": "Сухие прогреваемые опушки сосновых боров, вырубки, заросшие вереском поляны.",
    "coordinates": [
      [
        52.45,
        24.1
      ],
      [
        52.1,
        28.3
      ]
    ]
  },
  {
    "id": "cypripedium-calceolus",
    "name_ru": "Венерин башмачок настоящий",
    "name_be": "Венерын чаравічак сапраўдны",
    "name_lat": "Cypripedium calceolus",
    "category": "III",
    "kingdom": "plants",
    "taxon_group": "vascular_plants",
    "image_url": "/images/species/cypripedium-calceolus.jpg",
    "habitat": "Разреженные широколиственные, смешанные и сосновые леса на карбонатных почвах, лесные опушки и поляны.",
    "coordinates": [
      [
        55.63,
        27.05
      ],
      [
        54.85,
        26.85
      ],
      [
        52.6,
        23.82
      ]
    ]
  },
  {
    "id": "allium-ursinum",
    "name_ru": "Черемша (Лук медвежий)",
    "name_be": "Чарамша (Цыбуля мядзведжая)",
    "name_lat": "Allium ursinum",
    "category": "III",
    "kingdom": "plants",
    "taxon_group": "vascular_plants",
    "image_url": "/images/species/allium-ursinum.jpg",
    "habitat": "Тенистые широколиственные леса (дубравы, грабняки), ольшаники в долинах лесных ручьев на богатых влажных почвах.",
    "coordinates": [
      [
        52.58,
        23.85
      ],
      [
        53.8,
        27.2
      ]
    ]
  },
  {
    "id": "sparassis-crispa",
    "name_ru": "Спарассис курчавый (грибная капуста)",
    "name_be": "Спарасіс кучаравы",
    "name_lat": "Sparassis crispa",
    "category": "III",
    "kingdom": "fungi",
    "taxon_group": "fungi",
    "image_url": "/images/species/sparassis-crispa.jpg",
    "habitat": "Старые сосновые и смешанные сосново-широколиственные леса, у основания стволов и на пнях старых сосен.",
    "coordinates": [
      [
        52.68,
        23.9
      ],
      [
        54.89,
        26.92
      ]
    ]
  },
  {
    "id": "sarcosoma-globosum",
    "name_ru": "Саркосома шаровидная",
    "name_be": "Саркасома шарападобная",
    "name_lat": "Sarcosoma globosum",
    "category": "I",
    "kingdom": "fungi",
    "taxon_group": "fungi",
    "image_url": "/images/species/sarcosoma-globosum.jpg",
    "habitat": "Старовозрастные замшелые еловые леса зеленомошной группы, не тронутые рубками не менее 80–100 лет.",
    "coordinates": [
      [
        54.65,
        28.2
      ],
      [
        53.95,
        26.4
      ]
    ]
  },
  {
    "id": "lucanus-cervus",
    "name_ru": "Жук-олень",
    "name_be": "Жук-алень",
    "name_lat": "Lucanus cervus",
    "category": "II",
    "kingdom": "animals",
    "taxon_group": "insects",
    "image_url": "/images/species/lucanus-cervus.jpg",
    "habitat": "Старые пойменные дубравы юга Беларуси (Полесье), реже старые парки с вековыми дубами.",
    "coordinates": [
      [
        52.12,
        28.15
      ],
      [
        51.92,
        27.8
      ]
    ]
  },
  {
    "id": "pulsatilla-patens",
    "name_ru": "Прострел раскрытый (Сон-трава)",
    "name_be": "Сон-трава раскрытая",
    "name_lat": "Pulsatilla patens",
    "category": "IV",
    "kingdom": "plants",
    "taxon_group": "vascular_plants",
    "image_url": "/images/species/pulsatilla-patens.jpg",
    "habitat": "Сухие сосновые боры-беломошники, верещатники, песчаные террасы рек.",
    "coordinates": [
      [
        53.85,
        27.45
      ],
      [
        54.8,
        26.9
      ]
    ]
  }
];

const NATIONAL_PARKS = [
  {
    "id": "belovezhskaya-pushcha",
    "name_ru": "Национальный парк «Беловежская пуща»",
    "name_be": "Нацыянальны парк «Белавежская пушча»",
    "type": "park",
    "center": [
      52.5724,
      23.8016
    ],
    "polygon": [
      [
        52.48,
        23.7
      ],
      [
        52.55,
        23.62
      ],
      [
        52.75,
        23.65
      ],
      [
        52.88,
        23.95
      ],
      [
        52.82,
        24.28
      ],
      [
        52.62,
        24.22
      ],
      [
        52.48,
        23.88
      ],
      [
        52.48,
        23.7
      ]
    ],
    "area_sq_km": 1500,
    "established_year": 1991,
    "description_ru": "Старейший реликтовый лес Европы, объект Всемирного наследия ЮНЕСКО. Главный символ и оплот популяции европейского зубра.",
    "key_species": [
      "Европейский зубр",
      "Европейская рысь",
      "Черный аист",
      "Венерин башмачок"
    ]
  },
  {
    "id": "berezinsky-reserve",
    "name_ru": "Березинский биосферный заповедник",
    "name_be": "Бярэзінскі біясферны запаведнік",
    "type": "reserve",
    "center": [
      54.73,
      28.35
    ],
    "polygon": [
      [
        54.58,
        28.2
      ],
      [
        54.75,
        28.12
      ],
      [
        54.98,
        28.26
      ],
      [
        54.92,
        28.58
      ],
      [
        54.65,
        28.52
      ],
      [
        54.58,
        28.2
      ]
    ],
    "area_sq_km": 851,
    "established_year": 1925,
    "description_ru": "Единственная территория в Европе, где сосуществует европейская «Большая пятерка» млекопитающих: зубр, медведь, рысь, волк и лось.",
    "key_species": [
      "Бурый медведь",
      "Европейская рысь",
      "Европейский зубр",
      "Барсук"
    ]
  },
  {
    "id": "pripyatsky",
    "name_ru": "Национальный парк «Припятский»",
    "name_be": "Нацыянальны парк «Прыпяцкі»",
    "type": "park",
    "center": [
      52.0512,
      28.0245
    ],
    "polygon": [
      [
        52.02,
        27.65
      ],
      [
        52.2,
        27.72
      ],
      [
        52.25,
        28.32
      ],
      [
        52.02,
        28.48
      ],
      [
        51.9,
        28.02
      ],
      [
        52.02,
        27.65
      ]
    ],
    "area_sq_km": 880,
    "established_year": 1996,
    "description_ru": "«Белорусская Амазония» в пойме реки Припять: пойменные дубравы, протоки и царство редких водно-болотных птиц.",
    "key_species": [
      "Европейская болотная черепаха",
      "Жук-олень",
      "Черный аист",
      "Стерлядь"
    ]
  },
  {
    "id": "narochansky",
    "name_ru": "Национальный парк «Нарочанский»",
    "name_be": "Нацыянальны парк «Нарачанскі»",
    "type": "park",
    "center": [
      54.89,
      26.85
    ],
    "polygon": [
      [
        54.76,
        26.65
      ],
      [
        54.92,
        26.58
      ],
      [
        55.06,
        26.72
      ],
      [
        55.04,
        27.12
      ],
      [
        54.82,
        27.18
      ],
      [
        54.76,
        26.65
      ]
    ],
    "area_sq_km": 970,
    "established_year": 1999,
    "description_ru": "Крупнейшее озеро Беларуси Нарочь, ледниковые ландшафты, сосновые боры и популяции редких орхидей.",
    "key_species": [
      "Венерин башмачок",
      "Спарассис курчавый",
      "Сон-трава"
    ]
  },
  {
    "id": "braslav-lakes",
    "name_ru": "Национальный парк «Браславские озера»",
    "name_be": "Нацыянальны парк «Браслаўскія азёры»",
    "type": "park",
    "center": [
      55.63,
      27.05
    ],
    "polygon": [
      [
        55.52,
        26.92
      ],
      [
        55.66,
        26.82
      ],
      [
        55.8,
        26.92
      ],
      [
        55.82,
        27.26
      ],
      [
        55.58,
        27.22
      ],
      [
        55.52,
        26.92
      ]
    ],
    "area_sq_km": 700,
    "established_year": 1995,
    "description_ru": "Живописнейший каскад озер ледникового происхождения с островными экосистемами и гнездовьями редких водоплавающих птиц.",
    "key_species": [
      "Чернозобая гагара",
      "Орлан-белохвост",
      "Скопа"
    ]
  },
  {
    "id": "sporovsky",
    "name_ru": "Заказник «Споровский»",
    "name_be": "Заказнік «Спораўскі»",
    "type": "reserve",
    "center": [
      52.4167,
      25.1667
    ],
    "polygon": [
      [
        52.36,
        25.02
      ],
      [
        52.48,
        25.06
      ],
      [
        52.5,
        25.38
      ],
      [
        52.38,
        25.32
      ],
      [
        52.36,
        25.02
      ]
    ],
    "area_sq_km": 193,
    "established_year": 1991,
    "description_ru": "Крупнейшее низинное болото Центральной Европы. Главное мировое место гнездования исчезающей вертлявой камышевки.",
    "key_species": [
      "Вертлявая камышевка",
      "Болотная черепаха"
    ]
  },
  {
    "id": "yelnya",
    "name_ru": "Заказник «Ельня»",
    "name_be": "Заказнік «Ельня»",
    "type": "reserve",
    "center": [
      55.55,
      27.85
    ],
    "polygon": [
      [
        55.44,
        27.72
      ],
      [
        55.66,
        27.68
      ],
      [
        55.7,
        28.06
      ],
      [
        55.48,
        28.12
      ],
      [
        55.44,
        27.72
      ]
    ],
    "area_sq_km": 253,
    "established_year": 1968,
    "description_ru": "Один из крупнейших комплексов верховых болот в Европе возрастом более 9 000 лет. Тысячи озерков, стоянка серых журавлей.",
    "key_species": [
      "Черный аист",
      "Серый журавль",
      "Белая куропатка"
    ]
  },
  {
    "id": "olmany",
    "name_ru": "Заказник «Ольманские болота»",
    "name_be": "Заказнік «Альманскія балоты»",
    "type": "reserve",
    "center": [
      51.85,
      27.35
    ],
    "polygon": [
      [
        51.74,
        27.12
      ],
      [
        51.96,
        27.16
      ],
      [
        51.99,
        27.62
      ],
      [
        51.76,
        27.58
      ],
      [
        51.74,
        27.12
      ]
    ],
    "area_sq_km": 942,
    "established_year": 1998,
    "description_ru": "Крупнейший в Европе массив нетронутых переходных и верховых болот Полесья. Царство болотной черепахи и орлана-белохвоста.",
    "key_species": [
      "Европейская болотная черепаха",
      "Орлан-белохвост",
      "Змееяд"
    ]
  },
  {
    "id": "naliboki",
    "name_ru": "Заказник «Налибокская пуща»",
    "name_be": "Заказнік «Налібоцкая пушча»",
    "type": "reserve",
    "center": [
      53.95,
      26.35
    ],
    "polygon": [
      [
        53.76,
        26.12
      ],
      [
        54.12,
        26.16
      ],
      [
        54.16,
        26.68
      ],
      [
        53.82,
        26.62
      ],
      [
        53.76,
        26.12
      ]
    ],
    "area_sq_km": 868,
    "established_year": 2005,
    "description_ru": "Огромный сплошной лесной массив в бассейне Немана и Березины. Обитают вольноживущие тарпановидные дикие лошади коник и зубры.",
    "key_species": [
      "Европейский зубр",
      "Европейская рысь",
      "Бурый медведь"
    ]
  },
  {
    "id": "krasny-bor",
    "name_ru": "Заказник «Красный Бор»",
    "name_be": "Заказнік «Чырвоны Бор»",
    "type": "reserve",
    "center": [
      55.95,
      28.5
    ],
    "polygon": [
      [
        55.84,
        28.32
      ],
      [
        56.09,
        28.28
      ],
      [
        56.12,
        28.76
      ],
      [
        55.86,
        28.72
      ],
      [
        55.84,
        28.32
      ]
    ],
    "area_sq_km": 342,
    "established_year": 1997,
    "description_ru": "Северный таежный край ледниковых холмов, озер и древних сосновых боров на границе с Россией. Плотная популяция бурого медведя.",
    "key_species": [
      "Бурый медведь",
      "Бородатая неясыть",
      "Рысь"
    ]
  },
  {
    "id": "srednyaya-pripyat",
    "name_ru": "Заказник «Средняя Припять»",
    "name_be": "Заказнік «Сярэдняя Прыпяць»",
    "type": "reserve",
    "center": [
      52.15,
      26.8
    ],
    "polygon": [
      [
        52.04,
        26.42
      ],
      [
        52.26,
        26.38
      ],
      [
        52.3,
        27.32
      ],
      [
        52.06,
        27.28
      ],
      [
        52.04,
        26.42
      ]
    ],
    "area_sq_km": 930,
    "established_year": 1999,
    "description_ru": "Пойменная речная экосистема мирового значения, Рамсарское водно-болотное угодье, коридор весенней миграции птиц.",
    "key_species": [
      "Вертлявая камышевка",
      "Стерлядь",
      "Черный аист"
    ]
  }
];

const BELARUS_REGIONS = [
  {
    "id": "brest",
    "name_ru": "Брестская область",
    "name_be": "Брэсцкая вобласць",
    "center": [
      52.35,
      25.5
    ],
    "area_sq_km": 32787,
    "color": "#16a34a",
    "description_ru": "Край полесских болот, древней Беловежской пущи и уникальных популяций вертлявой камышевки."
  },
  {
    "id": "vitebsk",
    "name_ru": "Витебская область",
    "name_be": "Віцебская вобласць",
    "center": [
      55.2,
      29.3
    ],
    "area_sq_km": 40051,
    "color": "#0284c7",
    "description_ru": "Белорусское Поозерье: Браславские озера, древнейшие верховые болота Ельня и Березинский заповедник."
  },
  {
    "id": "gomel",
    "name_ru": "Гомельская область",
    "name_be": "Гомельская вобласць",
    "center": [
      52.15,
      29.8
    ],
    "area_sq_km": 40372,
    "color": "#d97706",
    "description_ru": "Белорусское Полесье: пойма реки Припять, дубравы, ареал болотной черепахи и жука-оленя."
  },
  {
    "id": "grodno",
    "name_ru": "Гродненская область",
    "name_be": "Гродзенская вобласць",
    "center": [
      53.5,
      25.0
    ],
    "area_sq_km": 25127,
    "color": "#059669",
    "description_ru": "Бассейн реки Неман, северная часть Беловежской пущи, болота Дикое и Грайно."
  },
  {
    "id": "minsk",
    "name_ru": "Минская область",
    "name_be": "Мінская вобласць",
    "center": [
      53.9,
      27.56
    ],
    "area_sq_km": 39854,
    "color": "#7c3aed",
    "description_ru": "Центральная Беларусь: озеро Нарочь, Налибокская пуща, заказники и колонии крапчатого суслика."
  },
  {
    "id": "mogilev",
    "name_ru": "Могилевская область",
    "name_be": "Магілёўская вобласць",
    "center": [
      53.75,
      30.7
    ],
    "area_sq_km": 29068,
    "color": "#ea580c",
    "description_ru": "Восточные дубравы, гидрологические заказники рек Сож и Днепр, места обитания стерляди."
  }
];
