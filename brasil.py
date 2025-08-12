import re
from datetime import datetime
from typing import Union, Mapping
from time import sleep

from playwright.sync_api import sync_playwright, Request

class Brasil:
    def __init__(self, user: str, password: str):
        self.logged = False
        self.p_context = sync_playwright()
        self._user = user
        self._password = password
    
    def _refresh_session(self, request: Request):
        if 'MODAL_RENOVACAO_SESSAO' in request.url:
            try:
                self._page.locator('.modal-renovacao-sessao-botao-primario').click()
            except:
                pass
        pass
        
    def __enter__(self):
        self.login()
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def login(self):
        # Cria uma nova página
        self._playwright = self.p_context.start()
        self._browser = self._playwright.chromium.launch(headless=False)
        self._page = self._browser.new_page()
        
        # Cria um Listener que verifica quando renovar a sessão
        self._page.on("request", self._refresh_session)
        self._page.goto("https://autoatendimento.bb.com.br/apf-apj-autoatendimento/")
        
        # Insere as informações do usuário
        self._page.locator('#identificador').fill(self._user)
        self._page.locator('#senhaChaveJ').fill(self._password)
        self._page.locator('#submit').click()
        
        try:
            # Aguarda até 30 segundos para o carregamento da página
            self._page.wait_for_selector(Elemento.id_iframe)
        except:
            raise Exception(self._page.locator('.conteudo').inner_text(timeout=15000))
        
        self.url_base = self._page.url
        self.url_base = self.url_base[:self.url_base.find('~2')]
        
        self.logged = True

    def consult_boleto(self, key: str, reset: bool = True) -> Mapping[str, Union[str, float, datetime]]:
        if not key:
            self.close('key cannot be empity')
        elif not self.logged:
            # Garante que o login será feio
            # Mesmo que não explicitamente
            self.login()
        
        # Monta o caminho da url
        # Caso seja atualizado a versão do site
        # O programa não irá quebrar
        endpoint = self.url_base + '~2Fcobranca~2Fconsultas.bb'
        
        self._page.goto(endpoint)
            
        # Garante que a página será carregada
        self._page.wait_for_selector(Elemento.id_iframe)
        frame = self._page.frame_locator(Elemento.id_iframe)
        
        frame.locator('select[name="tipoConsulta"]').select_option('HC07')
        
        
        agenc_inp = frame.locator('#dependenciaOrigem')
        btn_error = frame.locator(Elemento.id_btn_erro)
        content_page = frame.locator('.tabelaTrsResposta tbody tr')
        
        while True:
            while btn_error.count() == 0 and content_page.count() == 0 and agenc_inp.count() == 0:
                sleep(0.1)
            
            if agenc_inp.count() > 0:
                agenc_inp.fill('16047')
                frame.locator('#numeroContratoOrigem').fill('110000')
                # preechendo nosso número e valor do título
                frame.locator('input[name="nossoNumero"]').fill(key)
                # Botão de confirmar
                frame.locator(Elemento.id_btn_ok).click()
            elif btn_error.count() > 0:
                btn_error.click()
                print('Erro ao tentar utilizar o banco')
                return
            elif content_page.count() > 5 and agenc_inp.count() == 0:
                break
        
        dados = {}
        
        content_page = content_page.all_inner_texts()
        
        dados = dict(
            codigo = content_page[1].split('\t')[1].lower(),
            nome = content_page[2].split('\t')[1].lower(),
            endereco = content_page[3].split('\t')[1].lower(),
            cidade = content_page[4].split('\t')[1].lower(),
            cep = content_page[5].split('\t')[1].lower(),
            nosso_numero = content_page[9].split('\t')[1].lower(),
            status = content_page[10].split('\t')[1].lower(),
            modalidade = content_page[16].split('\t')[1].lower(),
            data_vencimento = content_page[17].split('\t')[1].lower(),
            data_entrada = content_page[18].split('\t')[1].lower(),
            data_emissao = content_page[19].split('\t')[1].lower(),
            valor_abatido = content_page[25].split('\t')[1].lower().replace('r$ ', ''),
            valor_titulo = content_page[26].split('\t')[1].lower().replace('r$ ', '')
        )
        
        if reset:
            frame.locator(Elemento.id_btn_nova).click()
        
        return dados
            
    def void_boleto(self, key: str, value: Union[float, int, str]):
        if not key or not value: # Verifica se a chave ou o valor não são compos vazios
            self.close('key and value cannot be empity')
        elif not self.logged: # Realiza o login caso o mesmo não tenha sido feito
            self.login()

        if isinstance(value, (int, float)): value = Decimais(value).text
        
        url = self.url_base + '~2Fcobranca~2FHI27.bb%3Fh=sim'
        
        self._page.goto(url)
        
        self._page.wait_for_selector(Elemento.id_iframe)
        frame = self._page.frame_locator(Elemento.id_iframe)
        
        agenc_inp = frame.locator('#dependenciaOrigem')
        btn_nova = frame.locator(Elemento.id_btn_nova)
        btn_voltar = frame.locator(Elemento.id_btn_erro)
        
        while True:
            while btn_nova.count() == 0 and btn_voltar.count() == 0 and agenc_inp.count() == 0:
                sleep(0.1)

            if agenc_inp.count() > 0:
                agenc_inp.fill('16047')
                frame.locator('#numeroContratoOrigem').fill('110000')
                
                frame.locator('input[name="nossoNumero"]').fill(key)
                frame.locator('input[name="valorTitulo"]').fill(value)

                frame.locator(Elemento.id_btn_ok).click()
            elif btn_nova.count() > 0:
                btn_nova.click()
                return True
            elif btn_voltar.count() > 0:
                btn_voltar.click()
                return False

    def descount_boleto(self, key: str, value: Union[float, int, str], disc_value: Union[float, int, str]) -> bool:
        data = self.consult_boleto(key, False)
        
        if isinstance(value, (int, float)): value = Decimais(value).text
        if isinstance(disc_value, (int, float)): disc_value = Decimais(disc_value).text
        
        frame = self._page.frame_locator(Elemento.id_iframe)
        reset = False
        
        if data['status'] != "normal":
            mensagem_retorno = f"Boleto {data['status']}"
            print(mensagem_retorno)
            reset = True
        elif data['valor_titulo'] != value:
            mensagem_retorno = f"Valor informado: {value} | Valor localizado: {data['valor_titulo']}"
            print(mensagem_retorno)
            reset = True
            
        if reset:
            frame.locator(Elemento.id_btn_nova).click()
            frame.locator('select[name="tipoConsulta"]').select_option('HC07')
            return False
        
        key_span = frame.locator('#span1')
        while key_span.count() > 0:
            key_span.click()
            frame.locator('#tr41 td a').click()
        
        abat_inp = frame.locator('#valorAbatimento')
        btn_new = frame.locator(Elemento.id_btn_nova)
        while True:
            while abat_inp.count() == 0 and btn_new.count() == 0:
                sleep(0.1)
            
            if btn_new.count() > 0:
                btn_new.click()
                break
            elif abat_inp.count() > 0:
                frame.locator('#valorTitulo').fill(value)
                abat_inp.fill(disc_value)
                frame.locator(Elemento.id_btn_ok).click()
                
            
        frame.locator('select[name="tipoConsulta"]').select_option('HC07')
        return True
        
    def close(self, raise_exception: Union[str, None] = None):
        if not self.logged:
            if raise_exception: raise Exception(raise_exception)
            return
        
        self._page.locator('.btn-logout').click()
        self.logged = False
        sleep(5)
        
        self._playwright = None
        self._browser.close()
        self._page.close()
        
        if raise_exception:
            raise Exception(raise_exception)

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
