"""Restricted arithmetic AST -> SymPy, never eval arbitrary student Python.

Verifies only expression equality under explicitly listed conditions, not complete
proofs, inequality claims, geometry, or free-form natural-language reasoning.
"""
import ast
import re
from sympy import Integer, Rational, Symbol, simplify, symbols

x, y = symbols('x y', real=True)
SYMBOLS = {name:Symbol(name, real=True) for name in ('x','y','a','b','q','n','x0','y0')}


class UnsupportedMath(ValueError):
    pass


def _convert(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        if abs(node.value)>1000000:
            raise UnsupportedMath('Constant outside allowed range')
        return Integer(node.value)
    if isinstance(node, ast.Name) and node.id in SYMBOLS:
        return SYMBOLS[node.id]
    if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.UAdd,ast.USub):
        value=_convert(node.operand)
        return value if isinstance(node.op,ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left=_convert(node.left)
        if isinstance(node.op, ast.Pow):
            if not (isinstance(node.right,ast.Constant) and type(node.right.value) is int and 0<=node.right.value<=5):
                raise UnsupportedMath('Only literal powers 0-5 supported')
            return left**node.right.value
        right=_convert(node.right)
        if isinstance(node.op,ast.Add):return left+right
        if isinstance(node.op,ast.Sub):return left-right
        if isinstance(node.op,ast.Mult):return left*right
        if isinstance(node.op,ast.Div):
            if right==0:raise UnsupportedMath('Division by zero')
            return left/right
    raise UnsupportedMath('Unsupported expression syntax (no function calls/attributes)')


def parse_restricted(expr:str):
    if len(expr)>180 or not expr.strip():
        raise UnsupportedMath('Expression must have 1-180 characters')
    normalized=expr.replace('−','-').replace('²','**2').replace('³','**3').replace('×','*').replace('÷','/')
    if re.search(r'[^a-zA-Z0-9_+*/() \t\-]',normalized):
        raise UnsupportedMath('Unsupported symbols; write * for multiplication and ** for powers')
    try:tree=ast.parse(normalized,mode='eval')
    except SyntaxError as ex:raise UnsupportedMath('Invalid arithmetic syntax') from ex
    if len(list(ast.walk(tree)))>75:
        raise UnsupportedMath('Expression too complex')
    return _convert(tree.body)


def verify_equivalence(left:str,right:str,problem_id:str):
    try:
        a,b=parse_restricted(left),parse_restricted(right)
    except (UnsupportedMath, OverflowError, ZeroDivisionError) as ex:
        return {'status':'UNSUPPORTED','verified':False,'reason':str(ex),'tool':'RESTRICTED_AST_SYMPY'}
    # Only these known problem assumptions are proven by the curated problem card.
    if problem_id=='inequality-bridge':
        a,b=a.subs(SYMBOLS['y'],1-SYMBOLS['x']),b.subs(SYMBOLS['y'],1-SYMBOLS['x'])
        conditions=['x+y=1','x>0','y>0','原表达式的分母都非零']
    else:
        conditions=['所有参与计算的表达式有定义；未自动证明新引入的限制条件']
    try:residual=simplify(a-b)
    except (ValueError,ArithmeticError,TypeError) as ex:
        return {'status':'INDETERMINATE','verified':False,'reason':str(ex),'tool':'RESTRICTED_AST_SYMPY'}
    equivalent = residual == 0
    return {'status':'EQUIVALENT_ON_DOMAIN' if equivalent else 'NOT_EQUIVALENT_AS_IDENTITY',
            'verified':bool(equivalent),'reason':'在指定条件下代数式恒等' if equivalent else '在已知条件下没有得到恒等关系；不自动断言某一步具体错误',
            'conditions':conditions,'domain_not_fully_checked':True,'tool':'RESTRICTED_AST_SYMPY',
            'warning':'这是受限代数恒等检验，不验证完整证明、解题策略或不等式。'}


def known_identity_check(identity_id):
    if identity_id=='inequality-sum-to-product':
        output=verify_equivalence('1/x+1/y','1/(x*y)','inequality-bridge')
        return {'identity_id':identity_id,'valid_under_conditions':output['verified'],
                'conditions':output.get('conditions',[]),'tool':'SYMPY_CURATED_CHECK'}
    if identity_id=='ellipse-tangent-at-3-0':
        on_curve=simplify(Rational(3**2,9)+Rational(0,4)-1)==0
        return {'identity_id':identity_id,'valid_under_conditions':bool(on_curve),
                'conditions':['P=(3,0) 在曲线上','该点非奇异'],'tool':'SYMPY_CURATED_CHECK'}
    return None
