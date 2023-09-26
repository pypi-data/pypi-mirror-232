"""交易接口"""


from vxutils.importutils import vxAPIWrappers


class vxTdAPI(vxAPIWrappers):
    __defaults__ = {
        "hq": {"class": "vxquant.providers.tdx.TdxHQProvider", "params": {}},
        "order_volume": {},
        "get_positions": {},
        "get_orders": {},
        "get_trades": {},
        "get_accountinfo": {},
    }
