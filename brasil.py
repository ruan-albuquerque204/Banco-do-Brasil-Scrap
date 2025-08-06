from threading import Thread
from datetime import datetime
from typing import Union, Mapping
from time import sleep

from playwright.sync_api import sync_playwright, Frame, Request

from decimais import Decimais

class Brasil:
    def __init__(self, user: str, password: str):
        self.logged = False
        self.p_context = sync_playwright()
        self._user = user
        self._password = password
        self._timer_observer = None
    
    def _refresh_session(self, request: Request):
        print('requeste')
        if request.url.endswith('modal-renovacao-sessao/modal-renovacao-sessao.html'):
            self._page.locator('.modal-renovacao-sessao-botao-primario').click()
        # modal-renovacao-sessao-botao modal-renovacao-sessao-botao-primario
        pass
    
    # def _refresh_session_two(self):
    #     while True:
    #         try:
    #             self._page.locator('.modal-renovacao-sessao-botao-primario').click()
    #             print('renovado')
    #         except:
    #             sleep(1)
        
    # def verify_timer(self):
    #     if not self.logged: return
    #     timer_text = self._page.locator('#token-time').inner_text()
    #     minutes = int(timer_text.split(' ')[1].split(':')[0])
        
    #     if minutes <= 5:
    #         self.close()
    #         self.login()
    
    def __enter__(self, *args):
        self.login()
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def login(self):
        # Cria uma nova página
        self._playwright = self.p_context.start()
        self._browser = self._playwright.chromium.launch(headless=False)
        self._page = self._browser.new_page()
        # if not self._timer_observer:
        #     self._timer_observer = Thread(target=self._refresh_session_two, name='timer observer', daemon=True)
        #     self._timer_observer.start()
        
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
        
        frame.locator('#dependenciaOrigem').fill('16047')
        frame.locator('#numeroContratoOrigem').fill('110000')
        
        # preechendo nosso número e valor do título
        frame.locator('input[name="nossoNumero"]').fill(key)
        
        # Botão de confirmar
        frame.locator(Elemento.id_btn_ok).click()
        
        btn_error = frame.locator(Elemento.id_btn_erro)
        content_page = frame.locator('.tabelaTrsResposta tbody tr')
        
        while btn_error.count() == 0 and content_page.count() == 0:
            sleep(0.1)
        
        if btn_error.count() > 0:
            btn_error.click()
            print('Erro ao tentar utilizar o banco')
            return
        
        dados = {}
        
        content_page = frame.locator('.tabelaTrsResposta tbody tr').all_inner_texts()
        
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
        
        frame.locator('#dependenciaOrigem').fill('16047')
        frame.locator('#numeroContratoOrigem').fill('110000')
        
        # preechendo nosso número e valor do título
        frame.locator('input[name="nossoNumero"]').press_sequentially(key)
        frame.locator('input[name="valorTitulo"]').press_sequentially(value)
        
        # Botão de confirmar
        frame.locator(Elemento.id_btn_ok).click()
        
        btn_nova = frame.locator(Elemento.id_btn_nova)
        btn_voltar = frame.locator(Elemento.id_btn_erro)
        
        while True:
            if btn_nova.count() > 0:
                btn_nova.click()
                return True
            elif btn_voltar.count() > 0:
                btn_voltar.click()
                return False
            sleep(1)

    def decount_boleto(self, key: str, value: Union[float, int, str], disc_value: Union[float, int, str]):
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
            # self._log(chave=chave, valor_boleto=valor_boleto, valor_credito=valor_credito, operacao="Abatimento", retorno=mensagem_retorno)
            frame.locator(Elemento.id_btn_nova).click()
            return
        
        frame.locator('#span1').click()
        frame.locator('#tr41 td a').click()
        
        frame.locator('#valorAbatimento').fill('15,15')
        frame.locator(Elemento.id_btn_ok).click()
        frame.locator(Elemento.id_btn_nova).click()
        pass
        
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
# https://autoatendimento.bb.com.br/apf-apj-autoatendimento/src/shared/directives/modal-renovacao-sessao/modal-renovacao-sessao.html
# https://eni.bb.com.br/eni1/matomo.php?e_c=MODAL_RENOVACAO_SESSAO&e_a=SISTEMA&e_n=MODAL_RENOVACAO_SESSAO%7C%7CEXIBIR&idsite=23&rec=1&r=487075&h=15&m=24&s=23&url=https%3A%2F%2Fautoatendimento.bb.com.br%2FWEB-INF%2Fjsp%2Fcobranca%2FHI05%2FHI05e.jsp&urlref=https%3A%2F%2Fautoatendimento.bb.com.br%2Fapf-apj-autoatendimento%2Findex.html%3Fv%3D3.9.4&uid=481958799&_id=02cf48e6edf5d378&_idts=1754417412&_idvc=1&_idn=0&_refts=0&_viewts=1754417412&send_image=1&pdf=1&qt=0&realp=0&wma=0&dir=0&fla=0&java=0&gears=0&ag=0&cookie=1&res=1280x720&_cvar=%7B%221%22%3A%5B%22IdServidorCliente%22%2C%22pxl1apj2b817_apj-aapj-4%22%5D%7D&gt_ms=132&pv_id=FcCRco
# https://gru-col.eum-appdynamics.com/eumcollector/beacons/browser/v2/GR-AAB-CCB/adrum
# modal-renovacao-sessao-botao modal-renovacao-sessao-botao-primario