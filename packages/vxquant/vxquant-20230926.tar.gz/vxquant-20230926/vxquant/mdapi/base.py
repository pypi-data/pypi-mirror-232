"""行情接口"""


from vxutils.importutils import vxAPIWrappers


class vxMdAPI(vxAPIWrappers):
    __defaults__ = {
        "calendar": {
            "class": "vxquant.providers.spiders.CNCalenderProvider",
            "params": {},
        },
        "hq": {"class": "vxquant.providers.tdx.TdxHQProvider", "params": {}},
    }


if __name__ == "__main__":
    mdapi = vxMdAPI()
    print(mdapi.hq("SHSE.600000"))
