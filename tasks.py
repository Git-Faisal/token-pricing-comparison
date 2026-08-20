"""Task definitions: 5 task types x 2 languages (English / Arabic mirrors).

Sudoku puzzles come from the Sudoku-Extreme benchmark test split
(https://huggingface.co/datasets/sapientinc/sudoku-extreme):
  - sudoku_moderate: source puzzles1_unbiased, rating 1
  - sudoku_extreme:  source puzzles4_forum_hardest_1905, rating 60
Reference answers are the dataset's own solutions.

Design choices (documented in README):
  - Arabic mirrors keep Western digits, so grading and token differences
    isolate the language of instructions/content, not numeral systems.
  - The flight-search tool schema stays in English in both mirrors, as it
    would in a real product.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _read(name: str) -> str:
    with open(os.path.join(HERE, "tasks", name), encoding="utf-8") as f:
        return f.read()


SUDOKU_MODERATE_PUZZLE = ".9...12...3..284.6.6.....8..7....14..2..5.7....3.....2.1.9........7.5....872.6..4"
SUDOKU_MODERATE_ANSWER = "598461273731528496264397581879632145426159738153874962615943827342785619987216354"
SUDOKU_EXTREME_PUZZLE = ".....8..1.6.9..2...4.52.9..4..6......9..45..6....924..9......7........3.35.2..6.."
SUDOKU_EXTREME_ANSWER = "529768341763914285148523967435671829892345716617892453984136572276459138351287694"


def _grid(puzzle: str) -> str:
    return "\n".join(puzzle[i * 9:(i + 1) * 9] for i in range(9))


def _sudoku_prompt_en(puzzle: str) -> str:
    return (
        "Solve this Sudoku puzzle. Dots are empty cells.\n\n"
        + _grid(puzzle)
        + "\n\nFill every cell so that each row, each column, and each 3x3 box "
        "contains the digits 1-9 exactly once.\n"
        "The last line of your reply must be exactly:\n"
        "FINAL: <the solved grid as one string of 81 digits, row by row, no spaces>"
    )


def _sudoku_prompt_ar(puzzle: str) -> str:
    return (
        "حُلّ لغز السودوكو التالي. النقاط تمثل خانات فارغة.\n\n"
        + _grid(puzzle)
        + "\n\nاملأ كل خانة بحيث يحتوي كل صف وكل عمود وكل مربع 3×3 على الأرقام من 1 إلى 9 مرة واحدة بالضبط.\n"
        "يجب أن يكون السطر الأخير من إجابتك بالضبط:\n"
        "FINAL: <الشبكة المحلولة كسلسلة واحدة من 81 رقماً، صفاً بعد صف، دون مسافات>"
    )


ROSTER_SOLUTION = {
    "sun_day": ["Fahad", "Layla"], "sun_night": ["Noura", "Omar"],
    "mon_day": ["Fahad", "Salem"], "mon_night": ["Noura", "Omar"],
    "tue_day": ["Fahad", "Layla"], "tue_night": ["Omar", "Salem"],
    "wed_day": ["Layla", "Noura"], "wed_night": ["Omar", "Salem"],
    "thu_day": ["Layla", "Noura"], "thu_night": ["Omar", "Salem"],
}

ROSTER_PROMPT_EN = """You are the operations manager at Al-Waha Logistics. Build next week's driver roster.

Drivers: Salem, Layla, Fahad, Omar, Noura.
Shifts: Sunday through Thursday, a day shift and a night shift each day. Every shift is staffed by exactly 2 drivers.

Rules (all must hold):
1. Exact weekly shift counts: Salem 4, Layla 4, Fahad 3, Omar 5, Noura 4.
2. Rest rule: a driver who works a night shift cannot work the next morning's day shift.
3. Refrigerated-cargo rule: every shift needs at least one certified driver. Only Salem, Layla, and Noura are certified.
4. Night shifts require a forklift licence. Fahad has no forklift licence.
5. Fahad is unavailable on Wednesday.
6. Noura and Fahad must never share a shift.
7. Nobody works both shifts of the same day.
8. Layla cannot work night shifts (evening classes).
9. Noura must work exactly 2 night shifts this week.
10. Salem cannot work the Sunday day shift.

This puzzle has exactly one valid roster. Find it.
Reply with ONLY a JSON object with exactly these keys: sun_day, sun_night, mon_day, mon_night, tue_day, tue_night, wed_day, wed_night, thu_day, thu_night. Each value is an array of exactly 2 driver names."""

ROSTER_PROMPT_AR = """أنت مدير العمليات في شركة الواحة للخدمات اللوجستية. قم بإعداد جدول مناوبات السائقين للأسبوع القادم.

السائقون: Salem، Layla، Fahad، Omar، Noura.
المناوبات: من الأحد إلى الخميس، مناوبة نهارية ومناوبة ليلية كل يوم. كل مناوبة يعمل فيها سائقان بالضبط.

القواعد (يجب تحقيقها جميعاً):
1. عدد المناوبات الأسبوعية بالضبط: Salem 4، Layla 4، Fahad 3، Omar 5، Noura 4.
2. قاعدة الراحة: السائق الذي يعمل مناوبة ليلية لا يمكنه العمل في المناوبة النهارية لصباح اليوم التالي.
3. قاعدة البضائع المبردة: كل مناوبة تحتاج إلى سائق معتمد واحد على الأقل. المعتمدون هم Salem وLayla وNoura فقط.
4. المناوبات الليلية تتطلب رخصة رافعة شوكية. Fahad لا يملك رخصة رافعة شوكية.
5. Fahad غير متاح يوم الأربعاء.
6. Noura وFahad لا يجوز أن يعملا في المناوبة نفسها أبداً.
7. لا يعمل أي سائق في مناوبتي اليوم نفسه.
8. Layla لا يمكنها العمل في المناوبات الليلية (دروس مسائية).
9. Noura يجب أن تعمل مناوبتين ليليتين بالضبط هذا الأسبوع.
10. Salem لا يمكنه العمل في المناوبة النهارية يوم الأحد.

لهذا اللغز جدول صحيح واحد فقط. جِده.
أجب فقط بكائن JSON يحتوي بالضبط على هذه المفاتيح: sun_day, sun_night, mon_day, mon_night, tue_day, tue_night, wed_day, wed_night, thu_day, thu_night. قيمة كل مفتاح مصفوفة من اسمي سائقين بالضبط."""

FLIGHT_TOOL = {
    "type": "function",
    "function": {
        "name": "search_flights",
        "description": "Search available flights between two airports on a date. Returns a JSON list of flights with airline, flight number, price in USD, and number of stops.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "IATA airport code, e.g. RUH"},
                "destination": {"type": "string", "description": "IATA airport code, e.g. LHR"},
                "date": {"type": "string", "description": "Departure date, YYYY-MM-DD"},
            },
            "required": ["origin", "destination", "date"],
        },
    },
}

FLIGHT_TOOL_RESULT = (
    '[{"airline": "Wizz Air", "flight": "W6 741", "price_usd": 189, "stops": 1},'
    ' {"airline": "Saudia", "flight": "SV 117", "price_usd": 432, "stops": 0},'
    ' {"airline": "British Airways", "flight": "BA 262", "price_usd": 511, "stops": 0}]'
)

TASKS = [
    {
        "id": "docqa_en",
        "type": "docqa",
        "lang": "en",
        "prompt": _read("docqa_en.txt"),
        "max_tokens": 4000,
        "grade": {"kind": "contains_all", "expected": [["84.6"], ["94.2"], ["May 14", "14 May", "2026-05-14", "May 14th"]]},
    },
    {
        "id": "docqa_ar",
        "type": "docqa",
        "lang": "ar",
        "prompt": _read("docqa_ar.txt"),
        "max_tokens": 4000,
        "grade": {"kind": "contains_all", "expected": [["84.6"], ["94.2"], ["14 مايو", "مايو 14", "2026-05-14", "14/5", "14-5"]]},
    },
    {
        "id": "extract_en",
        "type": "extract",
        "lang": "en",
        "prompt": _read("invoice_en.txt"),
        "max_tokens": 4000,
        "grade": {
            "kind": "json_fields",
            "expected": {"invoice_number": "INV-2026-0847", "total_incl_vat": 35857.0, "num_line_items": 3, "currency": "SAR"},
        },
    },
    {
        "id": "extract_ar",
        "type": "extract",
        "lang": "ar",
        "prompt": _read("invoice_ar.txt"),
        "max_tokens": 4000,
        "grade": {
            "kind": "json_fields",
            "expected": {"invoice_number": "INV-2026-0847", "total_incl_vat": 35857.0, "num_line_items": 3},
        },
    },
    {
        "id": "sudoku_moderate_en",
        "type": "sudoku_moderate",
        "lang": "en",
        "prompt": _sudoku_prompt_en(SUDOKU_MODERATE_PUZZLE),
        "max_tokens": 16000,
        "grade": {"kind": "sudoku", "expected": SUDOKU_MODERATE_ANSWER},
    },
    {
        "id": "sudoku_moderate_ar",
        "type": "sudoku_moderate",
        "lang": "ar",
        "prompt": _sudoku_prompt_ar(SUDOKU_MODERATE_PUZZLE),
        "max_tokens": 16000,
        "grade": {"kind": "sudoku", "expected": SUDOKU_MODERATE_ANSWER},
    },
    {
        "id": "sudoku_extreme_en",
        "type": "sudoku_extreme",
        "lang": "en",
        "prompt": _sudoku_prompt_en(SUDOKU_EXTREME_PUZZLE),
        "max_tokens": 32000,
        "grade": {"kind": "sudoku", "expected": SUDOKU_EXTREME_ANSWER},
    },
    {
        "id": "sudoku_extreme_ar",
        "type": "sudoku_extreme",
        "lang": "ar",
        "prompt": _sudoku_prompt_ar(SUDOKU_EXTREME_PUZZLE),
        "max_tokens": 32000,
        "grade": {"kind": "sudoku", "expected": SUDOKU_EXTREME_ANSWER},
    },
    {
        "id": "roster_en",
        "type": "roster",
        "lang": "en",
        "prompt": ROSTER_PROMPT_EN,
        "max_tokens": 128000,
        "grade": {"kind": "roster", "expected": ROSTER_SOLUTION},
    },
    {
        "id": "roster_ar",
        "type": "roster",
        "lang": "ar",
        "prompt": ROSTER_PROMPT_AR,
        "max_tokens": 128000,
        "grade": {"kind": "roster", "expected": ROSTER_SOLUTION},
    },
    {
        "id": "agentic_en",
        "type": "agentic",
        "lang": "en",
        "prompt": (
            "Using the search_flights tool, find the cheapest flight from Riyadh (RUH) "
            "to London (LHR) on 2026-09-10, then answer in one sentence with the airline "
            "and the price in USD."
        ),
        "max_tokens": 4000,
        "tools": [FLIGHT_TOOL],
        "tool_result": FLIGHT_TOOL_RESULT,
        "grade": {"kind": "agentic", "expected": ["Wizz", "189"]},
    },
    {
        "id": "agentic_ar",
        "type": "agentic",
        "lang": "ar",
        "prompt": (
            "باستخدام أداة search_flights، ابحث عن أرخص رحلة طيران من الرياض (RUH) "
            "إلى لندن (LHR) بتاريخ 2026-09-10، ثم أجب في جملة واحدة باسم شركة الطيران "
            "والسعر بالدولار الأمريكي."
        ),
        "max_tokens": 4000,
        "tools": [FLIGHT_TOOL],
        "tool_result": FLIGHT_TOOL_RESULT,
        "grade": {"kind": "agentic", "expected": ["189"]},
    },
]
