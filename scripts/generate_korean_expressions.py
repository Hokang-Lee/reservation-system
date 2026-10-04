import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF_DIR = ROOT / "docs"
OUTPUT = ROOT / "korean-expressions.js"

# A small, deliberately familiar glossary. These concepts repeat throughout
# the source texts and are easier to review than a whole sentence.
GLOSSARY = [
    ("하늘부모님", "天の父母様", "ハヌルプモニム"), ("참부모님", "真の父母様", "チャムブモニム"),
    ("독생녀", "ひとり娘", "トクセンニョ"), ("독생자", "ひとり子", "トクセンジャ"),
    ("한민족", "韓民族", "ハンミンジョク"), ("대한민국", "大韓民国", "テハンミングク"),
    ("한반도", "朝鮮半島", "ハンバンド"), ("기독교", "キリスト教", "キドッキョ"),
    ("불교", "仏教", "プルギョ"), ("유교", "儒教", "ユギョ"), ("하나님", "神", "ハナニム"),
    ("환웅", "桓雄", "ファヌン"), ("호랑이", "虎", "ホランイ"), ("곰", "熊", "コム"),
    ("한글", "ハングル", "ハングル"), ("자음", "子音", "チャウム"), ("모음", "母音", "モウム"),
    ("발음", "発音", "パルム"), ("일본군", "日本軍", "イルボングン"), ("김일성", "金日成", "キム・イルソン"),
    ("역사", "歴史", "ヨクサ"), ("인류", "人類", "インリュ"), ("민족", "民族", "ミンジョク"),
    ("세계", "世界", "セゲ"), ("평화", "平和", "ピョンファ"), ("사랑", "愛", "サラン"),
    ("희망", "希望", "ヒマン"), ("문화", "文化", "ムナ"), ("전통", "伝統", "チョントン"),
    ("정체성", "アイデンティティ", "チョンチェソン"), ("신앙", "信仰", "シナン"),
    ("가정", "家庭", "カジョン"), ("가족", "家族", "カジョク"), ("조국", "祖国", "チョグク"),
    ("한국", "韓国", "ハングク"), ("조선", "朝鮮", "チョソン"), ("독립", "独立", "トンニプ"),
    ("통일", "統一", "トンイル"), ("자유", "自由", "チャユ"), ("정의", "正義", "チョンイ"),
    ("생명", "生命", "センミョン"), ("창조", "創造", "チャンジョ"), ("미래", "未来", "ミレ"),
    ("꿈", "夢", "クム"), ("비전", "ビジョン", "ピジョン"), ("지혜", "知恵", "チヘ"),
    ("도덕", "道徳", "トドク"), ("책임", "責任", "チェギム"), ("역할", "役割", "ヨカル"),
    ("교육", "教育", "キョユク"), ("지도자", "指導者", "チドジャ"), ("발전", "発展", "パルチョン"),
    ("사회", "社会", "サフェ"), ("국가", "国家", "クッカ"), ("인간", "人間", "インガン"),
    ("마음", "心", "マウム"), ("감사", "感謝", "カムサ"), ("효정", "孝情", "ヒョジョン"),
    ("축복", "祝福", "チュクポク"), ("하늘", "天・空", "ハヌル"),
]

IPA = {
    "하늘부모님": "ha.nɯl.bu.mo.nim", "참부모님": "tɕʰam.bu.mo.nim",
    "독생녀": "tok.s͈ɛŋ.njʌ", "독생자": "tok.s͈ɛŋ.dʑa",
    "한민족": "han.min.dʑok", "대한민국": "tɛ.han.min.ɡuk",
    "한반도": "han.ban.do", "기독교": "ki.dok.k͈jo", "불교": "pul.ɡjo",
    "유교": "ju.ɡjo", "하나님": "ha.na.nim", "환웅": "hwan.uŋ",
    "호랑이": "ho.ɾaŋ.i", "곰": "kom", "한글": "han.ɡɯl",
    "자음": "tɕa.ɯm", "모음": "mo.ɯm", "발음": "pa.ɾɯm",
    "일본군": "il.bon.ɡun", "김일성": "kim.il.s͈ʌŋ", "역사": "jʌk.s͈a",
    "인류": "il.lju", "민족": "min.dʑok", "세계": "se.ɡje",
    "평화": "pʰjʌŋ.hwa", "사랑": "sa.ɾaŋ", "희망": "hi.maŋ",
    "문화": "mun.hwa", "전통": "tɕʌn.tʰoŋ", "정체성": "tɕʌŋ.tɕʰe.s͈ʌŋ",
    "신앙": "ɕi.naŋ", "가정": "ka.dʑʌŋ", "가족": "ka.dʑok",
    "조국": "tɕo.ɡuk", "한국": "han.ɡuk", "조선": "tɕo.sʌn",
    "독립": "toŋ.nip", "통일": "tʰoŋ.il", "자유": "tɕa.ju",
    "정의": "tɕʌŋ.ɰi", "생명": "sɛŋ.mjʌŋ", "창조": "tɕʰaŋ.dʑo",
    "미래": "mi.ɾɛ", "꿈": "k͈um", "비전": "pi.dʑʌn",
    "지혜": "tɕi.hje", "도덕": "to.dʌk", "책임": "tɕʰɛ.gim",
    "역할": "jʌ.kʰal", "교육": "kjo.juk", "지도자": "tɕi.do.dʑa",
    "발전": "pal.tɕ͈ʌn", "사회": "sa.hwe", "국가": "kuk.k͈a",
    "인간": "in.ɡan", "마음": "ma.ɯm", "감사": "kam.sa",
    "효정": "hjo.dʑʌŋ", "축복": "tɕʰuk.p͈ok", "하늘": "ha.nɯl",
}

PEOPLE = [
    ("단군", "タングン", "檀君"), ("환웅", "ファヌン", "桓雄"),
    ("을지문덕", "ウルチ・ムンドク", "乙支文徳"), ("강감찬", "カン・ガムチャン", "姜邯贊"),
    ("광개토대왕", "クァンゲト大王", "広開土王"), ("세종대왕", "セジョン大王", "世宗大王"),
    ("장영실", "チャン・ヨンシル", "蒋英実"), ("문익점", "ムン・イクチョム", "文益漸"),
    ("이순신", "イ・スンシン", "李舜臣"), ("신사임당", "シン・サイムダン", "申師任堂"),
    ("유형원", "ユ・ヒョンウォン", "柳馨遠"), ("이익", "イ・イク", "李瀷"),
    ("정약용", "チョン・ヤギョン", "丁若鏞"), ("최치원", "チェ・チウォン", "崔致遠"),
    ("최제우", "チェ・ジェウ", "崔濟愚"), ("최시형", "チェ・シヒョン", "崔時亨"),
    ("손병희", "ソン・ビョンヒ", "孫秉熙"),
    # 近代キリスト教・宗教運動（本文121〜125番にも登場）
    ("김익두", "キム・イクド", "金益斗"), ("이용도", "イ・ヨンド", "李龍道"),
    ("길선주", "キル・ソンジュ", "吉善宙"),
    ("이승만", "イ・スンマン", "李承晩"),
    ("김구", "キム・グ", "金九"), ("안중근", "アン・ジュングン", "安重根"),
    ("유관순", "ユ・グァンスン", "柳寛順"), ("이회영", "イ・フェヨン", "李會榮"),
    ("신채호", "シン・チェホ", "申采浩"), ("한용운", "ハン・ヨンウン", "韓龍雲"),
    ("이승훈", "イ・スンフン", "李承薫"), ("이수정", "イ・スジョン", "李樹廷"),
    ("최린", "チェ・リン", "崔麟"), ("오세창", "オ・セチャン", "吳世昌"),
    ("권동진", "クォン・ドンジン", "權東鎭"), ("고경명", "コ・ギョンミョン", "高敬命"),
    ("김일성", "キム・イルソン", "金日成"), ("문선명", "ムン・ソンミョン", "文鮮明"),
    ("한학자", "ハン・ハクチャ", "韓鶴子"), ("원효", "ウォニョ", "元暁"),
    ("이황", "イ・ファン", "李滉"), ("이이", "イ・イ", "李珥"),
]


def korean_sentences(pdf_path: Path) -> list[str]:
    text = "\n".join(page.extract_text() or "" for page in PdfReader(str(pdf_path)).pages)
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if len(re.findall(r"[가-힣]", line)) >= 6 and not re.search(r"[ぁ-んァ-ン]", line):
            lines.append(line)
    return [
        sentence.strip()
        for line in lines
        for sentence in re.split(r"(?<=[.!?])\s+", line)
        if len(re.findall(r"[가-힣]", sentence)) >= 6
    ]


def short_example(sentence: str) -> str:
    sentence = re.sub(r"^[（(][0-9 ]+[）)]\s*", "", sentence).strip()
    sentence = re.sub(r"\s+([.!?])", r"\1", sentence)
    return sentence if len(sentence) <= 42 else sentence[:41].rstrip() + "…"


documents = [
    (pdf_path.stem, korean_sentences(pdf_path))
    for pdf_path in sorted(PDF_DIR.glob("*.pdf"), key=lambda path: int(path.stem))
]
document_sentences = [sentences for _, sentences in documents]

# Keep one representative example for each glossary word, and also record
# every document in which it really appears.  The page uses the latter map;
# a word must never be shown for a day whose source documents do not contain it.
words = []
words_by_document = {}
person_names = {name for name, _, _ in PEOPLE}
for word, meaning, pronunciation in GLOSSARY:
    # 人名は「今日の韓国人物」だけで扱う。重要単語欄との二重表示を防ぐ。
    if word in person_names:
        continue
    example = next(
        (
            sentence
            for sentences in document_sentences
            for sentence in sentences
            if word in sentence
        ),
        None,
    )
    if example:
        entry = {
            "word": word,
            "pronunciation": pronunciation,
            "ipa": IPA[word],
            "meaning": meaning,
            "example": short_example(example),
        }
        words.append(entry)
        for document_id, sentences in documents:
            document_example = next((sentence for sentence in sentences if word in sentence), None)
            if not document_example:
                continue
            words_by_document.setdefault(document_id, []).append({
                **entry,
                "example": short_example(document_example),
            })

people = []
people_by_document = {}
for name, pronunciation, japanese_name in PEOPLE:
    person_was_found = False
    for document_id, sentences in documents:
        example = next((sentence for sentence in sentences if name in sentence), None)
        if not example:
            continue
        person_was_found = True
        entry = {
            "name": name,
            "pronunciation": pronunciation,
            "japaneseName": japanese_name,
            "example": short_example(example),
        }
        people_by_document.setdefault(document_id, []).append(entry)
    if person_was_found:
        people.append(name)

OUTPUT.write_text(
    "// Generated by scripts/generate_korean_expressions.py\n"
    f"window.KOREAN_WORD_LIST = {json.dumps(words, ensure_ascii=False, indent=2)};\n"
    f"window.KOREAN_WORDS_BY_DOCUMENT = {json.dumps(words_by_document, ensure_ascii=False, indent=2)};\n"
    f"window.KOREAN_PEOPLE_BY_DOCUMENT = {json.dumps(people_by_document, ensure_ascii=False, indent=2)};\n",
    encoding="utf-8",
)

print(f"Generated {len(words)} words and {len(people)} people in {OUTPUT.name}")
