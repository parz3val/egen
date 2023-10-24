from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response, HTMLResponse
from starlette.routing import Route
import sympy
import random
import re


def generate_expression(depth, max_depth, allow_brackets=True):
    if depth > max_depth or not allow_brackets:
        return str(random.randint(1, 100))

    operator = random.choice(['+', '-', '*', '/'])
    if operator == '/':
        operand1 = generate_expression(depth + 1, max_depth, allow_brackets)
        operand2 = generate_expression(depth + 1, max_depth, allow_brackets)
        return f"({operand1} {operator} {operand2})"
    else:
        bracket_type = random.choice(['(', '[', '{'])
        close_bracket = {'(': ')', '[': ']', '{': '}'}[bracket_type]
        operand1 = generate_expression(depth + 1, max_depth, allow_brackets)
        operand2 = generate_expression(depth + 1, max_depth, allow_brackets)
        return f"{bracket_type}{operand1} {operator} {operand2}{close_bracket}"

def generate_full_expression():
    depth = 0
    max_depth = 3  # You can adjust the depth for the desired complexity
    expression = generate_expression(depth, max_depth, True)
    return expression

def convert_custom_to_standard(expression):
    expression = re.sub(r'{', '(', expression)
    expression = re.sub(r'}', ')', expression)
    expression = re.sub(r'\[', '(', expression)
    expression = re.sub(r'\]', ')', expression)
    return expression

async def homepage(request):
    expression  = generate_full_expression()
    question = f"<h2 style='color:red;'>Question: {expression} </h2>"
    expression = convert_custom_to_standard(expression)
    simple = sympy.sympify(expression)
    answer = f"<h2 style='color:green'>answer: {simple.evalf()} </h2>"
    return Response(f'{question} <br/><hr> {answer}', media_type='text/html') 

async def evaluate_expression(request):
    data = await request.form()
    expression_raw = data.get('expression', 0)
    expression = convert_custom_to_standard(expression_raw)
    try:
        simple = sympy.sympify(expression)
        answer = f"<h2 style='color:green'>answer: {simple.evalf()} </h2>"
        question = f"<h2 style='color:red'>question: {expression} </h2>"
        return HTMLResponse(content=f'{question} <br/><hr> {answer}')
    except Exception as e:
        return HTMLResponse(content=f"<h1 style='color:red'>Your equation is wrong</h1> <hr> <br> <h3> question: {expression_raw}")

async def solver_page(request):
    html_form = """
    <h1>Expression Solver</h1>
    <form method="POST" action="/evaluate_expression">
      <label for="expression">Enter an Expression:</label>
      <input type="text" id="expression" name="expression" required>
      <button type="submit">Submit</button>
    </form>
    """
    return HTMLResponse(content=html_form)

app = Starlette(debug=True, routes=[
    Route('/', homepage),
    Route('/solver', solver_page),
    Route('/evaluate_expression', evaluate_expression, methods=['POST', 'GET']),
])
