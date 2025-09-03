def filter_error(txt: str):
    txt = txt.lower()
    if 'Esta instrução é exclusiva para título registrado'.lower() in txt:
        return 'titulo ja baixado'
    else:
        return 'erro'

def message_return(status: str, message: str) -> dict[str, str]:
    return {'status': status, 'message': message}

class Elemento:
    id_iframe = '#idIframeAreaTransacional'
    id_btn_ok = 'input[name="botao.acao.ok"]'
    id_btn_nova = 'input[name="botao.acao.nova"]'
    id_btn_erro = 'input[name="botao.acao.retornaErro"]'

class Decimais:
    def __init__(self, value_in_real: int | float | str):
        if isinstance(value_in_real, str):
            if "," in value_in_real:
                value_in_real = value_in_real.replace(".", "").replace(",", ".")
            if "-" in value_in_real:
                value_in_real = "-" + value_in_real.replace("-", "")
            value_in_real = float(value_in_real)
            
        self._real = value_in_real
        self._cents = self._real_to_cent(value_in_real)
    
    def _real_to_cent(self, number: float | int) -> int:
        return int(f"{number:.2f}".replace(".", ""))
    
    def _cent_to_real(self, number: int) -> float:
        return number/100
    
    def __add__(self, other):
        if isinstance(other, Decimais):
            return Decimais(self._cent_to_real(self._cents + other._cents))
        return NotImplemented
    
    def __sub__(self, other):
        if isinstance(other, Decimais):
            return Decimais(self._cent_to_real(self._cents - other._cents))
        return NotImplemented
    
    def __mul__(self, other):
        if isinstance(other, Decimais):
            return Decimais(self._real * other._real)
        return NotImplemented
    
    def __truediv__(self, other):
        if isinstance(other, Decimais):
            return Decimais(f"{self._real / other._real:.2f}")
        return NotImplemented
    
    @property
    def real(self) -> float:
        return self._real
    
    @property
    def cent(self) -> int:
        return self._cents
    
    @property
    def text(self) -> str:
        return f"{self._real:,.2f}".replace(".", "___").replace(",", ".").replace("___", ",")
    
    def __repr__(self):
        return f"{self._real:,.2f}".replace(".", "___").replace(",", ".").replace("___", ",")
