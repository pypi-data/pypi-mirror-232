# coding: UTF-8
import sys
bstack1l11lll_opy_ = sys.version_info [0] == 2
bstack1l1l1ll_opy_ = 2048
bstack1lll111_opy_ = 7
def bstack1l1l11l_opy_ (bstack1llll1l_opy_):
    global bstack1l11l_opy_
    bstack111l1ll_opy_ = ord (bstack1llll1l_opy_ [-1])
    bstack1111l11_opy_ = bstack1llll1l_opy_ [:-1]
    bstack11lll11_opy_ = bstack111l1ll_opy_ % len (bstack1111l11_opy_)
    bstack1llll1_opy_ = bstack1111l11_opy_ [:bstack11lll11_opy_] + bstack1111l11_opy_ [bstack11lll11_opy_:]
    if bstack1l11lll_opy_:
        bstack1l1l1l_opy_ = unicode () .join ([unichr (ord (char) - bstack1l1l1ll_opy_ - (bstack1ll1lll_opy_ + bstack111l1ll_opy_) % bstack1lll111_opy_) for bstack1ll1lll_opy_, char in enumerate (bstack1llll1_opy_)])
    else:
        bstack1l1l1l_opy_ = str () .join ([chr (ord (char) - bstack1l1l1ll_opy_ - (bstack1ll1lll_opy_ + bstack111l1ll_opy_) % bstack1lll111_opy_) for bstack1ll1lll_opy_, char in enumerate (bstack1llll1_opy_)])
    return eval (bstack1l1l1l_opy_)
import os
from urllib.parse import urlparse
from bstack_utils.messages import bstack1l1lll111l_opy_
def bstack1l1ll11lll_opy_(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
def bstack1l1ll1l1ll_opy_(bstack1l1ll1l111_opy_, bstack1l1ll1l1l1_opy_):
    from pypac import get_pac
    from pypac import PACSession
    from pypac.parser import PACFile
    import socket
    if os.path.isfile(bstack1l1ll1l111_opy_):
        with open(bstack1l1ll1l111_opy_) as f:
            pac = PACFile(f.read())
    elif bstack1l1ll11lll_opy_(bstack1l1ll1l111_opy_):
        pac = get_pac(url=bstack1l1ll1l111_opy_)
    else:
        raise Exception(bstack1l1l11l_opy_ (u"࠭ࡐࡢࡥࠣࡪ࡮ࡲࡥࠡࡦࡲࡩࡸࠦ࡮ࡰࡶࠣࡩࡽ࡯ࡳࡵ࠼ࠣࡿࢂ࠭࿷").format(bstack1l1ll1l111_opy_))
    session = PACSession(pac)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((bstack1l1l11l_opy_ (u"ࠢ࠹࠰࠻࠲࠽࠴࠸ࠣ࿸"), 80))
        bstack1l1ll1ll11_opy_ = s.getsockname()[0]
        s.close()
    except:
        bstack1l1ll1ll11_opy_ = bstack1l1l11l_opy_ (u"ࠨ࠲࠱࠴࠳࠶࠮࠱ࠩ࿹")
    proxy_url = session.get_pac().find_proxy_for_url(bstack1l1ll1l1l1_opy_, bstack1l1ll1ll11_opy_)
    return proxy_url
def bstack111llllll_opy_(config):
    return bstack1l1l11l_opy_ (u"ࠩ࡫ࡸࡹࡶࡐࡳࡱࡻࡽࠬ࿺") in config or bstack1l1l11l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࡒࡵࡳࡽࡿࠧ࿻") in config
def bstack1ll11l1l_opy_(config):
    if not bstack111llllll_opy_(config):
        return
    if config.get(bstack1l1l11l_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧ࿼")):
        return config.get(bstack1l1l11l_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨ࿽"))
    if config.get(bstack1l1l11l_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ࿾")):
        return config.get(bstack1l1l11l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫ࿿"))
def bstack1l1l1111_opy_(config, bstack1l1ll1l1l1_opy_):
    proxy = bstack1ll11l1l_opy_(config)
    proxies = {}
    if config.get(bstack1l1l11l_opy_ (u"ࠨࡪࡷࡸࡵࡖࡲࡰࡺࡼࠫက")) or config.get(bstack1l1l11l_opy_ (u"ࠩ࡫ࡸࡹࡶࡳࡑࡴࡲࡼࡾ࠭ခ")):
        if proxy.endswith(bstack1l1l11l_opy_ (u"ࠪ࠲ࡵࡧࡣࠨဂ")):
            proxies = bstack111ll111l_opy_(proxy, bstack1l1ll1l1l1_opy_)
        else:
            proxies = {
                bstack1l1l11l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࠪဃ"): proxy
            }
    return proxies
def bstack111ll111l_opy_(bstack1l1ll1l111_opy_, bstack1l1ll1l1l1_opy_):
    proxies = {}
    global bstack1l1ll1l11l_opy_
    if bstack1l1l11l_opy_ (u"ࠬࡖࡁࡄࡡࡓࡖࡔ࡞࡙ࠨင") in globals():
        return bstack1l1ll1l11l_opy_
    try:
        proxy = bstack1l1ll1l1ll_opy_(bstack1l1ll1l111_opy_, bstack1l1ll1l1l1_opy_)
        if bstack1l1l11l_opy_ (u"ࠨࡄࡊࡔࡈࡇ࡙ࠨစ") in proxy:
            proxies = {}
        elif bstack1l1l11l_opy_ (u"ࠢࡉࡖࡗࡔࠧဆ") in proxy or bstack1l1l11l_opy_ (u"ࠣࡊࡗࡘࡕ࡙ࠢဇ") in proxy or bstack1l1l11l_opy_ (u"ࠤࡖࡓࡈࡑࡓࠣဈ") in proxy:
            bstack1l1ll11ll1_opy_ = proxy.split(bstack1l1l11l_opy_ (u"ࠥࠤࠧဉ"))
            if bstack1l1l11l_opy_ (u"ࠦ࠿࠵࠯ࠣည") in bstack1l1l11l_opy_ (u"ࠧࠨဋ").join(bstack1l1ll11ll1_opy_[1:]):
                proxies = {
                    bstack1l1l11l_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬဌ"): bstack1l1l11l_opy_ (u"ࠢࠣဍ").join(bstack1l1ll11ll1_opy_[1:])
                }
            else:
                proxies = {
                    bstack1l1l11l_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧဎ"): str(bstack1l1ll11ll1_opy_[0]).lower() + bstack1l1l11l_opy_ (u"ࠤ࠽࠳࠴ࠨဏ") + bstack1l1l11l_opy_ (u"ࠥࠦတ").join(bstack1l1ll11ll1_opy_[1:])
                }
        elif bstack1l1l11l_opy_ (u"ࠦࡕࡘࡏ࡙࡛ࠥထ") in proxy:
            bstack1l1ll11ll1_opy_ = proxy.split(bstack1l1l11l_opy_ (u"ࠧࠦࠢဒ"))
            if bstack1l1l11l_opy_ (u"ࠨ࠺࠰࠱ࠥဓ") in bstack1l1l11l_opy_ (u"ࠢࠣန").join(bstack1l1ll11ll1_opy_[1:]):
                proxies = {
                    bstack1l1l11l_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧပ"): bstack1l1l11l_opy_ (u"ࠤࠥဖ").join(bstack1l1ll11ll1_opy_[1:])
                }
            else:
                proxies = {
                    bstack1l1l11l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩဗ"): bstack1l1l11l_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧဘ") + bstack1l1l11l_opy_ (u"ࠧࠨမ").join(bstack1l1ll11ll1_opy_[1:])
                }
        else:
            proxies = {
                bstack1l1l11l_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬယ"): proxy
            }
    except Exception as e:
        print(bstack1l1l11l_opy_ (u"ࠢࡴࡱࡰࡩࠥ࡫ࡲࡳࡱࡵࠦရ"), bstack1l1lll111l_opy_.format(bstack1l1ll1l111_opy_, str(e)))
    bstack1l1ll1l11l_opy_ = proxies
    return proxies