from __future__ import annotations

import math
from source_catalog import SOURCE_TITLES, source_problem_url

CPP_STARTER = """#include <iostream>
#include <cmath>
#include <string>
#include <vector>

using namespace std;

int main() {
    // Viết code của bạn ở đây

    return 0;
}
"""

def T(inp: str, out: str) -> dict:
    return {"input": inp, "output": out}

def P(exercise_id: int, statement: str, input_desc: str, output_desc: str, tests: list[dict], hint: str = "") -> dict:
    return {
        "id": exercise_id,
        "title": SOURCE_TITLES[exercise_id - 1],
        "statement": statement,
        "input": input_desc,
        "output": output_desc,
        "tests": tests,
        "hint": hint,
        "starter": CPP_STARTER,
        "source_url": source_problem_url(exercise_id),
        "source_mode": "source-aligned-local-judge",
    }

def fmt2(x: float) -> str:
    return f"{x:.2f}\n"

def fmt3(x: float) -> str:
    return f"{x:.3f}\n"

def fmt4(x: float) -> str:
    return f"{x:.4f}"

def fmt5(x: float) -> str:
    return f"{x:.5f}\n"

def fmt6(x: float) -> str:
    return f"{x:.6f}\n"

PROBLEMS: dict[int, dict] = {}

# 001
PROBLEMS[1] = P(
    1,
    "Nhập một số nguyên A và tính A + 2025.",
    "Một số nguyên A.",
    "In giá trị A + 2025.",
    [T("10\n", "2035\n"), T("0\n", "2025\n"), T("-2025\n", "0\n"), T("999999\n", "1002024\n")],
    "Đọc A rồi in A + 2025.",
)

# 002
PROBLEMS[2] = P(
    2,
    "Nhập một số nguyên A và tính A - 2.",
    "Một số nguyên A.",
    "In giá trị A - 2.",
    [T("10\n", "8\n"), T("2\n", "0\n"), T("0\n", "-2\n"), T("-8\n", "-10\n")],
    "Chỉ cần một phép trừ.",
)

# 003
PROBLEMS[3] = P(
    3,
    "Nhập một số nguyên A và tính A nhân 3.",
    "Một số nguyên A.",
    "In giá trị A * 3.",
    [T("7\n", "21\n"), T("0\n", "0\n"), T("-5\n", "-15\n"), T("123456\n", "370368\n")],
    "Dùng toán tử *.",
)

# 004
PROBLEMS[4] = P(
    4,
    "Nhập số nguyên A, tính A chia 3 và in kết quả với đúng 2 chữ số sau dấu thập phân.",
    "Một số nguyên A.",
    "Một số thực A/3, định dạng 2 chữ số thập phân.",
    [T("10\n", "3.33\n"), T("6\n", "2.00\n"), T("1\n", "0.33\n"), T("-8\n", "-2.67\n")],
    "Ép sang double rồi dùng fixed << setprecision(2).",
)

# 005
PROBLEMS[5] = P(
    5,
    "Nhập số nguyên A. In A² ở dòng đầu và A⁵ ở dòng thứ hai.",
    "Một số nguyên A.",
    "Dòng 1 là A², dòng 2 là A⁵.",
    [T("2\n", "4\n32\n"), T("3\n", "9\n243\n"), T("-2\n", "4\n-32\n"), T("10\n", "100\n100000\n")],
    "Có thể nhân trực tiếp hoặc dùng lũy thừa số nguyên.",
)

# 006
PROBLEMS[6] = P(
    6,
    "Nhập số không âm A và tính căn bậc hai của A, in với 2 chữ số sau dấu thập phân.",
    "Một số nguyên A >= 0.",
    "sqrt(A) với 2 chữ số thập phân.",
    [T("9\n", "3.00\n"), T("2\n", "1.41\n"), T("0\n", "0.00\n"), T("144\n", "12.00\n")],
    "Dùng sqrt và setprecision(2).",
)

# 007
PROBLEMS[7] = P(
    7,
    "Nhập số A khác 0 và tính nghịch đảo 1/A, in với 5 chữ số sau dấu thập phân.",
    "Một số nguyên A, A != 0.",
    "1/A với 5 chữ số thập phân.",
    [T("2\n", "0.50000\n"), T("4\n", "0.25000\n"), T("-5\n", "-0.20000\n"), T("3\n", "0.33333\n")],
    "Dùng double và fixed << setprecision(5).",
)

# 008
def out8(a: int, b: int) -> str:
    x1 = 21 * a + 5 * b - 2009
    x2 = (21 * a * a - 5 * b) / (2009 * b * b)
    x3 = (21 * a + 5 * b * b) / (2009 * b + 15)
    return f"{x1} {x2:.4f}\n{x3:.6f}\n"

PROBLEMS[8] = P(
    8,
    "Nhập hai số nguyên a và b. Tính ba biểu thức theo công thức của bài; hai giá trị đầu nằm trên cùng một dòng, giá trị thứ ba ở dòng kế tiếp.",
    "Hai dòng lần lượt chứa a và b. Chọn b khác 0.",
    "Dòng 1: 21a + 5b - 2009 và (21a² - 5b)/(2009b²), giá trị thứ hai có 4 chữ số thập phân. Dòng 2: (21a + 5b²)/(2009b + 15), có 6 chữ số thập phân.",
    [T("1\n1\n", out8(1, 1)), T("2\n3\n", out8(2, 3)), T("-2\n4\n", out8(-2, 4)), T("10\n2\n", out8(10, 2))],
    "Tách từng biểu thức ra biến double để dễ kiểm tra.",
)

# 009
def out9(a: int, b: int, c: int) -> str:
    x1 = (21 * a * a + 5 * b * b) / (2009 * c * c + 15)
    x2 = math.sqrt(a * a - 2 * b) / (3 * c * c + 4)
    return f"{x1:.4f} {x2:.4f}\n"

PROBLEMS[9] = P(
    9,
    "Nhập a, b, c và tính hai biểu thức số thực của bài.",
    "Ba số nguyên a b c trên một dòng, với a² - 2b >= 0.",
    "In hai giá trị, mỗi giá trị có 4 chữ số sau dấu thập phân.",
    [T("5 2 1\n", out9(5, 2, 1)), T("10 3 2\n", out9(10, 3, 2)), T("4 0 3\n", out9(4, 0, 3)), T("20 5 1\n", out9(20, 5, 1))],
    "Giá trị thứ hai có căn sqrt(a*a - 2*b).",
)

# 010
PROBLEMS[10] = P(
    10,
    "Nhập hai số nguyên dương a, b. In thương nguyên và phần dư của a chia b.",
    "Hai số nguyên dương a b, b > 0.",
    "Hai số: a / b theo phép chia nguyên và a % b.",
    [T("10 3\n", "3 1\n"), T("20 5\n", "4 0\n"), T("7 9\n", "0 7\n"), T("1000000000000 7\n", "142857142857 1\n")],
    "Dùng / và % với kiểu số nguyên.",
)

# 011
PROBLEMS[11] = P(
    11,
    "Có a quả táo chia đều cho b bạn. Hãy in số táo mỗi bạn nhận được và số táo còn dư.",
    "Hai số nguyên dương a b.",
    "Hai số: a/b nguyên và a%b.",
    [T("10 3\n", "3 1\n"), T("12 4\n", "3 0\n"), T("2 5\n", "0 2\n"), T("101 10\n", "10 1\n")],
    "Bài này cũng dùng chia nguyên và chia lấy dư.",
)

# 012
PROBLEMS[12] = P(
    12,
    "Nhập một số có đúng 2 chữ số và in chữ số hàng đơn vị trước, hàng chục sau.",
    "Một số nguyên dương gồm 2 chữ số.",
    "Hai chữ số theo thứ tự: hàng đơn vị, hàng chục.",
    [T("42\n", "2 4\n"), T("10\n", "0 1\n"), T("99\n", "9 9\n"), T("73\n", "3 7\n")],
    "Có thể dùng / và % hoặc đọc dưới dạng chuỗi.",
)

# 013
def digit_sum(n: str) -> int:
    return sum(int(ch) for ch in n if ch.isdigit())

PROBLEMS[13] = P(
    13,
    "Nhập một số nguyên không âm và tính tổng các chữ số.",
    "Một số nguyên không âm.",
    "Tổng các chữ số.",
    [T("12345\n", "15\n"), T("0\n", "0\n"), T("9005\n", "14\n"), T("1111111111\n", "10\n")],
    "Lặp qua từng chữ số hoặc dùng % 10.",
)

# 014
PROBLEMS[14] = P(
    14,
    "Nhập hai số nguyên không âm a, b và tính tổng chữ số hàng đơn vị của chúng.",
    "Hai số nguyên a b.",
    "a%10 + b%10.",
    [T("123 456\n", "9\n"), T("10 20\n", "0\n"), T("999 111\n", "10\n"), T("7 8\n", "15\n")],
    "Lấy chữ số cuối bằng % 10.",
)

# 015
PROBLEMS[15] = P(
    15,
    "Nhập hai số nguyên không âm a, b. Tính chữ số hàng đơn vị của a cộng với chữ số hàng chục của b.",
    "Hai số nguyên a b; b có ít nhất 2 chữ số.",
    "a%10 + (b/10)%10.",
    [T("123 456\n", "8\n"), T("10 20\n", "2\n"), T("999 111\n", "10\n"), T("7 83\n", "15\n")],
    "Hàng chục của b là (b / 10) % 10.",
)

# 016
PROBLEMS[16] = P(
    16,
    "Đổi số tiền n theo tờ 5000: in số tờ 5000 lấy được và số tiền còn lại.",
    "Một số nguyên không âm n.",
    "Hai số: n/5000 và n%5000.",
    [T("12000\n", "2 2000\n"), T("5000\n", "1 0\n"), T("4999\n", "0 4999\n"), T("123456\n", "24 3456\n")],
    "Dùng chia nguyên và lấy dư với 5000.",
)

# 017
def money17(n: int) -> str:
    a = n // 5000
    n %= 5000
    b = n // 2000
    n %= 2000
    c = n // 1000
    return f"{a} {b} {c}\n"

PROBLEMS[17] = P(
    17,
    "Đổi số tiền n thành số tờ 5000, 2000 và 1000 theo thứ tự ưu tiên từ mệnh giá lớn xuống nhỏ.",
    "Một số nguyên không âm n.",
    "Ba số: số tờ 5000, 2000, 1000.",
    [T("12000\n", money17(12000)), T("8000\n", money17(8000)), T("500\n", money17(500)), T("23600\n", money17(23600))],
    "Sau mỗi mệnh giá, cập nhật phần tiền còn lại bằng %.",
)

# 018
def time18(n: int) -> str:
    h = n // 3600
    n %= 3600
    m = n // 60
    s = n % 60
    return f"{h}:{m}:{s}\n"

PROBLEMS[18] = P(
    18,
    "Nhập tổng số giây n, đổi thành giờ:phút:giây.",
    "Một số nguyên không âm n.",
    "In theo dạng h:m:s, không bắt buộc thêm số 0 ở đầu.",
    [T("3661\n", time18(3661)), T("60\n", time18(60)), T("0\n", time18(0)), T("86399\n", time18(86399))],
    "1 giờ = 3600 giây, 1 phút = 60 giây.",
)

# 019
def desks(a: int, b: int, c: int) -> int:
    return (a + 1) // 2 + (b + 1) // 2 + (c + 1) // 2

PROBLEMS[19] = P(
    19,
    "Ba lớp có lần lượt a, b, c học sinh. Mỗi bàn ngồi tối đa 2 học sinh và không ghép học sinh giữa các lớp. Tính tổng số bàn tối thiểu.",
    "Ba số nguyên không âm a b c.",
    "Tổng ceil(a/2) + ceil(b/2) + ceil(c/2).",
    [T("20 21 22\n", f"{desks(20,21,22)}\n"), T("1 1 1\n", "3\n"), T("0 0 0\n", "0\n"), T("30 30 31\n", f"{desks(30,30,31)}\n")],
    "Với số nguyên dương x, ceil(x/2) = (x+1)/2 theo chia nguyên.",
)

# 020
PROBLEMS[20] = P(
    20,
    "Chia a đoạn mía cho b người: in số phần nguyên mỗi người nhận và phần còn dư.",
    "Hai dòng lần lượt chứa a và b, b > 0.",
    "Hai số: a/b nguyên và a%b.",
    [T("10\n3\n", "3 1\n"), T("20\n5\n", "4 0\n"), T("2\n7\n", "0 2\n"), T("101\n10\n", "10 1\n")],
    "Dùng / và % với kiểu nguyên.",
)

# 021
PROBLEMS[21] = P(
    21,
    "Nhập cạnh a của hình vuông. Tính chu vi và diện tích.",
    "Một số nguyên dương a.",
    "In chu vi và diện tích, cách nhau một khoảng trắng.",
    [T("5\n", "20 25\n"), T("1\n", "4 1\n"), T("10\n", "40 100\n"), T("123\n", "492 15129\n")],
    "Chu vi = 4a, diện tích = a².",
)

# 022
def circle22(r: float) -> str:
    return f"{2*r*3.14:.2f} {r*r*3.14:.2f}\n"

PROBLEMS[22] = P(
    22,
    "Nhập bán kính a của hình tròn. Dùng π = 3.14 để tính chu vi và diện tích.",
    "Một số thực không âm a.",
    "Chu vi và diện tích, mỗi số có 2 chữ số thập phân.",
    [T("1\n", circle22(1)), T("2\n", circle22(2)), T("10\n", circle22(10)), T("2.5\n", circle22(2.5))],
    "C = 2 * 3.14 * r; S = 3.14 * r * r.",
)

# 023
PROBLEMS[23] = P(
    23,
    "Nhập chiều dài a và chiều rộng b của hình chữ nhật. Tính chu vi và diện tích.",
    "Hai số nguyên dương a b.",
    "Chu vi và diện tích, cách nhau một khoảng trắng.",
    [T("5 3\n", "16 15\n"), T("1 1\n", "4 1\n"), T("10 2\n", "24 20\n"), T("7 9\n", "32 63\n")],
    "Chu vi = 2(a+b), diện tích = ab.",
)

# 024
PROBLEMS[24] = P(
    24,
    "Nhập đáy a và chiều cao b của tam giác. Tính diện tích tam giác.",
    "Hai số a b.",
    "Diện tích a*b/2 với 1 chữ số thập phân.",
    [T("4 3\n", "6.0\n"), T("5 3\n", "7.5\n"), T("10 2\n", "10.0\n"), T("1 1\n", "0.5\n")],
    "Dùng 0.5 * a * b và setprecision(1).",
)

# 025
def tri25(a: float, b: float, c: float) -> str:
    p = (a + b + c) / 2
    area = math.sqrt(p * (p-a) * (p-b) * (p-c))
    perimeter = a + b + c
    if float(perimeter).is_integer():
        first = str(int(perimeter))
    else:
        first = str(perimeter)
    return f"{first}\n{area:.3f}\n"

PROBLEMS[25] = P(
    25,
    "Nhập ba cạnh a, b, c của một tam giác. In chu vi rồi tính diện tích bằng công thức Heron.",
    "Ba số dương a b c tạo thành tam giác.",
    "Dòng 1 là chu vi. Dòng 2 là diện tích với 3 chữ số thập phân.",
    [T("3 4 5\n", tri25(3,4,5)), T("5 5 6\n", tri25(5,5,6)), T("2 3 4\n", tri25(2,3,4)), T("7 8 9\n", tri25(7,8,9))],
    "p = (a+b+c)/2, S = sqrt(p(p-a)(p-b)(p-c)).",
)

# 026
def circum26(a: float, b: float, c: float) -> str:
    p = (a + b + c) / 2
    area = math.sqrt(p * (p-a) * (p-b) * (p-c))
    r = a*b*c/(4*area)
    return f"{r:.3f}\n"

PROBLEMS[26] = P(
    26,
    "Nhập ba cạnh của tam giác và tính bán kính đường tròn ngoại tiếp.",
    "Ba số dương a b c tạo thành tam giác.",
    "R = abc/(4S), in với 3 chữ số thập phân.",
    [T("3 4 5\n", circum26(3,4,5)), T("5 5 6\n", circum26(5,5,6)), T("7 8 9\n", circum26(7,8,9)), T("6 8 10\n", circum26(6,8,10))],
    "Tính diện tích S bằng Heron trước.",
)

# 027
def avg27(a: float, b: float, c: float) -> str:
    return f"{(a+b+c)/3:.1f}\n"

PROBLEMS[27] = P(
    27,
    "Nhập ba số a, b, c và tính trung bình cộng.",
    "Ba dòng, mỗi dòng một số.",
    "Trung bình cộng với 1 chữ số thập phân.",
    [T("1\n2\n3\n", avg27(1,2,3)), T("10\n20\n30\n", avg27(10,20,30)), T("-1\n0\n1\n", avg27(-1,0,1)), T("2\n2\n3\n", avg27(2,2,3))],
    "Tổng ba số rồi chia cho 3.0.",
)

# 028
def score28(a: float, b: float, c: float) -> str:
    return f"{(2*a+2*b+c)/5:.1f}\n"

PROBLEMS[28] = P(
    28,
    "Nhập ba điểm a, b, c. Hai điểm đầu có hệ số 2, điểm cuối hệ số 1. Tính điểm trung bình có trọng số.",
    "Ba dòng, mỗi dòng một số thực.",
    "Giá trị (2a + 2b + c)/5 với 1 chữ số thập phân.",
    [T("8\n7\n9\n", score28(8,7,9)), T("10\n10\n10\n", score28(10,10,10)), T("5.5\n6.5\n7\n", score28(5.5,6.5,7)), T("0\n0\n10\n", score28(0,0,10))],
    "Nhớ chia cho tổng hệ số là 5.",
)

# 029
def area29(circumference: float) -> str:
    r = circumference / (2 * 3.14)
    area = r * r * 3.14
    return f"{area:.2f}\n"

PROBLEMS[29] = P(
    29,
    "Biết chu vi C của hình tròn, dùng π = 3.14 để tính diện tích.",
    "Một số thực C là chu vi hình tròn.",
    "Diện tích với 2 chữ số thập phân.",
    [T("6.28\n", area29(6.28)), T("31.4\n", area29(31.4)), T("12.56\n", area29(12.56)), T("3.14\n", area29(3.14))],
    "Từ C = 2πr suy ra r = C/(2π), sau đó S = πr².",
)

# 030
PROBLEMS[30] = P(
    30,
    "Biết chu vi a của hình vuông. Tính diện tích hình vuông.",
    "Một số nguyên dương a, chia hết cho 4.",
    "Diện tích hình vuông.",
    [T("20\n", "25\n"), T("4\n", "1\n"), T("40\n", "100\n"), T("100\n", "625\n")],
    "Cạnh = chu vi / 4.",
)

def get_problem(exercise_id: int):
    built_in = PROBLEMS.get(exercise_id)
    if built_in is not None:
        return built_in
    from judge_packs import approved_problem
    return approved_problem(exercise_id)

def public_problem(problem: dict):
    tests = problem.get("tests", [])
    visible = ([t for t in tests if t.get('origin') in ('official', 'demonstration')][:2] if any('origin' in t for t in tests) else tests[:2])
    return {
        "id": problem["id"],
        "title": problem["title"],
        "statement": problem["statement"],
        "input": problem["input"],
        "output": problem["output"],
        "samples": visible,
        "test_count": len(tests),
        "hidden_count": max(0, len(tests) - len(visible)),
        "starter": problem["starter"],
        "source_url": problem.get("source_url"),
        "source_mode": problem.get("source_mode"),
    }
