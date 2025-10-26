import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ByapiClient:
    """
    Byapi API客户端类，用于简化API调用。
    """
    
    def __init__(self):
        """
        初始化ByapiClient实例，从环境变量中获取licence。
        """
        self.licence = os.getenv('BYAPI_LICENCE')
        if not self.licence:
            raise ValueError("未找到BYAPI_LICENCE环境变量，请在.env文件中设置。")
    
    def _make_request(self, url_template, **kwargs):
        """
        发起API请求的通用方法。
        
        :param url_template: API URL模板
        :param kwargs: URL中的占位符参数
        :return: API响应的JSON数据
        """
        # 替换URL模板中的占位符
        url = url_template.replace('biyinglicence', self.licence)
        for key, value in kwargs.items():
            url = url.replace(f'{{{key}}}', str(value))
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hslt_list(self):
        """
        获取hslt列表。
        
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hslt/list/biyinglicence"
        return self._make_request(url_template)
    
    def get_hslt_new(self):
        """
        获取最新的hslt数据。
        
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hslt/new/biyinglicence"
        return self._make_request(url_template)
    
    def get_hszg_list(self):
        """
        获取hszg列表。
        
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hszg/list/biyinglicence"
        return self._make_request(url_template)
    
    def get_hszg_gg(self, code):
        """
        获取指数、行业、概念代码相关数据。
        
        :param code: 指数、行业、概念代码
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hszg/gg/{code}/biyinglicence"
        return self._make_request(url_template, code=code)
    
    def get_hszg_zg(self, stock_code):
        """
        获取股票代码相关数据。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hszg/zg/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hslt_ztgc(self, date):
        """
        获取指定日期的ztgc数据。
        
        :param date: 日期(如2020-01-15)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hslt/ztgc/{date}/biyinglicence"
        return self._make_request(url_template, date=date)
    
    def get_hslt_dtgc(self, date):
        """
        获取指定日期的dtgc数据。
        
        :param date: 日期(如2020-01-15)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hslt/dtgc/{date}/biyinglicence"
        return self._make_request(url_template, date=date)
    
    def get_hslt_qsgc(self, date):
        """
        获取指定日期的qsgc数据。
        
        :param date: 日期(如2020-01-15)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hslt/qsgc/{date}/biyinglicence"
        return self._make_request(url_template, date=date)
    
    def get_hslt_cxgc(self, date):
        """
        获取指定日期的cxgc数据。
        
        :param date: 日期(如2020-01-15)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hslt/cxgc/{date}/biyinglicence"
        return self._make_request(url_template, date=date)
    
    def get_hslt_zbgc(self, date):
        """
        获取指定日期的zbgc数据。
        
        :param date: 日期(如2020-01-15)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hslt/zbgc/{date}/biyinglicence"
        return self._make_request(url_template, date=date)
    
    def get_hscp_gsjj(self, stock_code):
        """
        获取股票公司简介。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/gsjj/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_sszs(self, stock_code):
        """
        获取股票所属指数。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/sszs/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_ljgg(self, stock_code):
        """
        获取股票最近公告。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/ljgg/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_ljds(self, stock_code):
        """
        获取股票最近大事。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/ljds/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_ljjj(self, stock_code):
        """
        获取股票最近基金。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/ljjj/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_jnfh(self, stock_code):
        """
        获取股票近年分红。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/jnfh/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_jnzf(self, stock_code):
        """
        获取股票近年增发。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/jnzf/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_jjxs(self, stock_code):
        """
        获取股票基金销售。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/jjxs/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_jdlr(self, stock_code):
        """
        获取股票季度利润。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/jdlr/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_jdxj(self, stock_code):
        """
        获取股票季度现金。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/jdxj/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_yjyg(self, stock_code):
        """
        获取股票业绩预告。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/yjyg/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_cwzb(self, stock_code):
        """
        获取股票财务指标。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/cwzb/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_sdgd(self, stock_code):
        """
        获取股票十大股东。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/sdgd/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_ltgd(self, stock_code):
        """
        获取股票流通股东。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/ltgd/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_gdbh(self, stock_code):
        """
        获取股票股东变化。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/gdbh/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hscp_jjcg(self, stock_code):
        """
        获取股票基金持股。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hscp/jjcg/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hsrl_ssjy(self, stock_code):
        """
        获取股票实时交易。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsrl/ssjy/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hsrl_zbjy(self, stock_code):
        """
        获取股票逐笔交易。
        
        :param stock_code: 股票代码(如000001)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsrl/zbjy/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hsstock_real_time(self, stock_code):
        """
        获取股票实时行情。
        
        :param stock_code: 股票代码
        :return: API响应的JSON数据
        """
        url_template = "https://api.biyingapi.com/hsstock/real/time/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hsstock_real_five(self, stock_code):
        """
        获取股票五档行情。
        
        :param stock_code: 股票代码
        :return: API响应的JSON数据
        """
        url_template = "https://api.biyingapi.com/hsstock/real/five/{stock_code}/biyinglicence"
        return self._make_request(url_template, stock_code=stock_code)
    
    def get_hsrl_ssjy_more(self, stock_codes):
        """
        获取多个股票实时交易。
        
        :param stock_codes: 股票代码列表，用逗号分隔(如000001,000002)
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsrl/ssjy_more/biyinglicence?stock_codes={stock_codes}"
        return self._make_request(url_template, stock_codes=stock_codes)
    
    def get_hsstock_history_transaction(self, stock_code, st=None, et=None, lt=None):
        """
        获取股票历史交易数据。
        
        :param stock_code: 股票代码(如000001)
        :param st: 开始时间
        :param et: 结束时间
        :param lt: 最新条数
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/history/transaction/{stock_code}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code}', str(stock_code))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_latest(self, stock_code_market, frequency='d', adjust='n', lt=None):
        """
        获取股票最新数据。
        
        :param stock_code_market: 股票代码.市场（如000001.SZ）
        :param frequency: 分时级别(如d)
        :param adjust: 除权方式
        :param lt: 最新条数
        :return: API响应的JSON数据
        """
        url_template = "https://api.biyingapi.com/hsstock/latest/{stock_code_market}/{frequency}/{adjust}/biyinglicence"
        params = {}
        if lt:
            params['lt'] = lt
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market)).replace('{frequency}', str(frequency)).replace('{adjust}', str(adjust))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_history(self, stock_code_market, frequency='d', adjust='n', st=None, et=None, lt=None):
        """
        获取股票历史数据。
        
        :param stock_code_market: 股票代码.市场（如000001.SZ）
        :param frequency: 分时级别(如d)
        :param adjust: 除权方式
        :param st: 开始时间(如20240601)
        :param et: 结束时间(如20250430)
        :param lt: 最新条数(如100)
        :return: API响应的JSON数据
        """
        url_template = "https://api.biyingapi.com/hsstock/history/{stock_code_market}/{frequency}/{adjust}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market)).replace('{frequency}', str(frequency)).replace('{adjust}', str(adjust))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_stopprice_history(self, stock_code_market, st=None, et=None):
        """
        获取股票停牌历史数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/stopprice/history/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_indicators(self, stock_code_market, st=None, et=None):
        """
        获取股票指标数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/indicators/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_instrument(self, stock_code_market):
        """
        获取股票基础信息。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/instrument/{stock_code_market}/biyinglicence"
        return self._make_request(url_template, stock_code_market=stock_code_market)
    
    def get_hsstock_financial_balance(self, stock_code_market, st=None, et=None):
        """
        获取股票资产负债表数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/financial/balance/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_financial_income(self, stock_code_market, st=None, et=None):
        """
        获取股票利润表数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/financial/income/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_financial_cashflow(self, stock_code_market, st=None, et=None):
        """
        获取股票现金流量表数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/financial/cashflow/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_financial_pershareindex(self, stock_code_market, st=None, et=None):
        """
        获取股票每股指标数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/financial/pershareindex/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_financial_capital(self, stock_code_market, st=None, et=None):
        """
        获取股票资本结构数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/financial/capital/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_financial_topholder(self, stock_code_market, st=None, et=None):
        """
        获取股票十大股东数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/financial/topholder/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_financial_flowholder(self, stock_code_market, st=None, et=None):
        """
        获取股票流通股东数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/financial/flowholder/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_financial_hm(self, stock_code_market, st=None, et=None):
        """
        获取股票行业市值数据。
        
        :param stock_code_market: 股票代码（如000001.SZ）
        :param st: 开始时间
        :param et: 结束时间
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/financial/hm/{stock_code_market}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_history_macd(self, stock_code_market, frequency='d', adjust='n', st=None, et=None, lt=None):
        """
        获取股票MACD历史数据。
        
        :param stock_code_market: 股票代码(如000001.SZ)
        :param frequency: 分时级别(如d)
        :param adjust: 除权类型(如n)
        :param st: 开始时间
        :param et: 结束时间
        :param lt: 最新条数
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/history/macd/{stock_code_market}/{frequency}/{adjust}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market)).replace('{frequency}', str(frequency)).replace('{adjust}', str(adjust))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_history_ma(self, stock_code_market, frequency='d', adjust='n', st=None, et=None, lt=None):
        """
        获取股票MA历史数据。
        
        :param stock_code_market: 股票代码(如000001.SZ)
        :param frequency: 分时级别(如d)
        :param adjust: 除权类型(如n)
        :param st: 开始时间
        :param et: 结束时间
        :param lt: 最新条数
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/history/ma/{stock_code_market}/{frequency}/{adjust}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market)).replace('{frequency}', str(frequency)).replace('{adjust}', str(adjust))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_history_boll(self, stock_code_market, frequency='d', adjust='n', st=None, et=None, lt=None):
        """
        获取股票BOLL历史数据。
        
        :param stock_code_market: 股票代码(如000001.SZ)
        :param frequency: 分时级别(如d)
        :param adjust: 除权类型(如n)
        :param st: 开始时间
        :param et: 结束时间
        :param lt: 最新条数
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/history/boll/{stock_code_market}/{frequency}/{adjust}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market)).replace('{frequency}', str(frequency)).replace('{adjust}', str(adjust))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    def get_hsstock_history_kdj(self, stock_code_market, frequency='d', adjust='n', st=None, et=None, lt=None):
        """
        获取股票KDJ历史数据。
        
        :param stock_code_market: 股票代码(如000001.SZ)
        :param frequency: 分时级别(如d)
        :param adjust: 除权类型(如n)
        :param st: 开始时间
        :param et: 结束时间
        :param lt: 最新条数
        :return: API响应的JSON数据
        """
        url_template = "http://api.biyingapi.com/hsstock/history/kdj/{stock_code_market}/{frequency}/{adjust}/biyinglicence"
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
            
        try:
            url = url_template.replace('biyinglicence', self.licence).replace('{stock_code_market}', str(stock_code_market)).replace('{frequency}', str(frequency)).replace('{adjust}', str(adjust))
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None