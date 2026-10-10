from __future__ import annotations





import json





import os





import sqlite3





import subprocess





import tempfile





from datetime import datetime, timezone





from http import HTTPStatus





from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer





from pathlib import Path





from urllib.parse import urlparse





from progression import choose_next
from source_progress import record_source_ac, SourceProgressError
from problems import get_problem, public_problem





from judge import judge_cpp


from source_catalog import SOURCE_LEVELS, SOURCE_NAME, SOURCE_SITE, SOURCE_TITLES, source_problem_url





ROOT = Path(__file__).resolve().parent





STATIC_DIR = ROOT / "static"





DATA_DIR = Path(os.environ["STUDY_COACH_DATA_DIR"]).resolve() if os.environ.get("STUDY_COACH_DATA_DIR") else ROOT / "data"





DB_PATH = DATA_DIR / "study.db"





HOST = os.environ.get("STUDY_COACH_HOST", "127.0.0.1")





PORT = int(os.environ.get("STUDY_COACH_PORT", "8780"))





LEVELS = SOURCE_LEVELS





TITLES_TEXT = """In Hello World





In tên của em





In tuổi của em





In tên trường





In 3 dòng giới thiệu bản thân





Vẽ hình vuông bằng ký tự *





Vẽ hình chữ nhật bằng *





In mặt cười ASCII





In hình ngôi nhà đơn giản





In cây thông





Nhập tên rồi chào người dùng





Nhập tuổi rồi in lại





Nhập tên và tuổi





Nhập hai số





Tính tổng hai số





Tính hiệu hai số





Tính tích hai số





Tính thương hai số





Tính tổng ba số





Tính chu vi hình vuông





Tính diện tích hình vuông





Tính chu vi hình chữ nhật





Tính diện tích hình chữ nhật





Tính diện tích tam giác





Đổi mét sang centimet





Đổi centimet sang mét





Đổi giờ sang phút





Đổi phút sang giây





Tính tuổi sau 10 năm





Tính năm sinh từ tuổi





Tính trung bình hai số





Tính trung bình ba số





Tính tiền mua 5 cây bút





Tính tiền thừa





Tính số kẹo chia đều





Tính số kẹo còn dư





Đổi độ C sang độ F





Đổi độ F sang độ C





Tính diện tích hình tròn





Tính chu vi hình tròn





Tính cạnh huyền tam giác vuông





Tính quãng đường từ vận tốc và thời gian





Tính vận tốc





Tính thời gian di chuyển





Đổi km sang mét





Đổi kg sang gram





Đổi lít sang ml





Tính tổng số chân của gà





Tính tổng chân của chó và gà





Tính số bánh trong nhiều hộp





Tách hàng đơn vị của số hai chữ số





Tách hàng chục





Tính tổng hai chữ số





Đảo số có hai chữ số





Tách ba chữ số





Tính tổng ba chữ số





Đảo số có ba chữ số





Tính số giây của một ngày





Tính số phút của một tuần





Tính số ngày đã sống xấp xỉ từ tuổi





Kiểm tra số dương





Kiểm tra số âm





Kiểm tra số 0





Kiểm tra chẵn/lẻ





Tìm số lớn hơn trong hai số





Tìm số nhỏ hơn trong hai số





Tìm lớn nhất trong ba số





Tìm nhỏ nhất trong ba số





Kiểm tra đủ tuổi đi học





Kiểm tra đủ tuổi xem phim





Xếp loại điểm đạt/chưa đạt





Xếp loại Giỏi/Khá/Trung bình





Kiểm tra số chia hết cho 3





Kiểm tra chia hết cho 5





Kiểm tra chia hết cho cả 3 và 5





Kiểm tra năm nhuận





Kiểm tra tháng có 30 hay 31 ngày





Kiểm tra ba cạnh có tạo thành tam giác





Nhận biết tam giác đều





Nhận biết tam giác cân





Nhận biết tam giác vuông





So sánh tuổi hai bạn





Tính giá vé theo tuổi





Tính giảm giá theo số tiền mua





Tính tiền điện đơn giản theo mức





Máy tính + - × ÷





Chọn đồ uống theo menu





Trò đoán số một lần





Kiểm tra mật khẩu đơn giản





Trò Oẳn-Tù-Tì cơ bản





In số 1–10





In số 1–100





In số 100 về 1





In số chẵn từ 1–100





In số lẻ từ 1–100





In bội số của 5





Tính tổng 1 đến n





Tính tổng số chẵn đến n





Tính tổng số lẻ đến n





Tính 1² + 2² + ... + n²





In bảng cửu chương 2





In bảng cửu chương n





In toàn bộ bảng cửu chương





Đếm từ 10 về 0





Đồng hồ đếm ngược





Tính n!





Tính 2^n





Đếm số chữ số của n





Tính tổng chữ số





Đảo ngược số





Kiểm tra số đối xứng





Tìm chữ số lớn nhất





Tìm chữ số nhỏ nhất





Đếm chữ số chẵn





Đếm chữ số lẻ





Liệt kê các ước của n





Đếm số ước





Tính tổng các ước





Kiểm tra số nguyên tố





Liệt kê số nguyên tố từ 1 đến n





Vẽ hàng 10 dấu *





Vẽ hình vuông





Vẽ hình chữ nhật





Vẽ tam giác vuông





Vẽ tam giác vuông ngược





Vẽ tam giác bằng số





Vẽ tam giác 1 22 333





Vẽ bảng số





Vẽ bàn cờ bằng ký tự





Vẽ khung chữ nhật rỗng





Vẽ hình vuông rỗng





Vẽ chữ X





Vẽ dấu cộng





Vẽ kim tự tháp





Vẽ kim tự tháp ngược





Vẽ hình thoi





Vẽ cây thông Noel





Vẽ cây thông nhiều tầng





Vẽ ngôi nhà ASCII





Vẽ đồng hồ cát





Vẽ bảng tọa độ





In dãy số tăng dần





In dãy số giảm dần theo hàng





Tam giác bảng cửu chương





Tam giác số liên tiếp





Tam giác Pascal đơn giản





Vẽ chữ A bằng *





Vẽ chữ H





Vẽ chữ T





Viết tên bằng ASCII Art





Nhập 5 số vào mảng/vector





In toàn bộ mảng/vector





Tính tổng mảng/vector





Tính trung bình mảng/vector





Tìm số lớn nhất





Tìm số nhỏ nhất





Tìm vị trí số lớn nhất





Tìm vị trí số nhỏ nhất





Đếm số chẵn





Đếm số lẻ





Đếm số dương





Đếm số âm





Tính tổng số chẵn





Tính tổng số lẻ





Tìm số lớn thứ hai





Đảo ngược mảng/vector





Kiểm tra mảng tăng dần





Kiểm tra mảng giảm dần





Tìm một số trong mảng/vector





Đếm số lần x xuất hiện





Thay mọi số âm bằng 0





Nhân mọi phần tử với 2





Tách số chẵn và số lẻ





Đếm số nguyên tố trong mảng/vector





Tìm các số nguyên tố





Sắp xếp tăng dần





Sắp xếp giảm dần





Xóa một phần tử





Thêm một phần tử





Loại bỏ phần tử trùng





Nhập tên và in tên





Đếm số ký tự





Đếm chữ cái





Đếm chữ số





Đếm khoảng trắng





Đếm nguyên âm





Đếm phụ âm





Đổi chữ thường thành chữ hoa





Đổi chữ hoa thành chữ thường





Viết hoa chữ cái đầu





Đảo ngược chuỗi





Kiểm tra từ đối xứng





Đếm số từ





Tìm từ dài nhất





Tìm ký tự xuất hiện nhiều nhất





Xóa khoảng trắng thừa





Kiểm tra mật khẩu dài tối thiểu 8 ký tự





Kiểm tra mật khẩu có số





Tạo username từ họ tên





Tạo lời chào theo tên





Mã hóa chữ bằng cách dịch 1 ký tự





Caesar Cipher đơn giản





Giải mã Caesar





Trò Hangman mini





Đếm một chữ xuất hiện bao nhiêu lần





Thay một từ trong câu





Kiểm tra câu có chứa từ khóa





Tách họ và tên





Viết tắt họ tên





Máy tạo nickname





Hàm tính tổng hai số





Hàm tìm max





Hàm tìm min





Hàm kiểm tra chẵn





Hàm kiểm tra số nguyên tố





Hàm tính giai thừa





Hàm tính lũy thừa





Hàm tính diện tích hình tròn





Hàm tính khoảng cách hai điểm





Hàm đổi nhiệt độ





Hàm tính tổng chữ số





Hàm đảo số





Hàm kiểm tra đối xứng





Hàm tìm UCLN





Hàm tìm BCNN





Fibonacci





Fibonacci bằng hàm





Đệ quy tính tổng 1→n





Đệ quy tính giai thừa





Đệ quy Fibonacci





Tìm kiếm tuyến tính





Binary Search





Bubble Sort





Selection Sort





Insertion Sort





So sánh hai thuật toán tìm kiếm





So sánh hai thuật toán sắp xếp





Đếm số bước thuật toán





Tìm cặp số có tổng bằng x





Tìm dãy con đơn giản





Đoán số 1–10





Đoán số 1–100





Đoán số có gợi ý lớn/nhỏ





Giới hạn 7 lần đoán





Oẳn-Tù-Tì





Oẳn-Tù-Tì nhiều vòng





Tung đồng xu





Tung xúc xắc





Hai xúc xắc





Đua xúc xắc





Quiz toán học





Quiz cộng





Quiz trừ





Quiz nhân





Quiz chia





Quiz bảng cửu chương





Hệ thống tính điểm quiz





Quiz 10 câu ngẫu nhiên





Trò tìm kho báu trên lưới





Trò mê cung dạng text





Tic-Tac-Toe mini





Game nhập đúng mật mã





Game chiến đấu Hero vs Monster





Hệ thống HP





Hệ thống tấn công ngẫu nhiên





Shop mua kiếm và giáp





Game nuôi thú ảo





Game chăm sóc robot





Game điều khiển robot trên lưới





Game phiêu lưu dạng văn bản





Máy tính bỏ túi





Đồng hồ đếm ngược





Máy tính tuổi





Máy tính BMI





Máy đổi đơn vị





Máy đổi nhiệt độ





Máy tính điểm học sinh





Quản lý danh sách điểm





Danh sách học sinh





Danh bạ mini





To-do list





Bộ đếm Pomodoro





Random tên học sinh





Random câu hỏi





Máy tạo mật khẩu





Máy tạo câu chuyện ngẫu nhiên





Chương trình học bảng cửu chương





Phần mềm luyện cộng trừ





Phần mềm luyện toán có điểm





Quiz kiến thức khoa học





Quiz Robotics





Robot tránh vật cản mô phỏng





Robot đi tới tọa độ





Robot giao hàng trên lưới





Mô phỏng đèn giao thông





Mô phỏng thang máy





Mô phỏng bãi đỗ xe





Mô phỏng Smart Home





Game hoàn chỉnh tự chọn





Dự án cuối khóa: thiết kế một sản phẩm lập trình của riêng học viên"""





TITLES = SOURCE_TITLES





if len(TITLES) != 300:





    raise RuntimeError(f"Expected 300 exercise titles, got {len(TITLES)}")





DIAGNOSTIC_QUEUE = [1, 15, 31, 61, 64, 73, 91, 97, 101, 109, 119, 121, 130, 151, 155, 159, 169]





OUTCOME_SCORE = {





    "independent": 1.00,





    "hint": 0.70,
    "external_pass": 0.70,





    "solution": 0.35,





    "failed": 0.15,





}





def utc_now() -> str:





    return datetime.now(timezone.utc).isoformat()





def level_for(exercise_id: int) -> tuple[int, str]:





    for idx, (lo, hi, topic) in enumerate(LEVELS, start=1):





        if lo <= exercise_id <= hi:





            return idx, topic





    return 10, "Khác"





def db() -> sqlite3.Connection:





    conn = sqlite3.connect(DB_PATH)





    conn.row_factory = sqlite3.Row





    return conn





def init_db() -> None:


    DATA_DIR.mkdir(parents=True, exist_ok=True)


    with db() as conn:


        conn.executescript(


            """


            CREATE TABLE IF NOT EXISTS exercises(


                id INTEGER PRIMARY KEY,


                title TEXT NOT NULL,


                level INTEGER NOT NULL,


                topic TEXT NOT NULL


            );


            CREATE TABLE IF NOT EXISTS attempts(


                id INTEGER PRIMARY KEY AUTOINCREMENT,


                exercise_id INTEGER NOT NULL,


                outcome TEXT NOT NULL,


                duration_sec INTEGER NOT NULL DEFAULT 0,


                compile_errors INTEGER NOT NULL DEFAULT 0,


                notes TEXT NOT NULL DEFAULT '',


                created_at TEXT NOT NULL,


                FOREIGN KEY(exercise_id) REFERENCES exercises(id)


            );


            CREATE TABLE IF NOT EXISTS meta(


                key TEXT PRIMARY KEY,


                value TEXT NOT NULL


            );


            """


        )





        rows = []


        for i, title in enumerate(TITLES, start=1):


            level, topic = level_for(i)


            rows.append((i, title, level, topic))


        conn.executemany(


            """


            INSERT INTO exercises(id,title,level,topic) VALUES(?,?,?,?)


            ON CONFLICT(id) DO UPDATE SET


                title=excluded.title,


                level=excluded.level,


                topic=excluded.topic


            """,


            rows,


        )


        conn.execute("DELETE FROM exercises WHERE id < 1 OR id > 300")





        defaults = {


            "current_video_number": "13",


            "current_video_title": "Vector trong C++",


            "current_video_percent": "100",


            "active_exercise_id": "1",


            "course_stage": "Đã xem đến Vector; bài tập dùng danh mục 300bàicode.vn",


            "exercise_source_name": SOURCE_NAME,


            "exercise_source_url": SOURCE_SITE,


            "progress_reset_id": "source-import-20261007",


        }


        for key, value in defaults.items():


            conn.execute("INSERT OR IGNORE INTO meta(key,value) VALUES(?,?)", (key, value))





def get_meta(conn: sqlite3.Connection) -> dict[str, str]:





    return {r["key"]: r["value"] for r in conn.execute("SELECT key,value FROM meta")}





def exercise_rows(conn: sqlite3.Connection) -> list[dict]:


    latest = {


        r["exercise_id"]: dict(r)


        for r in conn.execute(


            """


            SELECT a.*


            FROM attempts a


            JOIN (


                SELECT exercise_id, MAX(id) AS max_id


                FROM attempts GROUP BY exercise_id


            ) x ON x.max_id = a.id


            """


        )


    }


    rows = []


    for r in conn.execute("SELECT * FROM exercises ORDER BY id"):


        item = dict(r)


        att = latest.get(r["id"])


        item["latest_outcome"] = att["outcome"] if att else None


        item["status"] = (


            "mastered" if att and att["outcome"] in {"independent", "hint", "external_pass"}


            else "learning" if att


            else "new"


        )


        item["auto_judge"] = bool(get_problem(r["id"]))


        item["source_name"] = SOURCE_NAME


        item["source_url"] = source_problem_url(r["id"])


        rows.append(item)


    return rows





def topic_stats(conn: sqlite3.Connection) -> list[dict]:
    result = []
    for level_idx, (lo, hi, topic) in enumerate(LEVELS, start=1):
        rows = list(conn.execute(
            "SELECT outcome, exercise_id FROM attempts WHERE exercise_id BETWEEN ? AND ?",
            (lo, hi),
        ))
        best_by_exercise: dict[int, float] = {}
        for row in rows:
            exercise_id = int(row["exercise_id"])
            score = OUTCOME_SCORE.get(row["outcome"], 0.0)
            best_by_exercise[exercise_id] = max(best_by_exercise.get(exercise_id, 0.0), score)
        total_exercises = hi - lo + 1
        mastery = round(sum(best_by_exercise.values()) / total_exercises * 100, 1)
        independent = sum(1 for score in best_by_exercise.values() if score >= OUTCOME_SCORE["independent"])
        result.append({
            "level": level_idx,
            "topic": topic,
            "range": [lo, hi],
            "attempts": len(rows),
            "mastery": mastery,
            "independent_attempts": independent,
        })
    return result

def independent_streak(conn: sqlite3.Connection, lo: int, hi: int) -> int:





    rows = list(





        conn.execute(





            "SELECT outcome FROM attempts WHERE exercise_id BETWEEN ? AND ? ORDER BY id DESC LIMIT 10",





            (lo, hi),





        )





    )





    streak = 0





    for r in rows:





        if r["outcome"] == "independent":





            streak += 1





        else:





            break





    return streak





def first_unattempted(conn: sqlite3.Connection, lo: int, hi: int) -> int:


    tried = {


        r["exercise_id"]


        for r in conn.execute(


            "SELECT DISTINCT exercise_id FROM attempts WHERE exercise_id BETWEEN ? AND ?",


            (lo, hi),


        )


    }


    for x in range(lo, hi + 1):


        if x not in tried:


            return x


    return lo





def completed_exercise_ids(conn: sqlite3.Connection) -> set[int]:
    return {
        int(r["exercise_id"])
        for r in conn.execute(
            "SELECT DISTINCT exercise_id FROM attempts WHERE outcome IN ('independent','hint')"
        )
    }


def next_source_exercise(conn: sqlite3.Connection, after_id: int) -> int:
    completed = completed_exercise_ids(conn)
    for exercise_id in range(after_id + 1, 301):
        if exercise_id not in completed:
            return exercise_id
    for exercise_id in range(1, after_id + 1):
        if exercise_id not in completed:
            return exercise_id
    return 300


def recommendation(conn: sqlite3.Connection, stats: list[dict]) -> dict:
    return choose_next(conn, LEVELS, lambda exercise_id: get_problem(exercise_id) is not None)


def dashboard_payload() -> dict:





    with db() as conn:





        meta = get_meta(conn)





        exercises = exercise_rows(conn)





        stats = topic_stats(conn)





        rec = recommendation(conn, stats)





        attempted = conn.execute("SELECT COUNT(DISTINCT exercise_id) AS c FROM attempts").fetchone()["c"]





        mastered = conn.execute(





            "SELECT COUNT(*) AS c FROM attempts a "
            "JOIN (SELECT exercise_id, MAX(id) AS max_id FROM attempts GROUP BY exercise_id) x "
            "ON x.max_id=a.id WHERE a.outcome IN ('independent','hint','external_pass')"





        ).fetchone()["c"]





        recent = [





            dict(r)





            for r in conn.execute(





                """





                SELECT a.id,a.exercise_id,e.title,a.outcome,a.duration_sec,a.compile_errors,a.notes,a.created_at





                FROM attempts a JOIN exercises e ON e.id=a.exercise_id





                ORDER BY a.id DESC LIMIT 12





                """





            )





        ]





        payload = {





            "meta": meta,





            "summary": {





                "attempted": attempted,





                "mastered": mastered,





                "total": 300,





                "mastered_percent": round(mastered / 300 * 100, 1),





            },





            "recommendation": rec,





            "topics": stats,





            "exercises": exercises,





            "recent": recent,





        }





        compact = {





            "generated_at": utc_now(),





            "course": {





                "current_video_number": meta.get("current_video_number"),





                "current_video_title": meta.get("current_video_title"),





                "current_video_percent": meta.get("current_video_percent"),





            },





            "progress": payload["summary"],





            "recommendation": rec,





            "topics": stats,





            "recent_attempts": recent[:8],





        }





        (DATA_DIR / "chatgpt-summary.json").write_text(





            json.dumps(compact, ensure_ascii=False, indent=2),





            encoding="utf-8",





        )





        return payload





class Handler(SimpleHTTPRequestHandler):





    def __init__(self, *args, **kwargs):





        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)





    def log_message(self, format, *args):





        print("[Study-Coach]", format % args)





    def _json(self, payload, status=200):





        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")





        self.send_response(status)





        self.send_header("Content-Type", "application/json; charset=utf-8")





        self.send_header("Content-Length", str(len(body)))





        self.send_header("Cache-Control", "no-store")





        self.end_headers()





        self.wfile.write(body)





    def _read_json(self):





        size = int(self.headers.get("Content-Length", "0") or "0")





        raw = self.rfile.read(size) if size else b"{}"





        return json.loads(raw.decode("utf-8"))





    def do_GET(self):





        path = urlparse(self.path).path





        if path == "/api/dashboard":





            return self._json(dashboard_payload())





        if path.startswith("/api/exercise/"):





            try:





                exercise_id = int(path.rsplit("/", 1)[-1])





            except Exception:





                return self._json({"ok": False, "error": "Mã bài không hợp lệ."}, 400)





            problem = get_problem(exercise_id)





            if not problem:





                return self._json({"ok": False, "error": "Bài này chưa có bộ chấm tự động."}, 404)





            return self._json({"ok": True, "problem": public_problem(problem)})





        if path.startswith("/api/hint/"):





            try:





                exercise_id = int(path.rsplit("/", 1)[-1])





            except Exception:





                return self._json({"ok": False, "error": "Mã bài không hợp lệ."}, 400)





            problem = get_problem(exercise_id)





            if not problem:





                return self._json({"ok": False, "error": "Bài này chưa có gợi ý."}, 404)





            return self._json({"ok": True, "hint": problem.get("hint", "Hãy chia bài toán thành các bước nhỏ.")})





        if path == "/api/health":





            return self._json({"ok": True, "service": "Study-Coach", "version": "0.3.4"})





        if path == "/api/chatgpt":





            payload = dashboard_payload()





            return self._json({





                "course": {





                    "current_video_number": payload["meta"].get("current_video_number"),





                    "current_video_title": payload["meta"].get("current_video_title"),





                    "current_video_percent": payload["meta"].get("current_video_percent"),





                },





                "progress": payload["summary"],





                "recommendation": payload["recommendation"],





                "topics": payload["topics"],





                "recent_attempts": payload["recent"][:8],





            })





        if path == "/api/export":





            with db() as conn:





                return self._json(





                    {





                        "meta": get_meta(conn),





                        "attempts": [dict(r) for r in conn.execute("SELECT * FROM attempts ORDER BY id")],





                    }





                )





        if path == "/":





            self.path = "/index.html"





        return super().do_GET()





    def do_POST(self):





        path = urlparse(self.path).path





        try:





            data = self._read_json()





        except Exception as exc:





            return self._json({"ok": False, "error": f"JSON không hợp lệ: {exc}"}, 400)





        if path == "/api/judge":





            try:





                exercise_id = int(data.get("exercise_id"))





                code = str(data.get("code", ""))





                record = bool(data.get("record", False))





                hint_used = bool(data.get("hint_used", False))





                duration_sec = max(0, int(data.get("duration_sec", 0) or 0))





            except Exception:





                return self._json({"ok": False, "error": "Dữ liệu chấm bài không hợp lệ."}, 400)





            problem = get_problem(exercise_id)





            if not problem:





                return self._json({"ok": False, "error": "Bài này chưa có bộ chấm tự động."}, 404)





            result = judge_cpp(code, problem)





            payload = {"ok": True, "judge": result}





            if record:





                passed = bool(result.get("ok")) and bool(result.get("passed"))





                outcome = "hint" if passed and hint_used else "independent" if passed else "failed"





                compile_errors = 1 if result.get("stage") == "compile" else 0





                notes = "Auto judge: " + (





                    f"{result.get('passed_count', 0)}/{result.get('total_count', 0)} test passed"





                    if result.get("stage") == "run"





                    else result.get("stage", "unknown")





                )





                with db() as conn:





                    conn.execute(





                        "INSERT INTO attempts(exercise_id,outcome,duration_sec,compile_errors,notes,created_at) VALUES(?,?,?,?,?,?)",





                        (exercise_id, outcome, duration_sec, compile_errors, notes, utc_now()),





                    )





                    conn.execute(





                        "INSERT INTO meta(key,value) VALUES('active_exercise_id',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",





                        (str(exercise_id),),





                    )





                payload["recorded_outcome"] = outcome





                payload["dashboard"] = dashboard_payload()





            return self._json(payload)





        if path == "/api/source-result":
            try:
                exercise_id = data.get("exercise_id")
                # JSON booleans are not exercise identifiers.
                if type(exercise_id) is not int:
                    raise SourceProgressError("Mã bài phải là số nguyên từ 1 đến 300.")
                with db() as conn:
                    changed = record_source_ac(
                        conn, exercise_id, data.get("confirmed") is True,
                        lambda i: get_problem(i) is not None, utc_now,
                    )
            except SourceProgressError as exc:
                return self._json({"ok": False, "error": str(exc)}, 400)
            return self._json({
                "ok": True, "recorded": changed, "verification": "user_attested",
                "dashboard": dashboard_payload(),
            })
        if path == "/api/attempt":





            try:





                exercise_id = int(data.get("exercise_id"))





                outcome = str(data.get("outcome", ""))





                duration_sec = max(0, int(data.get("duration_sec", 0) or 0))





                compile_errors = max(0, int(data.get("compile_errors", 0) or 0))





                notes = str(data.get("notes", ""))[:1000]





            except Exception:





                return self._json({"ok": False, "error": "Dữ liệu bài làm không hợp lệ."}, 400)





            if not 1 <= exercise_id <= 300:





                return self._json({"ok": False, "error": "exercise_id phải từ 1 đến 300."}, 400)





            if outcome == "external_pass":
                return self._json({"ok": False, "error": "Dùng /api/source-result để xác nhận AC nguồn ngoài."}, 400)
            if outcome not in OUTCOME_SCORE:





                return self._json({"ok": False, "error": "outcome không hợp lệ."}, 400)





            with db() as conn:





                conn.execute(





                    "INSERT INTO attempts(exercise_id,outcome,duration_sec,compile_errors,notes,created_at) VALUES(?,?,?,?,?,?)",





                    (exercise_id, outcome, duration_sec, compile_errors, notes, utc_now()),





                )





                conn.execute(





                    "INSERT INTO meta(key,value) VALUES('active_exercise_id',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",





                    (str(exercise_id),),





                )





            return self._json({"ok": True, "dashboard": dashboard_payload()})





        if path == "/api/active":





            try:





                exercise_id = int(data.get("exercise_id"))





            except Exception:





                return self._json({"ok": False, "error": "exercise_id không hợp lệ."}, 400)





            if not 1 <= exercise_id <= 300:





                return self._json({"ok": False, "error": "exercise_id phải từ 1 đến 300."}, 400)





            with db() as conn:





                conn.execute(





                    "INSERT INTO meta(key,value) VALUES('active_exercise_id',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",





                    (str(exercise_id),),





                )





            return self._json({"ok": True, "dashboard": dashboard_payload()})





        if path == "/api/video":
            number = str(data.get("number", "")).strip()
            title = str(data.get("title", "")).strip()[:200]
            if not number:
                return self._json({"ok": False, "error": "Thiếu số video."}, 400)
            try:
                percent_value = int(data.get("percent", 0) or 0)
            except (TypeError, ValueError):
                return self._json({"ok": False, "error": "Phần trăm video phải là số từ 0 đến 100."}, 400)
            percent = str(max(0, min(100, percent_value)))
            with db() as conn:





                for key, value in (





                    ("current_video_number", number),





                    ("current_video_title", title),





                    ("current_video_percent", percent),





                ):





                    conn.execute(





                        "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",





                        (key, value),





                    )





            return self._json({"ok": True, "dashboard": dashboard_payload()})





        return self._json({"ok": False, "error": "Không tìm thấy API."}, 404)





def main() -> None:





    init_db()





    pid_file = DATA_DIR / "server.pid"





    pid_file.write_text(str(os.getpid()), encoding="utf-8")





    print(f"Study-Coach v0.3.2")





    print(f"Dashboard: http://{HOST}:{PORT}")





    print(f"Database: {DB_PATH}")





    server = ThreadingHTTPServer((HOST, PORT), Handler)





    try:





        server.serve_forever()





    except KeyboardInterrupt:





        pass





    finally:





        server.server_close()





        try:





            pid_file.unlink(missing_ok=True)





        except Exception:





            pass





if __name__ == "__main__":





    main()





