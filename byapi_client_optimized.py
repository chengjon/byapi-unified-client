import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any

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
        self.base_url = "http://api.biyingapi.com"
        self.https_base_url = "https://api.biyingapi.com"
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None, use_https: bool = False) -> Optional[Dict]:
        """
        发起API请求的通用方法。
        
        :param endpoint: API端点
        :param params: 查询参数
        :param use_https: 是否使用HTTPS
        :return: API响应的JSON数据
        """
        base_url = self.https_base_url if use_https else self.base_url
        url = f"{base_url}/{endpoint}/{self.licence}"
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except ValueError as e:
            print(f"响应解析失败: {e}")
            return None
    
    # hslt相关接口
    def get_hslt_list(self) -> Optional[Dict]:
        """获取hslt列表。"""
        return self._make_request("hslt/list")
    
    def get_hslt_new(self) -> Optional[Dict]:
        """获取最新的hslt数据。"""
        return self._make_request("hslt/new")
    
    def get_hslt_ztgc(self, date: str) -> Optional[Dict]:
        """获取指定日期的ztgc数据。"""
        return self._make_request("hslt/ztgc", {"date": date})
    
    def get_hslt_dtgc(self, date: str) -> Optional[Dict]:
        """获取指定日期的dtgc数据。"""
        return self._make_request("hslt/dtgc", {"date": date})
    
    def get_hslt_qsgc(self, date: str) -> Optional[Dict]:
        """获取指定日期的qsgc数据。"""
        return self._make_request("hslt/qsgc", {"date": date})
    
    def get_hslt_cxgc(self, date: str) -> Optional[Dict]:
        """获取指定日期的cxgc数据。"""
        return self._make_request("hslt/cxgc", {"date": date})
    
    def get_hslt_zbgc(self, date: str) -> Optional[Dict]:
        """获取指定日期的zbgc数据。"""
        return self._make_request("hslt/zbgc", {"date": date})
    
    # hszg相关接口
    def get_hszg_list(self) -> Optional[Dict]:
        """获取hszg列表。"""
        return self._make_request("hszg/list")
    
    def get_hszg_gg(self, code: str) -> Optional[Dict]:
        """获取指数、行业、概念代码相关数据。"""
        return self._make_request("hszg/gg", {"code": code})
    
    def get_hszg_zg(self, stock_code: str) -> Optional[Dict]:
        """获取股票代码相关数据。"""
        return self._make_request("hszg/zg", {"stock_code": stock_code})
    
    # hscp相关接口
    def get_hscp_gsjj(self, stock_code: str) -> Optional[Dict]:
        """获取股票公司简介。"""
        return self._make_request("hscp/gsjj", {"stock_code": stock_code})
    
    def get_hscp_sszs(self, stock_code: str) -> Optional[Dict]:
        """获取股票所属指数。"""
        return self._make_request("hscp/sszs", {"stock_code": stock_code})
    
    def get_hscp_ljgg(self, stock_code: str) -> Optional[Dict]:
        """获取股票最近公告。"""
        return self._make_request("hscp/ljgg", {"stock_code": stock_code})
    
    def get_hscp_ljds(self, stock_code: str) -> Optional[Dict]:
        """获取股票最近大事。"""
        return self._make_request("hscp/ljds", {"stock_code": stock_code})
    
    def get_hscp_ljjj(self, stock_code: str) -> Optional[Dict]:
        """获取股票最近基金。"""
        return self._make_request("hscp/ljjj", {"stock_code": stock_code})
    
    def get_hscp_jnfh(self, stock_code: str) -> Optional[Dict]:
        """获取股票近年分红。"""
        return self._make_request("hscp/jnfh", {"stock_code": stock_code})
    
    def get_hscp_jnzf(self, stock_code: str) -> Optional[Dict]:
        """获取股票近年增发。"""
        return self._make_request("hscp/jnzf", {"stock_code": stock_code})
    
    def get_hscp_jjxs(self, stock_code: str) -> Optional[Dict]:
        """获取股票基金销售。"""
        return self._make_request("hscp/jjxs", {"stock_code": stock_code})
    
    def get_hscp_jdlr(self, stock_code: str) -> Optional[Dict]:
        """获取股票季度利润。"""
        return self._make_request("hscp/jdlr", {"stock_code": stock_code})
    
    def get_hscp_jdxj(self, stock_code: str) -> Optional[Dict]:
        """获取股票季度现金。"""
        return self._make_request("hscp/jdxj", {"stock_code": stock_code})
    
    def get_hscp_yjyg(self, stock_code: str) -> Optional[Dict]:
        """获取股票业绩预告。"""
        return self._make_request("hscp/yjyg", {"stock_code": stock_code})
    
    def get_hscp_cwzb(self, stock_code: str) -> Optional[Dict]:
        """获取股票财务指标。"""
        return self._make_request("hscp/cwzb", {"stock_code": stock_code})
    
    def get_hscp_sdgd(self, stock_code: str) -> Optional[Dict]:
        """获取股票十大股东。"""
        return self._make_request("hscp/sdgd", {"stock_code": stock_code})
    
    def get_hscp_ltgd(self, stock_code: str) -> Optional[Dict]:
        """获取股票流通股东。"""
        return self._make_request("hscp/ltgd", {"stock_code": stock_code})
    
    def get_hscp_gdbh(self, stock_code: str) -> Optional[Dict]:
        """获取股票股东变化。"""
        return self._make_request("hscp/gdbh", {"stock_code": stock_code})
    
    def get_hscp_jjcg(self, stock_code: str) -> Optional[Dict]:
        """获取股票基金持股。"""
        return self._make_request("hscp/jjcg", {"stock_code": stock_code})
    
    # hsrl相关接口
    def get_hsrl_ssjy(self, stock_code: str) -> Optional[Dict]:
        """获取股票实时交易。"""
        return self._make_request("hsrl/ssjy", {"stock_code": stock_code})
    
    def get_hsrl_zbjy(self, stock_code: str) -> Optional[Dict]:
        """获取股票逐笔交易。"""
        return self._make_request("hsrl/zbjy", {"stock_code": stock_code})
    
    def get_hsrl_ssjy_more(self, stock_codes: str) -> Optional[Dict]:
        """获取多个股票实时交易。"""
        return self._make_request("hsrl/ssjy_more", {"stock_codes": stock_codes})
    
    # hsstock相关接口
    def get_hsstock_real_time(self, stock_code: str) -> Optional[Dict]:
        """获取股票实时行情。"""
        return self._make_request("hsstock/real/time", {"stock_code": stock_code}, use_https=True)
    
    def get_hsstock_real_five(self, stock_code: str) -> Optional[Dict]:
        """获取股票五档行情。"""
        return self._make_request("hsstock/real/five", {"stock_code": stock_code}, use_https=True)
    
    def get_hsstock_history_transaction(self, stock_code: str, st: Optional[str] = None, et: Optional[str] = None, lt: Optional[str] = None) -> Optional[Dict]:
        """获取股票历史交易数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
        return self._make_request("hsstock/history/transaction", {**params, "stock_code": stock_code})
    
    def get_hsstock_latest(self, stock_code_market: str, frequency: str = 'd', adjust: str = 'n', lt: Optional[str] = None) -> Optional[Dict]:
        """获取股票最新数据。"""
        params = {}
        if lt:
            params['lt'] = lt
        return self._make_request(f"hsstock/latest/{stock_code_market}/{frequency}/{adjust}", params, use_https=True)
    
    def get_hsstock_history(self, stock_code_market: str, frequency: str = 'd', adjust: str = 'n', st: Optional[str] = None, et: Optional[str] = None, lt: Optional[str] = None) -> Optional[Dict]:
        """获取股票历史数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
        return self._make_request(f"hsstock/history/{stock_code_market}/{frequency}/{adjust}", params, use_https=True)
    
    def get_hsstock_stopprice_history(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票停牌历史数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/stopprice/history", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_indicators(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票指标数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/indicators", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_instrument(self, stock_code_market: str) -> Optional[Dict]:
        """获取股票基础信息。"""
        return self._make_request("hsstock/instrument", {"stock_code_market": stock_code_market})
    
    def get_hsstock_financial_balance(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票资产负债表数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/financial/balance", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_financial_income(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票利润表数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/financial/income", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_financial_cashflow(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票现金流量表数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/financial/cashflow", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_financial_pershareindex(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票每股指标数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/financial/pershareindex", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_financial_capital(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票资本结构数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/financial/capital", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_financial_topholder(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票十大股东数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/financial/topholder", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_financial_flowholder(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票流通股东数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/financial/flowholder", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_financial_hm(self, stock_code_market: str, st: Optional[str] = None, et: Optional[str] = None) -> Optional[Dict]:
        """获取股票行业市值数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        return self._make_request("hsstock/financial/hm", {**params, "stock_code_market": stock_code_market})
    
    def get_hsstock_history_macd(self, stock_code_market: str, frequency: str = 'd', adjust: str = 'n', st: Optional[str] = None, et: Optional[str] = None, lt: Optional[str] = None) -> Optional[Dict]:
        """获取股票MACD历史数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
        return self._make_request(f"hsstock/history/macd/{stock_code_market}/{frequency}/{adjust}", params)
    
    def get_hsstock_history_ma(self, stock_code_market: str, frequency: str = 'd', adjust: str = 'n', st: Optional[str] = None, et: Optional[str] = None, lt: Optional[str] = None) -> Optional[Dict]:
        """获取股票MA历史数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
        return self._make_request(f"hsstock/history/ma/{stock_code_market}/{frequency}/{adjust}", params)
    
    def get_hsstock_history_boll(self, stock_code_market: str, frequency: str = 'd', adjust: str = 'n', st: Optional[str] = None, et: Optional[str] = None, lt: Optional[str] = None) -> Optional[Dict]:
        """获取股票BOLL历史数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
        return self._make_request(f"hsstock/history/boll/{stock_code_market}/{frequency}/{adjust}", params)
    
    def get_hsstock_history_kdj(self, stock_code_market: str, frequency: str = 'd', adjust: str = 'n', st: Optional[str] = None, et: Optional[str] = None, lt: Optional[str] = None) -> Optional[Dict]:
        """获取股票KDJ历史数据。"""
        params = {}
        if st:
            params['st'] = st
        if et:
            params['et'] = et
        if lt:
            params['lt'] = lt
        return self._make_request(f"hsstock/history/kdj/{stock_code_market}/{frequency}/{adjust}", params)