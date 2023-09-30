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
import atexit
import os
import signal
import sys
import yaml
import requests
import logging
import threading
import socket
import datetime
import string
import random
import json
import collections.abc
import re
import multiprocessing
import traceback
import copy
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
from bstack_utils.constants import *
def bstack1lll11l11_opy_():
  global CONFIG
  headers = {
        bstack1l1l11l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨࡵ"): bstack1l1l11l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ࡶ"),
      }
  proxies = bstack1l1l1111_opy_(CONFIG, bstack1lll11ll_opy_)
  try:
    response = requests.get(bstack1lll11ll_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack11l1l1l1l_opy_ = response.json()[bstack1l1l11l_opy_ (u"ࠫ࡭ࡻࡢࡴࠩࡷ")]
      logger.debug(bstack11l1lll1_opy_.format(response.json()))
      return bstack11l1l1l1l_opy_
    else:
      logger.debug(bstack11l1llll_opy_.format(bstack1l1l11l_opy_ (u"ࠧࡘࡥࡴࡲࡲࡲࡸ࡫ࠠࡋࡕࡒࡒࠥࡶࡡࡳࡵࡨࠤࡪࡸࡲࡰࡴࠣࠦࡸ")))
  except Exception as e:
    logger.debug(bstack11l1llll_opy_.format(e))
def bstack1l11lllll_opy_(hub_url):
  global CONFIG
  url = bstack1l1l11l_opy_ (u"ࠨࡨࡵࡶࡳࡷ࠿࠵࠯ࠣࡹ")+  hub_url + bstack1l1l11l_opy_ (u"ࠢ࠰ࡥ࡫ࡩࡨࡱࠢࡺ")
  headers = {
        bstack1l1l11l_opy_ (u"ࠨࡅࡲࡲࡹ࡫࡮ࡵ࠯ࡷࡽࡵ࡫ࠧࡻ"): bstack1l1l11l_opy_ (u"ࠩࡤࡴࡵࡲࡩࡤࡣࡷ࡭ࡴࡴ࠯࡫ࡵࡲࡲࠬࡼ"),
      }
  proxies = bstack1l1l1111_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack1ll111ll_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack1ll1l1llll_opy_.format(hub_url, e))
def bstack111l1111l_opy_():
  try:
    global bstack11ll11l1_opy_
    bstack11l1l1l1l_opy_ = bstack1lll11l11_opy_()
    bstack11lll1l1_opy_ = []
    results = []
    for bstack1l1ll1ll1_opy_ in bstack11l1l1l1l_opy_:
      bstack11lll1l1_opy_.append(bstack1lll1lll11_opy_(target=bstack1l11lllll_opy_,args=(bstack1l1ll1ll1_opy_,)))
    for t in bstack11lll1l1_opy_:
      t.start()
    for t in bstack11lll1l1_opy_:
      results.append(t.join())
    bstack11l11l1l1_opy_ = {}
    for item in results:
      hub_url = item[bstack1l1l11l_opy_ (u"ࠪ࡬ࡺࡨ࡟ࡶࡴ࡯ࠫࡽ")]
      latency = item[bstack1l1l11l_opy_ (u"ࠫࡱࡧࡴࡦࡰࡦࡽࠬࡾ")]
      bstack11l11l1l1_opy_[hub_url] = latency
    bstack11l11l11_opy_ = min(bstack11l11l1l1_opy_, key= lambda x: bstack11l11l1l1_opy_[x])
    bstack11ll11l1_opy_ = bstack11l11l11_opy_
    logger.debug(bstack1111llll1_opy_.format(bstack11l11l11_opy_))
  except Exception as e:
    logger.debug(bstack11llll111_opy_.format(e))
from bstack_utils.messages import *
from bstack_utils.config import Config
from bstack_utils.helper import bstack111111l1_opy_, bstack1lll111lll_opy_, bstack1lll1111l1_opy_
from bstack_utils.bstack1l1111lll_opy_ import bstack1llll1lll1_opy_
from bstack_utils.proxy import bstack111ll111l_opy_, bstack1l1l1111_opy_, bstack1ll11l1l_opy_, bstack111llllll_opy_
from browserstack_sdk.bstack1lll1111_opy_ import *
from browserstack_sdk.bstack111l111l_opy_ import *
bstack11llllll_opy_ = bstack1l1l11l_opy_ (u"ࠬࠦࠠ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱࡟ࡲࠥࠦࡩࡧࠪࡳࡥ࡬࡫ࠠ࠾࠿ࡀࠤࡻࡵࡩࡥࠢ࠳࠭ࠥࢁ࡜࡯ࠢࠣࠤࡹࡸࡹࡼ࡞ࡱࠤࡨࡵ࡮ࡴࡶࠣࡪࡸࠦ࠽ࠡࡴࡨࡵࡺ࡯ࡲࡦࠪ࡟ࠫ࡫ࡹ࡜ࠨࠫ࠾ࡠࡳࠦࠠࠡࠢࠣࡪࡸ࠴ࡡࡱࡲࡨࡲࡩࡌࡩ࡭ࡧࡖࡽࡳࡩࠨࡣࡵࡷࡥࡨࡱ࡟ࡱࡣࡷ࡬࠱ࠦࡊࡔࡑࡑ࠲ࡸࡺࡲࡪࡰࡪ࡭࡫ࡿࠨࡱࡡ࡬ࡲࡩ࡫ࡸࠪࠢ࠮ࠤࠧࡀࠢࠡ࠭ࠣࡎࡘࡕࡎ࠯ࡵࡷࡶ࡮ࡴࡧࡪࡨࡼࠬࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࠪࡤࡻࡦ࡯ࡴࠡࡰࡨࡻࡕࡧࡧࡦ࠴࠱ࡩࡻࡧ࡬ࡶࡣࡷࡩ࠭ࠨࠨࠪࠢࡀࡂࠥࢁࡽࠣ࠮ࠣࡠࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧ࡭ࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡆࡨࡸࡦ࡯࡬ࡴࠤࢀࡠࠬ࠯ࠩࠪ࡝ࠥ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩࠨ࡝ࠪࠢ࠮ࠤࠧ࠲࡜࡝ࡰࠥ࠭ࡡࡴࠠࠡࠢࠣࢁࡨࡧࡴࡤࡪࠫࡩࡽ࠯ࡻ࡝ࡰࠣࠤࠥࠦࡽ࡝ࡰࠣࠤࢂࡢ࡮ࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࠬࡿ")
bstack111l111l1_opy_ = bstack1l1l11l_opy_ (u"࠭࡜࡯࠱࠭ࠤࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽ࠡࠬ࠲ࡠࡳࡩ࡯࡯ࡵࡷࠤࡧࡹࡴࡢࡥ࡮ࡣࡵࡧࡴࡩࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸ࡣ࡜࡯ࡥࡲࡲࡸࡺࠠࡣࡵࡷࡥࡨࡱ࡟ࡤࡣࡳࡷࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࡡࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠲࡟࡟ࡲࡨࡵ࡮ࡴࡶࠣࡴࡤ࡯࡮ࡥࡧࡻࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠲࡞࡞ࡱࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡷࡱ࡯ࡣࡦࠪ࠳࠰ࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳ࠪ࡞ࡱࡧࡴࡴࡳࡵࠢ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱࠠ࠾ࠢࡵࡩࡶࡻࡩࡳࡧࠫࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣࠫ࠾ࡠࡳ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡲࡡࡶࡰࡦ࡬ࠥࡃࠠࡢࡵࡼࡲࡨࠦࠨ࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠩࠡ࠿ࡁࠤࢀࡢ࡮࡭ࡧࡷࠤࡨࡧࡰࡴ࠽࡟ࡲࡹࡸࡹࠡࡽ࡟ࡲࡨࡧࡰࡴࠢࡀࠤࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸ࠯࡜࡯ࠢࠣࢁࠥࡩࡡࡵࡥ࡫ࠬࡪࡾࠩࠡࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡲࡦࡶࡸࡶࡳࠦࡡࡸࡣ࡬ࡸࠥ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡩ࡯࡯ࡰࡨࡧࡹ࠮ࡻ࡝ࡰࠣࠤࠥࠦࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶ࠽ࠤࡥࡽࡳࡴ࠼࠲࠳ࡨࡪࡰ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡀࡥࡤࡴࡸࡃࠤࡼࡧࡱࡧࡴࡪࡥࡖࡔࡌࡇࡴࡳࡰࡰࡰࡨࡲࡹ࠮ࡊࡔࡑࡑ࠲ࡸࡺࡲࡪࡰࡪ࡭࡫ࡿࠨࡤࡣࡳࡷ࠮࠯ࡽࡡ࠮࡟ࡲࠥࠦࠠࠡ࠰࠱࠲ࡱࡧࡵ࡯ࡥ࡫ࡓࡵࡺࡩࡰࡰࡶࡠࡳࠦࠠࡾࠫ࡟ࡲࢂࡢ࡮࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱࡟ࡲࠬࢀ")
from ._version import __version__
bstack1llll111ll_opy_ = None
CONFIG = {}
bstack1llllllll_opy_ = {}
bstack111lll1ll_opy_ = {}
bstack111lll1l1_opy_ = None
bstack111ll1111_opy_ = None
bstack1l1lllll_opy_ = None
bstack1ll1llll1l_opy_ = -1
bstack11111ll1l_opy_ = bstack1l1l1ll1_opy_
bstack111l1l1ll_opy_ = 1
bstack1l111l11_opy_ = False
bstack1lll1l1lll_opy_ = False
bstack11l1l11l1_opy_ = bstack1l1l11l_opy_ (u"ࠧࠨࢁ")
bstack11l1ll111_opy_ = bstack1l1l11l_opy_ (u"ࠨࠩࢂ")
bstack11ll1ll1l_opy_ = False
bstack1ll1ll11l_opy_ = True
bstack111ll11l1_opy_ = bstack1l1l11l_opy_ (u"ࠩࠪࢃ")
bstack11ll1lll_opy_ = []
bstack11ll11l1_opy_ = bstack1l1l11l_opy_ (u"ࠪࠫࢄ")
bstack1l1ll1ll_opy_ = False
bstack11l1l1l11_opy_ = None
bstack1llllll1l_opy_ = None
bstack1llll11lll_opy_ = -1
bstack1llll11l1_opy_ = os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"ࠫࢃ࠭ࢅ")), bstack1l1l11l_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬࢆ"), bstack1l1l11l_opy_ (u"࠭࠮ࡳࡱࡥࡳࡹ࠳ࡲࡦࡲࡲࡶࡹ࠳ࡨࡦ࡮ࡳࡩࡷ࠴ࡪࡴࡱࡱࠫࢇ"))
bstack1ll11ll1_opy_ = []
bstack11l11l11l_opy_ = False
bstack11llll1l_opy_ = False
bstack1111l1ll_opy_ = None
bstack111ll11ll_opy_ = None
bstack11l11llll_opy_ = None
bstack11l1ll1ll_opy_ = None
bstack111ll111_opy_ = None
bstack1ll1lll11l_opy_ = None
bstack1l1lll111_opy_ = None
bstack1llll111_opy_ = None
bstack1l11l111l_opy_ = None
bstack1lll1l1l11_opy_ = None
bstack1ll1ll11_opy_ = None
bstack111ll1ll1_opy_ = None
bstack1ll1ll1l_opy_ = None
bstack1llll1ll11_opy_ = None
bstack1lll11l11l_opy_ = None
bstack11ll111l_opy_ = None
bstack1l11llll1_opy_ = None
bstack111ll1l1l_opy_ = None
bstack11l1l1111_opy_ = bstack1l1l11l_opy_ (u"ࠢࠣ࢈")
logger = logging.getLogger(__name__)
logging.basicConfig(level=bstack11111ll1l_opy_,
                    format=bstack1l1l11l_opy_ (u"ࠨ࡞ࡱࠩ࠭ࡧࡳࡤࡶ࡬ࡱࡪ࠯ࡳࠡ࡝ࠨࠬࡳࡧ࡭ࡦࠫࡶࡡࡠࠫࠨ࡭ࡧࡹࡩࡱࡴࡡ࡮ࡧࠬࡷࡢࠦ࠭ࠡࠧࠫࡱࡪࡹࡳࡢࡩࡨ࠭ࡸ࠭ࢉ"),
                    datefmt=bstack1l1l11l_opy_ (u"ࠩࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫࢊ"),
                    stream=sys.stdout)
bstack1l11l1ll1_opy_ = Config.get_instance()
def bstack1l11111l_opy_():
  global CONFIG
  global bstack11111ll1l_opy_
  if bstack1l1l11l_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬࢋ") in CONFIG:
    bstack11111ll1l_opy_ = bstack1ll11l1ll_opy_[CONFIG[bstack1l1l11l_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭ࢌ")]]
    logging.getLogger().setLevel(bstack11111ll1l_opy_)
def bstack1l1l1ll11_opy_():
  global CONFIG
  global bstack11l11l11l_opy_
  bstack111l11111_opy_ = bstack11l11l111_opy_(CONFIG)
  if (bstack1l1l11l_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧࢍ") in bstack111l11111_opy_ and str(bstack111l11111_opy_[bstack1l1l11l_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨࢎ")]).lower() == bstack1l1l11l_opy_ (u"ࠧࡵࡴࡸࡩࠬ࢏")):
    bstack11l11l11l_opy_ = True
def bstack1ll11l11l_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1111l1l1_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1l1l11l1l_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack1l1l11l_opy_ (u"ࠣ࠯࠰ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡥࡲࡲ࡫࡯ࡧࡧ࡫࡯ࡩࠧ࢐") == args[i].lower() or bstack1l1l11l_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡴࡦࡪࡩࠥ࢑") == args[i].lower():
      path = args[i + 1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack111ll11l1_opy_
      bstack111ll11l1_opy_ += bstack1l1l11l_opy_ (u"ࠪ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡇࡴࡴࡦࡪࡩࡉ࡭ࡱ࡫ࠠࠨ࢒") + path
      return path
  return None
bstack1lll1ll1ll_opy_ = re.compile(bstack1l1l11l_opy_ (u"ࡶࠧ࠴ࠪࡀ࡞ࠧࡿ࠭࠴ࠪࡀࠫࢀ࠲࠯ࡅࠢ࢓"))
def bstack1l1111ll_opy_(loader, node):
  value = loader.construct_scalar(node)
  for group in bstack1lll1ll1ll_opy_.findall(value):
    if group is not None and os.environ.get(group) is not None:
      value = value.replace(bstack1l1l11l_opy_ (u"ࠧࠪࡻࠣ࢔") + group + bstack1l1l11l_opy_ (u"ࠨࡽࠣ࢕"), os.environ.get(group))
  return value
def bstack1ll1l1l1l_opy_():
  bstack1ll111l1_opy_ = bstack1l1l11l1l_opy_()
  if bstack1ll111l1_opy_ and os.path.exists(os.path.abspath(bstack1ll111l1_opy_)):
    fileName = bstack1ll111l1_opy_
  if bstack1l1l11l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࡥࡆࡊࡎࡈࠫ࢖") in os.environ and os.path.exists(
          os.path.abspath(os.environ[bstack1l1l11l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬࢗ")])) and not bstack1l1l11l_opy_ (u"ࠩࡩ࡭ࡱ࡫ࡎࡢ࡯ࡨࠫ࢘") in locals():
    fileName = os.environ[bstack1l1l11l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡓࡓࡌࡉࡈࡡࡉࡍࡑࡋ࢙ࠧ")]
  if bstack1l1l11l_opy_ (u"ࠫ࡫࡯࡬ࡦࡐࡤࡱࡪ࢚࠭") in locals():
    bstack1l111ll_opy_ = os.path.abspath(fileName)
  else:
    bstack1l111ll_opy_ = bstack1l1l11l_opy_ (u"࢛ࠬ࠭")
  bstack111111lll_opy_ = os.getcwd()
  bstack111ll1l11_opy_ = bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩ࢜")
  bstack1l1l1llll_opy_ = bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹࡢ࡯࡯ࠫ࢝")
  while (not os.path.exists(bstack1l111ll_opy_)) and bstack111111lll_opy_ != bstack1l1l11l_opy_ (u"ࠣࠤ࢞"):
    bstack1l111ll_opy_ = os.path.join(bstack111111lll_opy_, bstack111ll1l11_opy_)
    if not os.path.exists(bstack1l111ll_opy_):
      bstack1l111ll_opy_ = os.path.join(bstack111111lll_opy_, bstack1l1l1llll_opy_)
    if bstack111111lll_opy_ != os.path.dirname(bstack111111lll_opy_):
      bstack111111lll_opy_ = os.path.dirname(bstack111111lll_opy_)
    else:
      bstack111111lll_opy_ = bstack1l1l11l_opy_ (u"ࠤࠥ࢟")
  if not os.path.exists(bstack1l111ll_opy_):
    bstack11llll11_opy_(
      bstack1l11ll11_opy_.format(os.getcwd()))
  try:
    with open(bstack1l111ll_opy_, bstack1l1l11l_opy_ (u"ࠪࡶࠬࢠ")) as stream:
      yaml.add_implicit_resolver(bstack1l1l11l_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧࢡ"), bstack1lll1ll1ll_opy_)
      yaml.add_constructor(bstack1l1l11l_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨࢢ"), bstack1l1111ll_opy_)
      config = yaml.load(stream, yaml.FullLoader)
      return config
  except:
    with open(bstack1l111ll_opy_, bstack1l1l11l_opy_ (u"࠭ࡲࠨࢣ")) as stream:
      try:
        config = yaml.safe_load(stream)
        return config
      except yaml.YAMLError as exc:
        bstack11llll11_opy_(bstack1lllll11l_opy_.format(str(exc)))
def bstack1111lll1_opy_(config):
  bstack1ll1lll111_opy_ = bstack1l111111_opy_(config)
  for option in list(bstack1ll1lll111_opy_):
    if option.lower() in bstack1lll11ll1_opy_ and option != bstack1lll11ll1_opy_[option.lower()]:
      bstack1ll1lll111_opy_[bstack1lll11ll1_opy_[option.lower()]] = bstack1ll1lll111_opy_[option]
      del bstack1ll1lll111_opy_[option]
  return config
def bstack1ll11llll_opy_():
  global bstack111lll1ll_opy_
  for key, bstack1l11111ll_opy_ in bstack111l11l1_opy_.items():
    if isinstance(bstack1l11111ll_opy_, list):
      for var in bstack1l11111ll_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack111lll1ll_opy_[key] = os.environ[var]
          break
    elif bstack1l11111ll_opy_ in os.environ and os.environ[bstack1l11111ll_opy_] and str(os.environ[bstack1l11111ll_opy_]).strip():
      bstack111lll1ll_opy_[key] = os.environ[bstack1l11111ll_opy_]
  if bstack1l1l11l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩࢤ") in os.environ:
    bstack111lll1ll_opy_[bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬࢥ")] = {}
    bstack111lll1ll_opy_[bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢦ")][bstack1l1l11l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࢧ")] = os.environ[bstack1l1l11l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ࢨ")]
def bstack11l1ll11_opy_():
  global bstack1llllllll_opy_
  global bstack111ll11l1_opy_
  for idx, val in enumerate(sys.argv):
    if idx < len(sys.argv) and bstack1l1l11l_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨࢩ").lower() == val.lower():
      bstack1llllllll_opy_[bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪࢪ")] = {}
      bstack1llllllll_opy_[bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫࢫ")][bstack1l1l11l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࢬ")] = sys.argv[idx + 1]
      del sys.argv[idx:idx + 2]
      break
  for key, bstack1l11lll1_opy_ in bstack1111lll11_opy_.items():
    if isinstance(bstack1l11lll1_opy_, list):
      for idx, val in enumerate(sys.argv):
        for var in bstack1l11lll1_opy_:
          if idx < len(sys.argv) and bstack1l1l11l_opy_ (u"ࠩ࠰࠱ࠬࢭ") + var.lower() == val.lower() and not key in bstack1llllllll_opy_:
            bstack1llllllll_opy_[key] = sys.argv[idx + 1]
            bstack111ll11l1_opy_ += bstack1l1l11l_opy_ (u"ࠪࠤ࠲࠳ࠧࢮ") + var + bstack1l1l11l_opy_ (u"ࠫࠥ࠭ࢯ") + sys.argv[idx + 1]
            del sys.argv[idx:idx + 2]
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx < len(sys.argv) and bstack1l1l11l_opy_ (u"ࠬ࠳࠭ࠨࢰ") + bstack1l11lll1_opy_.lower() == val.lower() and not key in bstack1llllllll_opy_:
          bstack1llllllll_opy_[key] = sys.argv[idx + 1]
          bstack111ll11l1_opy_ += bstack1l1l11l_opy_ (u"࠭ࠠ࠮࠯ࠪࢱ") + bstack1l11lll1_opy_ + bstack1l1l11l_opy_ (u"ࠧࠡࠩࢲ") + sys.argv[idx + 1]
          del sys.argv[idx:idx + 2]
def bstack11l1lll1l_opy_(config):
  bstack1l1l111l_opy_ = config.keys()
  for bstack1lll11l1l1_opy_, bstack11111lll1_opy_ in bstack1llllll11l_opy_.items():
    if bstack11111lll1_opy_ in bstack1l1l111l_opy_:
      config[bstack1lll11l1l1_opy_] = config[bstack11111lll1_opy_]
      del config[bstack11111lll1_opy_]
  for bstack1lll11l1l1_opy_, bstack11111lll1_opy_ in bstack1lll1l111l_opy_.items():
    if isinstance(bstack11111lll1_opy_, list):
      for bstack1111llll_opy_ in bstack11111lll1_opy_:
        if bstack1111llll_opy_ in bstack1l1l111l_opy_:
          config[bstack1lll11l1l1_opy_] = config[bstack1111llll_opy_]
          del config[bstack1111llll_opy_]
          break
    elif bstack11111lll1_opy_ in bstack1l1l111l_opy_:
      config[bstack1lll11l1l1_opy_] = config[bstack11111lll1_opy_]
      del config[bstack11111lll1_opy_]
  for bstack1111llll_opy_ in list(config):
    for bstack1111111l1_opy_ in bstack1lll1l11_opy_:
      if bstack1111llll_opy_.lower() == bstack1111111l1_opy_.lower() and bstack1111llll_opy_ != bstack1111111l1_opy_:
        config[bstack1111111l1_opy_] = config[bstack1111llll_opy_]
        del config[bstack1111llll_opy_]
  bstack1lll1ll1_opy_ = []
  if bstack1l1l11l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫࢳ") in config:
    bstack1lll1ll1_opy_ = config[bstack1l1l11l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬࢴ")]
  for platform in bstack1lll1ll1_opy_:
    for bstack1111llll_opy_ in list(platform):
      for bstack1111111l1_opy_ in bstack1lll1l11_opy_:
        if bstack1111llll_opy_.lower() == bstack1111111l1_opy_.lower() and bstack1111llll_opy_ != bstack1111111l1_opy_:
          platform[bstack1111111l1_opy_] = platform[bstack1111llll_opy_]
          del platform[bstack1111llll_opy_]
  for bstack1lll11l1l1_opy_, bstack11111lll1_opy_ in bstack1lll1l111l_opy_.items():
    for platform in bstack1lll1ll1_opy_:
      if isinstance(bstack11111lll1_opy_, list):
        for bstack1111llll_opy_ in bstack11111lll1_opy_:
          if bstack1111llll_opy_ in platform:
            platform[bstack1lll11l1l1_opy_] = platform[bstack1111llll_opy_]
            del platform[bstack1111llll_opy_]
            break
      elif bstack11111lll1_opy_ in platform:
        platform[bstack1lll11l1l1_opy_] = platform[bstack11111lll1_opy_]
        del platform[bstack11111lll1_opy_]
  for bstack111111l11_opy_ in bstack1lll1l11ll_opy_:
    if bstack111111l11_opy_ in config:
      if not bstack1lll1l11ll_opy_[bstack111111l11_opy_] in config:
        config[bstack1lll1l11ll_opy_[bstack111111l11_opy_]] = {}
      config[bstack1lll1l11ll_opy_[bstack111111l11_opy_]].update(config[bstack111111l11_opy_])
      del config[bstack111111l11_opy_]
  for platform in bstack1lll1ll1_opy_:
    for bstack111111l11_opy_ in bstack1lll1l11ll_opy_:
      if bstack111111l11_opy_ in list(platform):
        if not bstack1lll1l11ll_opy_[bstack111111l11_opy_] in platform:
          platform[bstack1lll1l11ll_opy_[bstack111111l11_opy_]] = {}
        platform[bstack1lll1l11ll_opy_[bstack111111l11_opy_]].update(platform[bstack111111l11_opy_])
        del platform[bstack111111l11_opy_]
  config = bstack1111lll1_opy_(config)
  return config
def bstack11lll11l_opy_(config):
  global bstack11l1ll111_opy_
  if bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧࢵ") in config and str(config[bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨࢶ")]).lower() != bstack1l1l11l_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫࢷ"):
    if not bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪࢸ") in config:
      config[bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫࢹ")] = {}
    if not bstack1l1l11l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࢺ") in config[bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢻ")]:
      bstack1lll111ll_opy_ = datetime.datetime.now()
      bstack1l1ll111_opy_ = bstack1lll111ll_opy_.strftime(bstack1l1l11l_opy_ (u"ࠪࠩࡩࡥࠥࡣࡡࠨࡌࠪࡓࠧࢼ"))
      hostname = socket.gethostname()
      bstack1l11l1l11_opy_ = bstack1l1l11l_opy_ (u"ࠫࠬࢽ").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack1l1l11l_opy_ (u"ࠬࢁࡽࡠࡽࢀࡣࢀࢃࠧࢾ").format(bstack1l1ll111_opy_, hostname, bstack1l11l1l11_opy_)
      config[bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪࢿ")][bstack1l1l11l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩࣀ")] = identifier
    bstack11l1ll111_opy_ = config[bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬࣁ")][bstack1l1l11l_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࣂ")]
  return config
def bstack11l11lll_opy_():
  if (
          isinstance(os.getenv(bstack1l1l11l_opy_ (u"ࠪࡎࡊࡔࡋࡊࡐࡖࡣ࡚ࡘࡌࠨࣃ")), str) and len(os.getenv(bstack1l1l11l_opy_ (u"ࠫࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍࠩࣄ"))) > 0
  ) or (
          isinstance(os.getenv(bstack1l1l11l_opy_ (u"ࠬࡐࡅࡏࡍࡌࡒࡘࡥࡈࡐࡏࡈࠫࣅ")), str) and len(os.getenv(bstack1l1l11l_opy_ (u"࠭ࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠬࣆ"))) > 0
  ):
    return os.getenv(bstack1l1l11l_opy_ (u"ࠧࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗ࠭ࣇ"), 0)
  if str(os.getenv(bstack1l1l11l_opy_ (u"ࠨࡅࡌࠫࣈ"))).lower() == bstack1l1l11l_opy_ (u"ࠩࡷࡶࡺ࡫ࠧࣉ") and str(os.getenv(bstack1l1l11l_opy_ (u"ࠪࡇࡎࡘࡃࡍࡇࡆࡍࠬ࣊"))).lower() == bstack1l1l11l_opy_ (u"ࠫࡹࡸࡵࡦࠩ࣋"):
    return os.getenv(bstack1l1l11l_opy_ (u"ࠬࡉࡉࡓࡅࡏࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࠨ࣌"), 0)
  if str(os.getenv(bstack1l1l11l_opy_ (u"࠭ࡃࡊࠩ࣍"))).lower() == bstack1l1l11l_opy_ (u"ࠧࡵࡴࡸࡩࠬ࣎") and str(os.getenv(bstack1l1l11l_opy_ (u"ࠨࡖࡕࡅ࡛ࡏࡓࠨ࣏"))).lower() == bstack1l1l11l_opy_ (u"ࠩࡷࡶࡺ࡫࣐ࠧ"):
    return os.getenv(bstack1l1l11l_opy_ (u"ࠪࡘࡗࡇࡖࡊࡕࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓ࣑ࠩ"), 0)
  if str(os.getenv(bstack1l1l11l_opy_ (u"ࠫࡈࡏ࣒ࠧ"))).lower() == bstack1l1l11l_opy_ (u"ࠬࡺࡲࡶࡧ࣓ࠪ") and str(os.getenv(bstack1l1l11l_opy_ (u"࠭ࡃࡊࡡࡑࡅࡒࡋࠧࣔ"))).lower() == bstack1l1l11l_opy_ (u"ࠧࡤࡱࡧࡩࡸ࡮ࡩࡱࠩࣕ"):
    return 0
  if os.getenv(bstack1l1l11l_opy_ (u"ࠨࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡇࡘࡁࡏࡅࡋࠫࣖ")) and os.getenv(bstack1l1l11l_opy_ (u"ࠩࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡉࡏࡎࡏࡌࡘࠬࣗ")):
    return os.getenv(bstack1l1l11l_opy_ (u"ࠪࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠬࣘ"), 0)
  if str(os.getenv(bstack1l1l11l_opy_ (u"ࠫࡈࡏࠧࣙ"))).lower() == bstack1l1l11l_opy_ (u"ࠬࡺࡲࡶࡧࠪࣚ") and str(os.getenv(bstack1l1l11l_opy_ (u"࠭ࡄࡓࡑࡑࡉࠬࣛ"))).lower() == bstack1l1l11l_opy_ (u"ࠧࡵࡴࡸࡩࠬࣜ"):
    return os.getenv(bstack1l1l11l_opy_ (u"ࠨࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗ࠭ࣝ"), 0)
  if str(os.getenv(bstack1l1l11l_opy_ (u"ࠩࡆࡍࠬࣞ"))).lower() == bstack1l1l11l_opy_ (u"ࠪࡸࡷࡻࡥࠨࣟ") and str(os.getenv(bstack1l1l11l_opy_ (u"ࠫࡘࡋࡍࡂࡒࡋࡓࡗࡋࠧ࣠"))).lower() == bstack1l1l11l_opy_ (u"ࠬࡺࡲࡶࡧࠪ࣡"):
    return os.getenv(bstack1l1l11l_opy_ (u"࠭ࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡍࡓࡇࡥࡉࡅࠩ࣢"), 0)
  if str(os.getenv(bstack1l1l11l_opy_ (u"ࠧࡄࡋࣣࠪ"))).lower() == bstack1l1l11l_opy_ (u"ࠨࡶࡵࡹࡪ࠭ࣤ") and str(os.getenv(bstack1l1l11l_opy_ (u"ࠩࡊࡍ࡙ࡒࡁࡃࡡࡆࡍࠬࣥ"))).lower() == bstack1l1l11l_opy_ (u"ࠪࡸࡷࡻࡥࠨࣦ"):
    return os.getenv(bstack1l1l11l_opy_ (u"ࠫࡈࡏ࡟ࡋࡑࡅࡣࡎࡊࠧࣧ"), 0)
  if str(os.getenv(bstack1l1l11l_opy_ (u"ࠬࡉࡉࠨࣨ"))).lower() == bstack1l1l11l_opy_ (u"࠭ࡴࡳࡷࡨࣩࠫ") and str(os.getenv(bstack1l1l11l_opy_ (u"ࠧࡃࡗࡌࡐࡉࡑࡉࡕࡇࠪ࣪"))).lower() == bstack1l1l11l_opy_ (u"ࠨࡶࡵࡹࡪ࠭࣫"):
    return os.getenv(bstack1l1l11l_opy_ (u"ࠩࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠫ࣬"), 0)
  if str(os.getenv(bstack1l1l11l_opy_ (u"ࠪࡘࡋࡥࡂࡖࡋࡏࡈ࣭ࠬ"))).lower() == bstack1l1l11l_opy_ (u"ࠫࡹࡸࡵࡦ࣮ࠩ"):
    return os.getenv(bstack1l1l11l_opy_ (u"ࠬࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈ࣯ࠬ"), 0)
  return -1
def bstack1lll1ll1l1_opy_(bstack1lllll11l1_opy_):
  global CONFIG
  if not bstack1l1l11l_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨࣰ") in CONFIG[bstack1l1l11l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࣱࠩ")]:
    return
  CONFIG[bstack1l1l11l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࣲࠪ")] = CONFIG[bstack1l1l11l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࣳ")].replace(
    bstack1l1l11l_opy_ (u"ࠪࠨࢀࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࢁࠬࣴ"),
    str(bstack1lllll11l1_opy_)
  )
def bstack11l11ll1l_opy_():
  global CONFIG
  if not bstack1l1l11l_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪࣵ") in CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࣶࠧ")]:
    return
  bstack1lll111ll_opy_ = datetime.datetime.now()
  bstack1l1ll111_opy_ = bstack1lll111ll_opy_.strftime(bstack1l1l11l_opy_ (u"࠭ࠥࡥ࠯ࠨࡦ࠲ࠫࡈ࠻ࠧࡐࠫࣷ"))
  CONFIG[bstack1l1l11l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩࣸ")] = CONFIG[bstack1l1l11l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࣹࠪ")].replace(
    bstack1l1l11l_opy_ (u"ࠩࠧࡿࡉࡇࡔࡆࡡࡗࡍࡒࡋࡽࠨࣺ"),
    bstack1l1ll111_opy_
  )
def bstack1ll11111l_opy_():
  global CONFIG
  if bstack1l1l11l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬࣻ") in CONFIG and not bool(CONFIG[bstack1l1l11l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ࣼ")]):
    del CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࣽ")]
    return
  if not bstack1l1l11l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨࣾ") in CONFIG:
    CONFIG[bstack1l1l11l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩࣿ")] = bstack1l1l11l_opy_ (u"ࠨࠥࠧࡿࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࢀࠫऀ")
  if bstack1l1l11l_opy_ (u"ࠩࠧࡿࡉࡇࡔࡆࡡࡗࡍࡒࡋࡽࠨँ") in CONFIG[bstack1l1l11l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬं")]:
    bstack11l11ll1l_opy_()
    os.environ[bstack1l1l11l_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨः")] = CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऄ")]
  if not bstack1l1l11l_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨअ") in CONFIG[bstack1l1l11l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩआ")]:
    return
  bstack1lllll11l1_opy_ = bstack1l1l11l_opy_ (u"ࠨࠩइ")
  bstack11l11lll1_opy_ = bstack11l11lll_opy_()
  if bstack11l11lll1_opy_ != -1:
    bstack1lllll11l1_opy_ = bstack1l1l11l_opy_ (u"ࠩࡆࡍࠥ࠭ई") + str(bstack11l11lll1_opy_)
  if bstack1lllll11l1_opy_ == bstack1l1l11l_opy_ (u"ࠪࠫउ"):
    bstack1ll1lll1ll_opy_ = bstack111111ll_opy_(CONFIG[bstack1l1l11l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧऊ")])
    if bstack1ll1lll1ll_opy_ != -1:
      bstack1lllll11l1_opy_ = str(bstack1ll1lll1ll_opy_)
  if bstack1lllll11l1_opy_:
    bstack1lll1ll1l1_opy_(bstack1lllll11l1_opy_)
    os.environ[bstack1l1l11l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩऋ")] = CONFIG[bstack1l1l11l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨऌ")]
def bstack1ll11l111_opy_(bstack111llll11_opy_, bstack11111ll11_opy_, path):
  bstack1ll1ll1l1_opy_ = {
    bstack1l1l11l_opy_ (u"ࠧࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫऍ"): bstack11111ll11_opy_
  }
  if os.path.exists(path):
    bstack1ll1lll1_opy_ = json.load(open(path, bstack1l1l11l_opy_ (u"ࠨࡴࡥࠫऎ")))
  else:
    bstack1ll1lll1_opy_ = {}
  bstack1ll1lll1_opy_[bstack111llll11_opy_] = bstack1ll1ll1l1_opy_
  with open(path, bstack1l1l11l_opy_ (u"ࠤࡺ࠯ࠧए")) as outfile:
    json.dump(bstack1ll1lll1_opy_, outfile)
def bstack111111ll_opy_(bstack111llll11_opy_):
  bstack111llll11_opy_ = str(bstack111llll11_opy_)
  bstack1ll1ll1ll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"ࠪࢂࠬऐ")), bstack1l1l11l_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫऑ"))
  try:
    if not os.path.exists(bstack1ll1ll1ll1_opy_):
      os.makedirs(bstack1ll1ll1ll1_opy_)
    file_path = os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"ࠬࢄࠧऒ")), bstack1l1l11l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ओ"), bstack1l1l11l_opy_ (u"ࠧ࠯ࡤࡸ࡭ࡱࡪ࠭࡯ࡣࡰࡩ࠲ࡩࡡࡤࡪࡨ࠲࡯ࡹ࡯࡯ࠩऔ"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack1l1l11l_opy_ (u"ࠨࡹࠪक")):
        pass
      with open(file_path, bstack1l1l11l_opy_ (u"ࠤࡺ࠯ࠧख")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack1l1l11l_opy_ (u"ࠪࡶࠬग")) as bstack1ll1ll1lll_opy_:
      bstack1lll1l1ll_opy_ = json.load(bstack1ll1ll1lll_opy_)
    if bstack111llll11_opy_ in bstack1lll1l1ll_opy_:
      bstack1l111ll11_opy_ = bstack1lll1l1ll_opy_[bstack111llll11_opy_][bstack1l1l11l_opy_ (u"ࠫ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨघ")]
      bstack1ll1l1lll1_opy_ = int(bstack1l111ll11_opy_) + 1
      bstack1ll11l111_opy_(bstack111llll11_opy_, bstack1ll1l1lll1_opy_, file_path)
      return bstack1ll1l1lll1_opy_
    else:
      bstack1ll11l111_opy_(bstack111llll11_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack1lll11llll_opy_.format(str(e)))
    return -1
def bstack1llllll111_opy_(config):
  if not config[bstack1l1l11l_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧङ")] or not config[bstack1l1l11l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩच")]:
    return True
  else:
    return False
def bstack1llll1111_opy_(config):
  if bstack1l1l11l_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭छ") in config:
    del (config[bstack1l1l11l_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧज")])
    return False
  if bstack1111l1l1_opy_() < version.parse(bstack1l1l11l_opy_ (u"ࠩ࠶࠲࠹࠴࠰ࠨझ")):
    return False
  if bstack1111l1l1_opy_() >= version.parse(bstack1l1l11l_opy_ (u"ࠪ࠸࠳࠷࠮࠶ࠩञ")):
    return True
  if bstack1l1l11l_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫट") in config and config[bstack1l1l11l_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬठ")] == False:
    return False
  else:
    return True
def bstack1l1ll111l_opy_(config, index=0):
  global bstack11ll1ll1l_opy_
  bstack1lll11111l_opy_ = {}
  caps = bstack11l1lll11_opy_ + bstack1l1l1lll1_opy_
  if bstack11ll1ll1l_opy_:
    caps += bstack1ll111lll_opy_
  for key in config:
    if key in caps + [bstack1l1l11l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩड")]:
      continue
    bstack1lll11111l_opy_[key] = config[key]
  if bstack1l1l11l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪढ") in config:
    for bstack11lllll1l_opy_ in config[bstack1l1l11l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫण")][index]:
      if bstack11lllll1l_opy_ in caps + [bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧत"), bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫथ")]:
        continue
      bstack1lll11111l_opy_[bstack11lllll1l_opy_] = config[bstack1l1l11l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧद")][index][bstack11lllll1l_opy_]
  bstack1lll11111l_opy_[bstack1l1l11l_opy_ (u"ࠬ࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧध")] = socket.gethostname()
  if bstack1l1l11l_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧन") in bstack1lll11111l_opy_:
    del (bstack1lll11111l_opy_[bstack1l1l11l_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨऩ")])
  return bstack1lll11111l_opy_
def bstack11l11l1ll_opy_(config):
  global bstack11ll1ll1l_opy_
  bstack1llll1ll_opy_ = {}
  caps = bstack1l1l1lll1_opy_
  if bstack11ll1ll1l_opy_:
    caps += bstack1ll111lll_opy_
  for key in caps:
    if key in config:
      bstack1llll1ll_opy_[key] = config[key]
  return bstack1llll1ll_opy_
def bstack1llll11111_opy_(bstack1lll11111l_opy_, bstack1llll1ll_opy_):
  bstack1l1llll1l_opy_ = {}
  for key in bstack1lll11111l_opy_.keys():
    if key in bstack1llllll11l_opy_:
      bstack1l1llll1l_opy_[bstack1llllll11l_opy_[key]] = bstack1lll11111l_opy_[key]
    else:
      bstack1l1llll1l_opy_[key] = bstack1lll11111l_opy_[key]
  for key in bstack1llll1ll_opy_:
    if key in bstack1llllll11l_opy_:
      bstack1l1llll1l_opy_[bstack1llllll11l_opy_[key]] = bstack1llll1ll_opy_[key]
    else:
      bstack1l1llll1l_opy_[key] = bstack1llll1ll_opy_[key]
  return bstack1l1llll1l_opy_
def bstack1l111l1l1_opy_(config, index=0):
  global bstack11ll1ll1l_opy_
  config = copy.deepcopy(config)
  caps = {}
  bstack1llll1ll_opy_ = bstack11l11l1ll_opy_(config)
  bstack111lllll_opy_ = bstack1l1l1lll1_opy_
  bstack111lllll_opy_ += bstack1111ll1ll_opy_
  if bstack11ll1ll1l_opy_:
    bstack111lllll_opy_ += bstack1ll111lll_opy_
  if bstack1l1l11l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫप") in config:
    if bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧफ") in config[bstack1l1l11l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ब")][index]:
      caps[bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩभ")] = config[bstack1l1l11l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨम")][index][bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫय")]
    if bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨर") in config[bstack1l1l11l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫऱ")][index]:
      caps[bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪल")] = str(config[bstack1l1l11l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ळ")][index][bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬऴ")])
    bstack1l1111l11_opy_ = {}
    for bstack111ll11l_opy_ in bstack111lllll_opy_:
      if bstack111ll11l_opy_ in config[bstack1l1l11l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨव")][index]:
        if bstack111ll11l_opy_ == bstack1l1l11l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨश"):
          try:
            bstack1l1111l11_opy_[bstack111ll11l_opy_] = str(config[bstack1l1l11l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪष")][index][bstack111ll11l_opy_] * 1.0)
          except:
            bstack1l1111l11_opy_[bstack111ll11l_opy_] = str(config[bstack1l1l11l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫस")][index][bstack111ll11l_opy_])
        else:
          bstack1l1111l11_opy_[bstack111ll11l_opy_] = config[bstack1l1l11l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬह")][index][bstack111ll11l_opy_]
        del (config[bstack1l1l11l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ऺ")][index][bstack111ll11l_opy_])
    bstack1llll1ll_opy_ = update(bstack1llll1ll_opy_, bstack1l1111l11_opy_)
  bstack1lll11111l_opy_ = bstack1l1ll111l_opy_(config, index)
  for bstack1111llll_opy_ in bstack1l1l1lll1_opy_ + [bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩऻ"), bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ़࠭")]:
    if bstack1111llll_opy_ in bstack1lll11111l_opy_:
      bstack1llll1ll_opy_[bstack1111llll_opy_] = bstack1lll11111l_opy_[bstack1111llll_opy_]
      del (bstack1lll11111l_opy_[bstack1111llll_opy_])
  if bstack1llll1111_opy_(config):
    bstack1lll11111l_opy_[bstack1l1l11l_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ऽ")] = True
    caps.update(bstack1llll1ll_opy_)
    caps[bstack1l1l11l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨा")] = bstack1lll11111l_opy_
  else:
    bstack1lll11111l_opy_[bstack1l1l11l_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨि")] = False
    caps.update(bstack1llll11111_opy_(bstack1lll11111l_opy_, bstack1llll1ll_opy_))
    if bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧी") in caps:
      caps[bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫु")] = caps[bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩू")]
      del (caps[bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪृ")])
    if bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧॄ") in caps:
      caps[bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩॅ")] = caps[bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩॆ")]
      del (caps[bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪे")])
  return caps
def bstack1l11l1l1l_opy_():
  global bstack11ll11l1_opy_
  if bstack1111l1l1_opy_() <= version.parse(bstack1l1l11l_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪै")):
    if bstack11ll11l1_opy_ != bstack1l1l11l_opy_ (u"ࠫࠬॉ"):
      return bstack1l1l11l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨॊ") + bstack11ll11l1_opy_ + bstack1l1l11l_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥो")
    return bstack11111ll1_opy_
  if bstack11ll11l1_opy_ != bstack1l1l11l_opy_ (u"ࠧࠨौ"):
    return bstack1l1l11l_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱्ࠥ") + bstack11ll11l1_opy_ + bstack1l1l11l_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥॎ")
  return bstack1llll1l1l1_opy_
def bstack1l1lll11_opy_(options):
  return hasattr(options, bstack1l1l11l_opy_ (u"ࠪࡷࡪࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶࡼࠫॏ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1111ll11_opy_(options, bstack1l1l1l1ll_opy_):
  for bstack1lll1l1l1_opy_ in bstack1l1l1l1ll_opy_:
    if bstack1lll1l1l1_opy_ in [bstack1l1l11l_opy_ (u"ࠫࡦࡸࡧࡴࠩॐ"), bstack1l1l11l_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩ॑")]:
      next
    if bstack1lll1l1l1_opy_ in options._experimental_options:
      options._experimental_options[bstack1lll1l1l1_opy_] = update(options._experimental_options[bstack1lll1l1l1_opy_],
                                                         bstack1l1l1l1ll_opy_[bstack1lll1l1l1_opy_])
    else:
      options.add_experimental_option(bstack1lll1l1l1_opy_, bstack1l1l1l1ll_opy_[bstack1lll1l1l1_opy_])
  if bstack1l1l11l_opy_ (u"࠭ࡡࡳࡩࡶ॒ࠫ") in bstack1l1l1l1ll_opy_:
    for arg in bstack1l1l1l1ll_opy_[bstack1l1l11l_opy_ (u"ࠧࡢࡴࡪࡷࠬ॓")]:
      options.add_argument(arg)
    del (bstack1l1l1l1ll_opy_[bstack1l1l11l_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭॔")])
  if bstack1l1l11l_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ࠭ॕ") in bstack1l1l1l1ll_opy_:
    for ext in bstack1l1l1l1ll_opy_[bstack1l1l11l_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧॖ")]:
      options.add_extension(ext)
    del (bstack1l1l1l1ll_opy_[bstack1l1l11l_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨॗ")])
def bstack11lll1ll1_opy_(options, bstack111l11l1l_opy_):
  if bstack1l1l11l_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫक़") in bstack111l11l1l_opy_:
    for bstack1l1111ll1_opy_ in bstack111l11l1l_opy_[bstack1l1l11l_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬख़")]:
      if bstack1l1111ll1_opy_ in options._preferences:
        options._preferences[bstack1l1111ll1_opy_] = update(options._preferences[bstack1l1111ll1_opy_], bstack111l11l1l_opy_[bstack1l1l11l_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭ग़")][bstack1l1111ll1_opy_])
      else:
        options.set_preference(bstack1l1111ll1_opy_, bstack111l11l1l_opy_[bstack1l1l11l_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧज़")][bstack1l1111ll1_opy_])
  if bstack1l1l11l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧड़") in bstack111l11l1l_opy_:
    for arg in bstack111l11l1l_opy_[bstack1l1l11l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨढ़")]:
      options.add_argument(arg)
def bstack11lll1l1l_opy_(options, bstack1111l111l_opy_):
  if bstack1l1l11l_opy_ (u"ࠫࡼ࡫ࡢࡷ࡫ࡨࡻࠬफ़") in bstack1111l111l_opy_:
    options.use_webview(bool(bstack1111l111l_opy_[bstack1l1l11l_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼ࠭य़")]))
  bstack1111ll11_opy_(options, bstack1111l111l_opy_)
def bstack1lllll11ll_opy_(options, bstack11lll111l_opy_):
  for bstack1111l11l_opy_ in bstack11lll111l_opy_:
    if bstack1111l11l_opy_ in [bstack1l1l11l_opy_ (u"࠭ࡴࡦࡥ࡫ࡲࡴࡲ࡯ࡨࡻࡓࡶࡪࡼࡩࡦࡹࠪॠ"), bstack1l1l11l_opy_ (u"ࠧࡢࡴࡪࡷࠬॡ")]:
      next
    options.set_capability(bstack1111l11l_opy_, bstack11lll111l_opy_[bstack1111l11l_opy_])
  if bstack1l1l11l_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ॢ") in bstack11lll111l_opy_:
    for arg in bstack11lll111l_opy_[bstack1l1l11l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧॣ")]:
      options.add_argument(arg)
  if bstack1l1l11l_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧ।") in bstack11lll111l_opy_:
    options.bstack1lll11lll_opy_(bool(bstack11lll111l_opy_[bstack1l1l11l_opy_ (u"ࠫࡹ࡫ࡣࡩࡰࡲࡰࡴ࡭ࡹࡑࡴࡨࡺ࡮࡫ࡷࠨ॥")]))
def bstack111ll1lll_opy_(options, bstack11l1111ll_opy_):
  for bstack1l1l1ll1l_opy_ in bstack11l1111ll_opy_:
    if bstack1l1l1ll1l_opy_ in [bstack1l1l11l_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ०"), bstack1l1l11l_opy_ (u"࠭ࡡࡳࡩࡶࠫ१")]:
      next
    options._options[bstack1l1l1ll1l_opy_] = bstack11l1111ll_opy_[bstack1l1l1ll1l_opy_]
  if bstack1l1l11l_opy_ (u"ࠧࡢࡦࡧ࡭ࡹ࡯࡯࡯ࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ२") in bstack11l1111ll_opy_:
    for bstack1l1ll1l11_opy_ in bstack11l1111ll_opy_[bstack1l1l11l_opy_ (u"ࠨࡣࡧࡨ࡮ࡺࡩࡰࡰࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ३")]:
      options.bstack1lll1lll1l_opy_(
        bstack1l1ll1l11_opy_, bstack11l1111ll_opy_[bstack1l1l11l_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭४")][bstack1l1ll1l11_opy_])
  if bstack1l1l11l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ५") in bstack11l1111ll_opy_:
    for arg in bstack11l1111ll_opy_[bstack1l1l11l_opy_ (u"ࠫࡦࡸࡧࡴࠩ६")]:
      options.add_argument(arg)
def bstack1llll11ll1_opy_(options, caps):
  if not hasattr(options, bstack1l1l11l_opy_ (u"ࠬࡑࡅ࡚ࠩ७")):
    return
  if options.KEY == bstack1l1l11l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ८") and options.KEY in caps:
    bstack1111ll11_opy_(options, caps[bstack1l1l11l_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ९")])
  elif options.KEY == bstack1l1l11l_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭॰") and options.KEY in caps:
    bstack11lll1ll1_opy_(options, caps[bstack1l1l11l_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧॱ")])
  elif options.KEY == bstack1l1l11l_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫࠱ࡳࡵࡺࡩࡰࡰࡶࠫॲ") and options.KEY in caps:
    bstack1lllll11ll_opy_(options, caps[bstack1l1l11l_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬॳ")])
  elif options.KEY == bstack1l1l11l_opy_ (u"ࠬࡳࡳ࠻ࡧࡧ࡫ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ॴ") and options.KEY in caps:
    bstack11lll1l1l_opy_(options, caps[bstack1l1l11l_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧॵ")])
  elif options.KEY == bstack1l1l11l_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ॶ") and options.KEY in caps:
    bstack111ll1lll_opy_(options, caps[bstack1l1l11l_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧॷ")])
def bstack1lll111111_opy_(caps):
  global bstack11ll1ll1l_opy_
  if bstack11ll1ll1l_opy_:
    if bstack1ll11l11l_opy_() < version.parse(bstack1l1l11l_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨॸ")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack1l1l11l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪॹ")
    if bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩॺ") in caps:
      browser = caps[bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪॻ")]
    elif bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧॼ") in caps:
      browser = caps[bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨॽ")]
    browser = str(browser).lower()
    if browser == bstack1l1l11l_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨॾ") or browser == bstack1l1l11l_opy_ (u"ࠩ࡬ࡴࡦࡪࠧॿ"):
      browser = bstack1l1l11l_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪঀ")
    if browser == bstack1l1l11l_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬঁ"):
      browser = bstack1l1l11l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬং")
    if browser not in [bstack1l1l11l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭ঃ"), bstack1l1l11l_opy_ (u"ࠧࡦࡦࡪࡩࠬ঄"), bstack1l1l11l_opy_ (u"ࠨ࡫ࡨࠫঅ"), bstack1l1l11l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩআ"), bstack1l1l11l_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫই")]:
      return None
    try:
      package = bstack1l1l11l_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭ঈ").format(browser)
      name = bstack1l1l11l_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭উ")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack1l1lll11_opy_(options):
        return None
      for bstack1111llll_opy_ in caps.keys():
        options.set_capability(bstack1111llll_opy_, caps[bstack1111llll_opy_])
      bstack1llll11ll1_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack1l1ll11l_opy_(options, bstack11l11l1l_opy_):
  if not bstack1l1lll11_opy_(options):
    return
  for bstack1111llll_opy_ in bstack11l11l1l_opy_.keys():
    if bstack1111llll_opy_ in bstack1111ll1ll_opy_:
      next
    if bstack1111llll_opy_ in options._caps and type(options._caps[bstack1111llll_opy_]) in [dict, list]:
      options._caps[bstack1111llll_opy_] = update(options._caps[bstack1111llll_opy_], bstack11l11l1l_opy_[bstack1111llll_opy_])
    else:
      options.set_capability(bstack1111llll_opy_, bstack11l11l1l_opy_[bstack1111llll_opy_])
  bstack1llll11ll1_opy_(options, bstack11l11l1l_opy_)
  if bstack1l1l11l_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬঊ") in options._caps:
    if options._caps[bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬঋ")] and options._caps[bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ঌ")].lower() != bstack1l1l11l_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪ঍"):
      del options._caps[bstack1l1l11l_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩ঎")]
def bstack111llll1l_opy_(proxy_config):
  if bstack1l1l11l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨএ") in proxy_config:
    proxy_config[bstack1l1l11l_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧঐ")] = proxy_config[bstack1l1l11l_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪ঑")]
    del (proxy_config[bstack1l1l11l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫ঒")])
  if bstack1l1l11l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫও") in proxy_config and proxy_config[bstack1l1l11l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬঔ")].lower() != bstack1l1l11l_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪক"):
    proxy_config[bstack1l1l11l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧখ")] = bstack1l1l11l_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬগ")
  if bstack1l1l11l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫঘ") in proxy_config:
    proxy_config[bstack1l1l11l_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪঙ")] = bstack1l1l11l_opy_ (u"ࠨࡲࡤࡧࠬচ")
  return proxy_config
def bstack1lllllllll_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack1l1l11l_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨছ") in config:
    return proxy
  config[bstack1l1l11l_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩজ")] = bstack111llll1l_opy_(config[bstack1l1l11l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪঝ")])
  if proxy == None:
    proxy = Proxy(config[bstack1l1l11l_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫঞ")])
  return proxy
def bstack1llll1l11l_opy_(self):
  global CONFIG
  global bstack1ll1ll11_opy_
  try:
    proxy = bstack1ll11l1l_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack1l1l11l_opy_ (u"࠭࠮ࡱࡣࡦࠫট")):
        proxies = bstack111ll111l_opy_(proxy, bstack1l11l1l1l_opy_())
        if len(proxies) > 0:
          protocol, bstack1ll1llll11_opy_ = proxies.popitem()
          if bstack1l1l11l_opy_ (u"ࠢ࠻࠱࠲ࠦঠ") in bstack1ll1llll11_opy_:
            return bstack1ll1llll11_opy_
          else:
            return bstack1l1l11l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤড") + bstack1ll1llll11_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack1l1l11l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨঢ").format(str(e)))
  return bstack1ll1ll11_opy_(self)
def bstack1l1l11l11_opy_():
  global CONFIG
  return bstack111llllll_opy_(CONFIG) and bstack1111l1l1_opy_() >= version.parse(bstack1lll11l1l_opy_)
def bstack1l111111_opy_(config):
  bstack1ll1lll111_opy_ = {}
  if bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧণ") in config:
    bstack1ll1lll111_opy_ = config[bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨত")]
  if bstack1l1l11l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫথ") in config:
    bstack1ll1lll111_opy_ = config[bstack1l1l11l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬদ")]
  proxy = bstack1ll11l1l_opy_(config)
  if proxy:
    if proxy.endswith(bstack1l1l11l_opy_ (u"ࠧ࠯ࡲࡤࡧࠬধ")) and os.path.isfile(proxy):
      bstack1ll1lll111_opy_[bstack1l1l11l_opy_ (u"ࠨ࠯ࡳࡥࡨ࠳ࡦࡪ࡮ࡨࠫন")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack1l1l11l_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ঩")):
        proxies = bstack1l1l1111_opy_(config, bstack1l11l1l1l_opy_())
        if len(proxies) > 0:
          protocol, bstack1ll1llll11_opy_ = proxies.popitem()
          if bstack1l1l11l_opy_ (u"ࠥ࠾࠴࠵ࠢপ") in bstack1ll1llll11_opy_:
            parsed_url = urlparse(bstack1ll1llll11_opy_)
          else:
            parsed_url = urlparse(protocol + bstack1l1l11l_opy_ (u"ࠦ࠿࠵࠯ࠣফ") + bstack1ll1llll11_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack1ll1lll111_opy_[bstack1l1l11l_opy_ (u"ࠬࡶࡲࡰࡺࡼࡌࡴࡹࡴࠨব")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack1ll1lll111_opy_[bstack1l1l11l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡕࡵࡲࡵࠩভ")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack1ll1lll111_opy_[bstack1l1l11l_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡛ࡳࡦࡴࠪম")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack1ll1lll111_opy_[bstack1l1l11l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡐࡢࡵࡶࠫয")] = str(parsed_url.password)
  return bstack1ll1lll111_opy_
def bstack11l11l111_opy_(config):
  if bstack1l1l11l_opy_ (u"ࠩࡷࡩࡸࡺࡃࡰࡰࡷࡩࡽࡺࡏࡱࡶ࡬ࡳࡳࡹࠧর") in config:
    return config[bstack1l1l11l_opy_ (u"ࠪࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠨ঱")]
  return {}
def bstack1ll1l111_opy_(caps):
  global bstack11l1ll111_opy_
  if bstack1l1l11l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮࠾ࡴࡶࡴࡪࡱࡱࡷࠬল") in caps:
    caps[bstack1l1l11l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭঳")][bstack1l1l11l_opy_ (u"࠭࡬ࡰࡥࡤࡰࠬ঴")] = True
    if bstack11l1ll111_opy_:
      caps[bstack1l1l11l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨ঵")][bstack1l1l11l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪশ")] = bstack11l1ll111_opy_
  else:
    caps[bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯࡮ࡲࡧࡦࡲࠧষ")] = True
    if bstack11l1ll111_opy_:
      caps[bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫস")] = bstack11l1ll111_opy_
def bstack1111l111_opy_():
  global CONFIG
  if bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨহ") in CONFIG and CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ঺")]:
    bstack1ll1lll111_opy_ = bstack1l111111_opy_(CONFIG)
    bstack1lll1l1l1l_opy_(CONFIG[bstack1l1l11l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ঻")], bstack1ll1lll111_opy_)
def bstack1lll1l1l1l_opy_(key, bstack1ll1lll111_opy_):
  global bstack1llll111ll_opy_
  logger.info(bstack1ll1llllll_opy_)
  try:
    bstack1llll111ll_opy_ = Local()
    bstack11111l1l_opy_ = {bstack1l1l11l_opy_ (u"ࠧ࡬ࡧࡼ়ࠫ"): key}
    bstack11111l1l_opy_.update(bstack1ll1lll111_opy_)
    logger.debug(bstack1lllll1l11_opy_.format(str(bstack11111l1l_opy_)))
    bstack1llll111ll_opy_.start(**bstack11111l1l_opy_)
    if bstack1llll111ll_opy_.isRunning():
      logger.info(bstack1llll11l_opy_)
  except Exception as e:
    bstack11llll11_opy_(bstack1111ll1l1_opy_.format(str(e)))
def bstack1111111ll_opy_():
  global bstack1llll111ll_opy_
  if bstack1llll111ll_opy_.isRunning():
    logger.info(bstack11111111l_opy_)
    bstack1llll111ll_opy_.stop()
  bstack1llll111ll_opy_ = None
def bstack1llll111l1_opy_(bstack11l111ll1_opy_=[]):
  global CONFIG
  bstack111ll1l1_opy_ = []
  bstack1l1l1111l_opy_ = [bstack1l1l11l_opy_ (u"ࠨࡱࡶࠫঽ"), bstack1l1l11l_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬা"), bstack1l1l11l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧি"), bstack1l1l11l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ী"), bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪু"), bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧূ")]
  try:
    for err in bstack11l111ll1_opy_:
      bstack1lll111l11_opy_ = {}
      for k in bstack1l1l1111l_opy_:
        val = CONFIG[bstack1l1l11l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪৃ")][int(err[bstack1l1l11l_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧৄ")])].get(k)
        if val:
          bstack1lll111l11_opy_[k] = val
      bstack1lll111l11_opy_[bstack1l1l11l_opy_ (u"ࠩࡷࡩࡸࡺࡳࠨ৅")] = {
        err[bstack1l1l11l_opy_ (u"ࠪࡲࡦࡳࡥࠨ৆")]: err[bstack1l1l11l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪে")]
      }
      bstack111ll1l1_opy_.append(bstack1lll111l11_opy_)
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧࡱࡵࡱࡦࡺࡴࡪࡰࡪࠤࡩࡧࡴࡢࠢࡩࡳࡷࠦࡥࡷࡧࡱࡸ࠿ࠦࠧৈ") + str(e))
  finally:
    return bstack111ll1l1_opy_
def bstack1lll1l111_opy_():
  global bstack11l1l1111_opy_
  global bstack11ll1lll_opy_
  global bstack1ll11ll1_opy_
  if bstack11l1l1111_opy_:
    logger.warning(bstack1lllll11_opy_.format(str(bstack11l1l1111_opy_)))
  logger.info(bstack1ll1ll111_opy_)
  global bstack1llll111ll_opy_
  if bstack1llll111ll_opy_:
    bstack1111111ll_opy_()
  try:
    for driver in bstack11ll1lll_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack1llllll11_opy_)
  bstack11ll11lll_opy_()
  if len(bstack1ll11ll1_opy_) > 0:
    message = bstack1llll111l1_opy_(bstack1ll11ll1_opy_)
    bstack11ll11lll_opy_(message)
  else:
    bstack11ll11lll_opy_()
def bstack1lll1lllll_opy_(self, *args):
  logger.error(bstack1l1ll1l1l_opy_)
  bstack1lll1l111_opy_()
  sys.exit(1)
def bstack11llll11_opy_(err):
  logger.critical(bstack1l111l111_opy_.format(str(err)))
  bstack11ll11lll_opy_(bstack1l111l111_opy_.format(str(err)))
  atexit.unregister(bstack1lll1l111_opy_)
  sys.exit(1)
def bstack1ll111111_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack11ll11lll_opy_(message)
  atexit.unregister(bstack1lll1l111_opy_)
  sys.exit(1)
def bstack111l1ll1l_opy_():
  global CONFIG
  global bstack1llllllll_opy_
  global bstack111lll1ll_opy_
  global bstack1ll1ll11l_opy_
  CONFIG = bstack1ll1l1l1l_opy_()
  bstack1ll11llll_opy_()
  bstack11l1ll11_opy_()
  CONFIG = bstack11l1lll1l_opy_(CONFIG)
  update(CONFIG, bstack111lll1ll_opy_)
  update(CONFIG, bstack1llllllll_opy_)
  CONFIG = bstack11lll11l_opy_(CONFIG)
  bstack1ll1ll11l_opy_ = bstack1lll1111l1_opy_(CONFIG)
  bstack1l11l1ll1_opy_.bstack1l11l1l1_opy_(bstack1l1l11l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡥࡳࡦࡵࡶ࡭ࡴࡴࠧ৉"), bstack1ll1ll11l_opy_)
  if (bstack1l1l11l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ৊") in CONFIG and bstack1l1l11l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫো") in bstack1llllllll_opy_) or (
          bstack1l1l11l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬৌ") in CONFIG and bstack1l1l11l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ্࠭") not in bstack111lll1ll_opy_):
    if os.getenv(bstack1l1l11l_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨৎ")):
      CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ৏")] = os.getenv(bstack1l1l11l_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡥࡃࡐࡏࡅࡍࡓࡋࡄࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࠪ৐"))
    else:
      bstack1ll11111l_opy_()
  elif (bstack1l1l11l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪ৑") not in CONFIG and bstack1l1l11l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ৒") in CONFIG) or (
          bstack1l1l11l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬ৓") in bstack111lll1ll_opy_ and bstack1l1l11l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭৔") not in bstack1llllllll_opy_):
    del (CONFIG[bstack1l1l11l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭৕")])
  if bstack1llllll111_opy_(CONFIG):
    bstack11llll11_opy_(bstack1l1llllll_opy_)
  bstack11ll111ll_opy_()
  bstack1lll11ll1l_opy_()
  if bstack11ll1ll1l_opy_:
    CONFIG[bstack1l1l11l_opy_ (u"ࠬࡧࡰࡱࠩ৖")] = bstack1lll1l1l_opy_(CONFIG)
    logger.info(bstack1ll1lll1l1_opy_.format(CONFIG[bstack1l1l11l_opy_ (u"࠭ࡡࡱࡲࠪৗ")]))
def bstack1lll11ll1l_opy_():
  global CONFIG
  global bstack11ll1ll1l_opy_
  if bstack1l1l11l_opy_ (u"ࠧࡢࡲࡳࠫ৘") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack1ll111111_opy_(e, bstack1lllll1l1l_opy_)
    bstack11ll1ll1l_opy_ = True
    bstack1l11l1ll1_opy_.bstack1l11l1l1_opy_(bstack1l1l11l_opy_ (u"ࠨࡣࡳࡴࡤࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ৙"), True)
def bstack1lll1l1l_opy_(config):
  bstack1lll11111_opy_ = bstack1l1l11l_opy_ (u"ࠩࠪ৚")
  app = config[bstack1l1l11l_opy_ (u"ࠪࡥࡵࡶࠧ৛")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack1ll11l11_opy_:
      if os.path.exists(app):
        bstack1lll11111_opy_ = bstack1l11l1ll_opy_(config, app)
      elif bstack11l1111l1_opy_(app):
        bstack1lll11111_opy_ = app
      else:
        bstack11llll11_opy_(bstack11lll11l1_opy_.format(app))
    else:
      if bstack11l1111l1_opy_(app):
        bstack1lll11111_opy_ = app
      elif os.path.exists(app):
        bstack1lll11111_opy_ = bstack1l11l1ll_opy_(app)
      else:
        bstack11llll11_opy_(bstack1lll11l111_opy_)
  else:
    if len(app) > 2:
      bstack11llll11_opy_(bstack11lll11ll_opy_)
    elif len(app) == 2:
      if bstack1l1l11l_opy_ (u"ࠫࡵࡧࡴࡩࠩড়") in app and bstack1l1l11l_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡤ࡯ࡤࠨঢ়") in app:
        if os.path.exists(app[bstack1l1l11l_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ৞")]):
          bstack1lll11111_opy_ = bstack1l11l1ll_opy_(config, app[bstack1l1l11l_opy_ (u"ࠧࡱࡣࡷ࡬ࠬয়")], app[bstack1l1l11l_opy_ (u"ࠨࡥࡸࡷࡹࡵ࡭ࡠ࡫ࡧࠫৠ")])
        else:
          bstack11llll11_opy_(bstack11lll11l1_opy_.format(app))
      else:
        bstack11llll11_opy_(bstack11lll11ll_opy_)
    else:
      for key in app:
        if key in bstack1l111l11l_opy_:
          if key == bstack1l1l11l_opy_ (u"ࠩࡳࡥࡹ࡮ࠧৡ"):
            if os.path.exists(app[key]):
              bstack1lll11111_opy_ = bstack1l11l1ll_opy_(config, app[key])
            else:
              bstack11llll11_opy_(bstack11lll11l1_opy_.format(app))
          else:
            bstack1lll11111_opy_ = app[key]
        else:
          bstack11llll11_opy_(bstack1l11l1lll_opy_)
  return bstack1lll11111_opy_
def bstack11l1111l1_opy_(bstack1lll11111_opy_):
  import re
  bstack1lllll1l1_opy_ = re.compile(bstack1l1l11l_opy_ (u"ࡵࠦࡣࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫࠦࠥৢ"))
  bstack1ll1lll1l_opy_ = re.compile(bstack1l1l11l_opy_ (u"ࡶࠧࡤ࡛ࡢ࠯ࡽࡅ࠲ࡠ࠰࠮࠻࡟ࡣ࠳ࡢ࠭࡞ࠬ࠲࡟ࡦ࠳ࡺࡂ࠯࡝࠴࠲࠿࡜ࡠ࠰࡟࠱ࡢ࠰ࠤࠣৣ"))
  if bstack1l1l11l_opy_ (u"ࠬࡨࡳ࠻࠱࠲ࠫ৤") in bstack1lll11111_opy_ or re.fullmatch(bstack1lllll1l1_opy_, bstack1lll11111_opy_) or re.fullmatch(bstack1ll1lll1l_opy_, bstack1lll11111_opy_):
    return True
  else:
    return False
def bstack1l11l1ll_opy_(config, path, bstack11l11111l_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack1l1l11l_opy_ (u"࠭ࡲࡣࠩ৥")).read()).hexdigest()
  bstack1ll1l11ll_opy_ = bstack11llll11l_opy_(md5_hash)
  bstack1lll11111_opy_ = None
  if bstack1ll1l11ll_opy_:
    logger.info(bstack1ll1llll1_opy_.format(bstack1ll1l11ll_opy_, md5_hash))
    return bstack1ll1l11ll_opy_
  bstack1lllllll1l_opy_ = MultipartEncoder(
    fields={
      bstack1l1l11l_opy_ (u"ࠧࡧ࡫࡯ࡩࠬ০"): (os.path.basename(path), open(os.path.abspath(path), bstack1l1l11l_opy_ (u"ࠨࡴࡥࠫ১")), bstack1l1l11l_opy_ (u"ࠩࡷࡩࡽࡺ࠯ࡱ࡮ࡤ࡭ࡳ࠭২")),
      bstack1l1l11l_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭৩"): bstack11l11111l_opy_
    }
  )
  response = requests.post(bstack111l1l1l1_opy_, data=bstack1lllllll1l_opy_,
                           headers={bstack1l1l11l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲࡚ࡹࡱࡧࠪ৪"): bstack1lllllll1l_opy_.content_type},
                           auth=(config[bstack1l1l11l_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ৫")], config[bstack1l1l11l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ৬")]))
  try:
    res = json.loads(response.text)
    bstack1lll11111_opy_ = res[bstack1l1l11l_opy_ (u"ࠧࡢࡲࡳࡣࡺࡸ࡬ࠨ৭")]
    logger.info(bstack111l1ll1_opy_.format(bstack1lll11111_opy_))
    bstack11l1llll1_opy_(md5_hash, bstack1lll11111_opy_)
  except ValueError as err:
    bstack11llll11_opy_(bstack1ll11ll11_opy_.format(str(err)))
  return bstack1lll11111_opy_
def bstack11ll111ll_opy_():
  global CONFIG
  global bstack111l1l1ll_opy_
  bstack1llll1l11_opy_ = 0
  bstack1ll11lll1_opy_ = 1
  if bstack1l1l11l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ৮") in CONFIG:
    bstack1ll11lll1_opy_ = CONFIG[bstack1l1l11l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ৯")]
  if bstack1l1l11l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ৰ") in CONFIG:
    bstack1llll1l11_opy_ = len(CONFIG[bstack1l1l11l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧৱ")])
  bstack111l1l1ll_opy_ = int(bstack1ll11lll1_opy_) * int(bstack1llll1l11_opy_)
def bstack11llll11l_opy_(md5_hash):
  bstack1ll111l1l_opy_ = os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"ࠬࢄࠧ৲")), bstack1l1l11l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭৳"), bstack1l1l11l_opy_ (u"ࠧࡢࡲࡳ࡙ࡵࡲ࡯ࡢࡦࡐࡈ࠺ࡎࡡࡴࡪ࠱࡮ࡸࡵ࡮ࠨ৴"))
  if os.path.exists(bstack1ll111l1l_opy_):
    bstack111l11ll_opy_ = json.load(open(bstack1ll111l1l_opy_, bstack1l1l11l_opy_ (u"ࠨࡴࡥࠫ৵")))
    if md5_hash in bstack111l11ll_opy_:
      bstack1llllllll1_opy_ = bstack111l11ll_opy_[md5_hash]
      bstack111l1llll_opy_ = datetime.datetime.now()
      bstack111l1l11l_opy_ = datetime.datetime.strptime(bstack1llllllll1_opy_[bstack1l1l11l_opy_ (u"ࠩࡷ࡭ࡲ࡫ࡳࡵࡣࡰࡴࠬ৶")], bstack1l1l11l_opy_ (u"ࠪࠩࡩ࠵ࠥ࡮࠱ࠨ࡝ࠥࠫࡈ࠻ࠧࡐ࠾࡙ࠪࠧ৷"))
      if (bstack111l1llll_opy_ - bstack111l1l11l_opy_).days > 60:
        return None
      elif version.parse(str(__version__)) > version.parse(bstack1llllllll1_opy_[bstack1l1l11l_opy_ (u"ࠫࡸࡪ࡫ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ৸")]):
        return None
      return bstack1llllllll1_opy_[bstack1l1l11l_opy_ (u"ࠬ࡯ࡤࠨ৹")]
  else:
    return None
def bstack11l1llll1_opy_(md5_hash, bstack1lll11111_opy_):
  bstack1ll1ll1ll1_opy_ = os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"࠭ࡾࠨ৺")), bstack1l1l11l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ৻"))
  if not os.path.exists(bstack1ll1ll1ll1_opy_):
    os.makedirs(bstack1ll1ll1ll1_opy_)
  bstack1ll111l1l_opy_ = os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"ࠨࢀࠪৼ")), bstack1l1l11l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ৽"), bstack1l1l11l_opy_ (u"ࠪࡥࡵࡶࡕࡱ࡮ࡲࡥࡩࡓࡄ࠶ࡊࡤࡷ࡭࠴ࡪࡴࡱࡱࠫ৾"))
  bstack1lll111l1l_opy_ = {
    bstack1l1l11l_opy_ (u"ࠫ࡮ࡪࠧ৿"): bstack1lll11111_opy_,
    bstack1l1l11l_opy_ (u"ࠬࡺࡩ࡮ࡧࡶࡸࡦࡳࡰࠨ਀"): datetime.datetime.strftime(datetime.datetime.now(), bstack1l1l11l_opy_ (u"࠭ࠥࡥ࠱ࠨࡱ࠴࡙ࠫࠡࠧࡋ࠾ࠪࡓ࠺ࠦࡕࠪਁ")),
    bstack1l1l11l_opy_ (u"ࠧࡴࡦ࡮ࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬਂ"): str(__version__)
  }
  if os.path.exists(bstack1ll111l1l_opy_):
    bstack111l11ll_opy_ = json.load(open(bstack1ll111l1l_opy_, bstack1l1l11l_opy_ (u"ࠨࡴࡥࠫਃ")))
  else:
    bstack111l11ll_opy_ = {}
  bstack111l11ll_opy_[md5_hash] = bstack1lll111l1l_opy_
  with open(bstack1ll111l1l_opy_, bstack1l1l11l_opy_ (u"ࠤࡺ࠯ࠧ਄")) as outfile:
    json.dump(bstack111l11ll_opy_, outfile)
def bstack1l1l11lll_opy_(self):
  return
def bstack1llll111l_opy_(self):
  return
def bstack1llll1l1ll_opy_(self):
  from selenium.webdriver.remote.webdriver import WebDriver
  WebDriver.quit(self)
def bstack1lll11l1ll_opy_(self):
  global bstack11l1l11l1_opy_
  global bstack111lll1l1_opy_
  global bstack111ll11ll_opy_
  try:
    if bstack1l1l11l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪਅ") in bstack11l1l11l1_opy_ and self.session_id != None:
      bstack1lll111l1_opy_ = bstack1l1l11l_opy_ (u"ࠫࡵࡧࡳࡴࡧࡧࠫਆ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack1l1l11l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬਇ")
      bstack111111ll1_opy_ = bstack1l11l11l_opy_(bstack1l1l11l_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩਈ"), bstack1l1l11l_opy_ (u"ࠧࠨਉ"), bstack1lll111l1_opy_, bstack1l1l11l_opy_ (u"ࠨ࠮ࠣࠫਊ").join(
        threading.current_thread().bstackTestErrorMessages), bstack1l1l11l_opy_ (u"ࠩࠪ਋"), bstack1l1l11l_opy_ (u"ࠪࠫ਌"))
      if self != None:
        self.execute_script(bstack111111ll1_opy_)
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣࡻ࡭࡯࡬ࡦࠢࡰࡥࡷࡱࡩ࡯ࡩࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࠧ਍") + str(e))
  bstack111ll11ll_opy_(self)
  self.session_id = None
def bstack1llll1111l_opy_(self, *args, **kwargs):
  bstack1ll111l11_opy_ = bstack1111l1ll_opy_(self, *args, **kwargs)
  bstack1llll1lll1_opy_.bstack111l11l11_opy_(self)
  return bstack1ll111l11_opy_
def bstack1ll1l111l_opy_(self, command_executor,
             desired_capabilities=None, browser_profile=None, proxy=None,
             keep_alive=True, file_detector=None, options=None):
  global CONFIG
  global bstack111lll1l1_opy_
  global bstack1ll1llll1l_opy_
  global bstack1l1lllll_opy_
  global bstack1l111l11_opy_
  global bstack1lll1l1lll_opy_
  global bstack11l1l11l1_opy_
  global bstack1111l1ll_opy_
  global bstack11ll1lll_opy_
  global bstack1llll11lll_opy_
  CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧ਎")] = str(bstack11l1l11l1_opy_) + str(__version__)
  command_executor = bstack1l11l1l1l_opy_()
  logger.debug(bstack1ll1l1ll1_opy_.format(command_executor))
  proxy = bstack1lllllllll_opy_(CONFIG, proxy)
  bstack1111lllll_opy_ = 0 if bstack1ll1llll1l_opy_ < 0 else bstack1ll1llll1l_opy_
  try:
    if bstack1l111l11_opy_ is True:
      bstack1111lllll_opy_ = int(multiprocessing.current_process().name)
    elif bstack1lll1l1lll_opy_ is True:
      bstack1111lllll_opy_ = int(threading.current_thread().name)
  except:
    bstack1111lllll_opy_ = 0
  bstack11l11l1l_opy_ = bstack1l111l1l1_opy_(CONFIG, bstack1111lllll_opy_)
  logger.debug(bstack1111l1111_opy_.format(str(bstack11l11l1l_opy_)))
  if bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪਏ") in CONFIG and CONFIG[bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࠫਐ")]:
    bstack1ll1l111_opy_(bstack11l11l1l_opy_)
  if desired_capabilities:
    bstack1ll1111ll_opy_ = bstack11l1lll1l_opy_(desired_capabilities)
    bstack1ll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨ਑")] = bstack1llll1111_opy_(CONFIG)
    bstack111l1lll1_opy_ = bstack1l111l1l1_opy_(bstack1ll1111ll_opy_)
    if bstack111l1lll1_opy_:
      bstack11l11l1l_opy_ = update(bstack111l1lll1_opy_, bstack11l11l1l_opy_)
    desired_capabilities = None
  if options:
    bstack1l1ll11l_opy_(options, bstack11l11l1l_opy_)
  if not options:
    options = bstack1lll111111_opy_(bstack11l11l1l_opy_)
  if proxy and bstack1111l1l1_opy_() >= version.parse(bstack1l1l11l_opy_ (u"ࠩ࠷࠲࠶࠶࠮࠱ࠩ਒")):
    options.proxy(proxy)
  if options and bstack1111l1l1_opy_() >= version.parse(bstack1l1l11l_opy_ (u"ࠪ࠷࠳࠾࠮࠱ࠩਓ")):
    desired_capabilities = None
  if (
          not options and not desired_capabilities
  ) or (
          bstack1111l1l1_opy_() < version.parse(bstack1l1l11l_opy_ (u"ࠫ࠸࠴࠸࠯࠲ࠪਔ")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack11l11l1l_opy_)
  logger.info(bstack111lll111_opy_)
  if bstack1111l1l1_opy_() >= version.parse(bstack1l1l11l_opy_ (u"ࠬ࠺࠮࠲࠲࠱࠴ࠬਕ")):
    bstack1111l1ll_opy_(self, command_executor=command_executor,
              options=options, keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1111l1l1_opy_() >= version.parse(bstack1l1l11l_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬਖ")):
    bstack1111l1ll_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities, options=options,
              browser_profile=browser_profile, proxy=proxy,
              keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1111l1l1_opy_() >= version.parse(bstack1l1l11l_opy_ (u"ࠧ࠳࠰࠸࠷࠳࠶ࠧਗ")):
    bstack1111l1ll_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities,
              browser_profile=browser_profile, proxy=proxy,
              keep_alive=keep_alive, file_detector=file_detector)
  else:
    bstack1111l1ll_opy_(self, command_executor=command_executor,
              desired_capabilities=desired_capabilities,
              browser_profile=browser_profile, proxy=proxy,
              keep_alive=keep_alive)
  try:
    bstack1llll1l111_opy_ = bstack1l1l11l_opy_ (u"ࠨࠩਘ")
    if bstack1111l1l1_opy_() >= version.parse(bstack1l1l11l_opy_ (u"ࠩ࠷࠲࠵࠴࠰ࡣ࠳ࠪਙ")):
      bstack1llll1l111_opy_ = self.caps.get(bstack1l1l11l_opy_ (u"ࠥࡳࡵࡺࡩ࡮ࡣ࡯ࡌࡺࡨࡕࡳ࡮ࠥਚ"))
    else:
      bstack1llll1l111_opy_ = self.capabilities.get(bstack1l1l11l_opy_ (u"ࠦࡴࡶࡴࡪ࡯ࡤࡰࡍࡻࡢࡖࡴ࡯ࠦਛ"))
    if bstack1llll1l111_opy_:
      if bstack1111l1l1_opy_() <= version.parse(bstack1l1l11l_opy_ (u"ࠬ࠹࠮࠲࠵࠱࠴ࠬਜ")):
        self.command_executor._url = bstack1l1l11l_opy_ (u"ࠨࡨࡵࡶࡳ࠾࠴࠵ࠢਝ") + bstack11ll11l1_opy_ + bstack1l1l11l_opy_ (u"ࠢ࠻࠺࠳࠳ࡼࡪ࠯ࡩࡷࡥࠦਞ")
      else:
        self.command_executor._url = bstack1l1l11l_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥਟ") + bstack1llll1l111_opy_ + bstack1l1l11l_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥਠ")
      logger.debug(bstack1lllll1111_opy_.format(bstack1llll1l111_opy_))
    else:
      logger.debug(bstack1ll11111_opy_.format(bstack1l1l11l_opy_ (u"ࠥࡓࡵࡺࡩ࡮ࡣ࡯ࠤࡍࡻࡢࠡࡰࡲࡸࠥ࡬࡯ࡶࡰࡧࠦਡ")))
  except Exception as e:
    logger.debug(bstack1ll11111_opy_.format(e))
  if bstack1l1l11l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪਢ") in bstack11l1l11l1_opy_:
    bstack1lllll111_opy_(bstack1ll1llll1l_opy_, bstack1llll11lll_opy_)
  bstack111lll1l1_opy_ = self.session_id
  if bstack1l1l11l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬਣ") in bstack11l1l11l1_opy_ or bstack1l1l11l_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ਤ") in bstack11l1l11l1_opy_:
    threading.current_thread().bstack1111ll111_opy_ = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
    bstack1llll1lll1_opy_.bstack111l11l11_opy_(self)
  bstack11ll1lll_opy_.append(self)
  if bstack1l1l11l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪਥ") in CONFIG and bstack1l1l11l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ਦ") in CONFIG[bstack1l1l11l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬਧ")][bstack1111lllll_opy_]:
    bstack1l1lllll_opy_ = CONFIG[bstack1l1l11l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ਨ")][bstack1111lllll_opy_][bstack1l1l11l_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ਩")]
  logger.debug(bstack1llll11l11_opy_.format(bstack111lll1l1_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    def bstack1lll11ll11_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1l1ll1ll_opy_
      if(bstack1l1l11l_opy_ (u"ࠧ࡯࡮ࡥࡧࡻ࠲࡯ࡹࠢਪ") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"࠭ࡾࠨਫ")), bstack1l1l11l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧਬ"), bstack1l1l11l_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪਭ")), bstack1l1l11l_opy_ (u"ࠩࡺࠫਮ")) as fp:
          fp.write(bstack1l1l11l_opy_ (u"ࠥࠦਯ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack1l1l11l_opy_ (u"ࠦ࡮ࡴࡤࡦࡺࡢࡦࡸࡺࡡࡤ࡭࠱࡮ࡸࠨਰ")))):
          with open(args[1], bstack1l1l11l_opy_ (u"ࠬࡸࠧ਱")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack1l1l11l_opy_ (u"࠭ࡡࡴࡻࡱࡧࠥ࡬ࡵ࡯ࡥࡷ࡭ࡴࡴࠠࡠࡰࡨࡻࡕࡧࡧࡦࠪࡦࡳࡳࡺࡥࡹࡶ࠯ࠤࡵࡧࡧࡦࠢࡀࠤࡻࡵࡩࡥࠢ࠳࠭ࠬਲ") in line), None)
            if index is not None:
                lines.insert(index+2, bstack11llllll_opy_)
            lines.insert(1, bstack111l111l1_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack1l1l11l_opy_ (u"ࠢࡪࡰࡧࡩࡽࡥࡢࡴࡶࡤࡧࡰ࠴ࡪࡴࠤਲ਼")), bstack1l1l11l_opy_ (u"ࠨࡹࠪ਴")) as bstack1lllllll1_opy_:
              bstack1lllllll1_opy_.writelines(lines)
        CONFIG[bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡔࡆࡎࠫਵ")] = str(bstack11l1l11l1_opy_) + str(__version__)
        bstack1111lllll_opy_ = 0 if bstack1ll1llll1l_opy_ < 0 else bstack1ll1llll1l_opy_
        try:
          if bstack1l111l11_opy_ is True:
            bstack1111lllll_opy_ = int(multiprocessing.current_process().name)
          elif bstack1lll1l1lll_opy_ is True:
            bstack1111lllll_opy_ = int(threading.current_thread().name)
        except:
          bstack1111lllll_opy_ = 0
        CONFIG[bstack1l1l11l_opy_ (u"ࠥࡹࡸ࡫ࡗ࠴ࡅࠥਸ਼")] = False
        CONFIG[bstack1l1l11l_opy_ (u"ࠦ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥ਷")] = True
        bstack11l11l1l_opy_ = bstack1l111l1l1_opy_(CONFIG, bstack1111lllll_opy_)
        logger.debug(bstack1111l1111_opy_.format(str(bstack11l11l1l_opy_)))
        if CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩਸ")]:
          bstack1ll1l111_opy_(bstack11l11l1l_opy_)
        if bstack1l1l11l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩਹ") in CONFIG and bstack1l1l11l_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬ਺") in CONFIG[bstack1l1l11l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ਻")][bstack1111lllll_opy_]:
          bstack1l1lllll_opy_ = CONFIG[bstack1l1l11l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷ਼ࠬ")][bstack1111lllll_opy_][bstack1l1l11l_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ਽")]
        args.append(os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"ࠫࢃ࠭ਾ")), bstack1l1l11l_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬਿ"), bstack1l1l11l_opy_ (u"࠭࠮ࡴࡧࡶࡷ࡮ࡵ࡮ࡪࡦࡶ࠲ࡹࡾࡴࠨੀ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack11l11l1l_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack1l1l11l_opy_ (u"ࠢࡪࡰࡧࡩࡽࡥࡢࡴࡶࡤࡧࡰ࠴ࡪࡴࠤੁ"))
      bstack1l1ll1ll_opy_ = True
      return bstack1llll1ll11_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack1ll1l1lll_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack111lll1l1_opy_
    global bstack1ll1llll1l_opy_
    global bstack1l1lllll_opy_
    global bstack1l111l11_opy_
    global bstack1lll1l1lll_opy_
    global bstack11l1l11l1_opy_
    global bstack1111l1ll_opy_
    CONFIG[bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡓࡅࡍࠪੂ")] = str(bstack11l1l11l1_opy_) + str(__version__)
    bstack1111lllll_opy_ = 0 if bstack1ll1llll1l_opy_ < 0 else bstack1ll1llll1l_opy_
    try:
      if bstack1l111l11_opy_ is True:
        bstack1111lllll_opy_ = int(multiprocessing.current_process().name)
      elif bstack1lll1l1lll_opy_ is True:
        bstack1111lllll_opy_ = int(threading.current_thread().name)
    except:
      bstack1111lllll_opy_ = 0
    CONFIG[bstack1l1l11l_opy_ (u"ࠤ࡬ࡷࡕࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣ੃")] = True
    bstack11l11l1l_opy_ = bstack1l111l1l1_opy_(CONFIG, bstack1111lllll_opy_)
    logger.debug(bstack1111l1111_opy_.format(str(bstack11l11l1l_opy_)))
    if CONFIG[bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧ੄")]:
      bstack1ll1l111_opy_(bstack11l11l1l_opy_)
    if bstack1l1l11l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ੅") in CONFIG and bstack1l1l11l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ੆") in CONFIG[bstack1l1l11l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩੇ")][bstack1111lllll_opy_]:
      bstack1l1lllll_opy_ = CONFIG[bstack1l1l11l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪੈ")][bstack1111lllll_opy_][bstack1l1l11l_opy_ (u"ࠨࡵࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭੉")]
    import urllib
    import json
    bstack1111l1l11_opy_ = bstack1l1l11l_opy_ (u"ࠩࡺࡷࡸࡀ࠯࠰ࡥࡧࡴ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡲ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࡄࡩࡡࡱࡵࡀࠫ੊") + urllib.parse.quote(json.dumps(bstack11l11l1l_opy_))
    browser = self.connect(bstack1111l1l11_opy_)
    return browser
except Exception as e:
    pass
def bstack11l1l1l1_opy_():
    global bstack1l1ll1ll_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        BrowserType.launch = bstack1ll1l1lll_opy_
        bstack1l1ll1ll_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1lll11ll11_opy_
      bstack1l1ll1ll_opy_ = True
    except Exception as e:
      pass
def bstack1ll111ll1_opy_(context, bstack11ll1l11l_opy_):
  try:
    context.page.evaluate(bstack1l1l11l_opy_ (u"ࠥࡣࠥࡃ࠾ࠡࡽࢀࠦੋ"), bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡰࡤࡱࡪࠨ࠺ࠨੌ")+ json.dumps(bstack11ll1l11l_opy_) + bstack1l1l11l_opy_ (u"ࠧࢃࡽ੍ࠣ"))
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠡࡽࢀࠦ੎"), e)
def bstack1111lll1l_opy_(context, message, level):
  try:
    context.page.evaluate(bstack1l1l11l_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ੏"), bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭੐") + json.dumps(message) + bstack1l1l11l_opy_ (u"ࠩ࠯ࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠬੑ") + json.dumps(level) + bstack1l1l11l_opy_ (u"ࠪࢁࢂ࠭੒"))
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠦࡪࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡪࡰࠣࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠠࡢࡰࡱࡳࡹࡧࡴࡪࡱࡱࠤࢀࢃࠢ੓"), e)
def bstack11ll11111_opy_(context, status, message = bstack1l1l11l_opy_ (u"ࠧࠨ੔")):
  try:
    if(status == bstack1l1l11l_opy_ (u"ࠨࡦࡢ࡫࡯ࡩࡩࠨ੕")):
      context.page.evaluate(bstack1l1l11l_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ੖"), bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡳࡧࡤࡷࡴࡴࠢ࠻ࠩ੗") + json.dumps(bstack1l1l11l_opy_ (u"ࠤࡖࡧࡪࡴࡡࡳ࡫ࡲࠤ࡫ࡧࡩ࡭ࡧࡧࠤࡼ࡯ࡴࡩ࠼ࠣࠦ੘") + str(message)) + bstack1l1l11l_opy_ (u"ࠪ࠰ࠧࡹࡴࡢࡶࡸࡷࠧࡀࠧਖ਼") + json.dumps(status) + bstack1l1l11l_opy_ (u"ࠦࢂࢃࠢਗ਼"))
    else:
      context.page.evaluate(bstack1l1l11l_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨਜ਼"), bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡹࡴࡢࡶࡸࡷࠧࡀࠧੜ") + json.dumps(status) + bstack1l1l11l_opy_ (u"ࠢࡾࡿࠥ੝"))
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡴࠡࡵࡨࡷࡸ࡯࡯࡯ࠢࡶࡸࡦࡺࡵࡴࠢࡾࢁࠧਫ਼"), e)
def bstack11111l11l_opy_(self, url):
  global bstack1ll1ll1l_opy_
  try:
    bstack1l1ll11l1_opy_(url)
  except Exception as err:
    logger.debug(bstack1l1llll1_opy_.format(str(err)))
  try:
    bstack1ll1ll1l_opy_(self, url)
  except Exception as e:
    try:
      bstack11ll1lll1_opy_ = str(e)
      if any(err_msg in bstack11ll1lll1_opy_ for err_msg in bstack11l1l11l_opy_):
        bstack1l1ll11l1_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1l1llll1_opy_.format(str(err)))
    raise e
def bstack1lllll1lll_opy_(self):
  global bstack1llllll1l_opy_
  bstack1llllll1l_opy_ = self
  return
def bstack1111l11ll_opy_(self):
  global bstack11l1l1l11_opy_
  bstack11l1l1l11_opy_ = self
  return
def bstack1lll11lll1_opy_(self, test):
  global CONFIG
  global bstack11l1l1l11_opy_
  global bstack1llllll1l_opy_
  global bstack111lll1l1_opy_
  global bstack111ll1111_opy_
  global bstack1l1lllll_opy_
  global bstack11l11llll_opy_
  global bstack11l1ll1ll_opy_
  global bstack111ll111_opy_
  global bstack11ll1lll_opy_
  try:
    if not bstack111lll1l1_opy_:
      with open(os.path.join(os.path.expanduser(bstack1l1l11l_opy_ (u"ࠩࢁࠫ੟")), bstack1l1l11l_opy_ (u"ࠪ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠪ੠"), bstack1l1l11l_opy_ (u"ࠫ࠳ࡹࡥࡴࡵ࡬ࡳࡳ࡯ࡤࡴ࠰ࡷࡼࡹ࠭੡"))) as f:
        bstack11l1l111l_opy_ = json.loads(bstack1l1l11l_opy_ (u"ࠧࢁࠢ੢") + f.read().strip() + bstack1l1l11l_opy_ (u"࠭ࠢࡹࠤ࠽ࠤࠧࡿࠢࠨ੣") + bstack1l1l11l_opy_ (u"ࠢࡾࠤ੤"))
        bstack111lll1l1_opy_ = bstack11l1l111l_opy_[str(threading.get_ident())]
  except:
    pass
  if bstack11ll1lll_opy_:
    for driver in bstack11ll1lll_opy_:
      if bstack111lll1l1_opy_ == driver.session_id:
        if test:
          bstack1llll1ll1_opy_ = str(test.data)
        if not bstack11l11l11l_opy_ and bstack1llll1ll1_opy_:
          bstack11l111lll_opy_ = {
            bstack1l1l11l_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨ੥"): bstack1l1l11l_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪ੦"),
            bstack1l1l11l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭੧"): {
              bstack1l1l11l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ੨"): bstack1llll1ll1_opy_
            }
          }
          bstack1l1111111_opy_ = bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪ੩").format(json.dumps(bstack11l111lll_opy_))
          driver.execute_script(bstack1l1111111_opy_)
        if bstack111ll1111_opy_:
          bstack1ll1lllll_opy_ = {
            bstack1l1l11l_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭੪"): bstack1l1l11l_opy_ (u"ࠧࡢࡰࡱࡳࡹࡧࡴࡦࠩ੫"),
            bstack1l1l11l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫ੬"): {
              bstack1l1l11l_opy_ (u"ࠩࡧࡥࡹࡧࠧ੭"): bstack1llll1ll1_opy_ + bstack1l1l11l_opy_ (u"ࠪࠤࡵࡧࡳࡴࡧࡧࠥࠬ੮"),
              bstack1l1l11l_opy_ (u"ࠫࡱ࡫ࡶࡦ࡮ࠪ੯"): bstack1l1l11l_opy_ (u"ࠬ࡯࡮ࡧࡱࠪੰ")
            }
          }
          bstack11l111lll_opy_ = {
            bstack1l1l11l_opy_ (u"࠭ࡡࡤࡶ࡬ࡳࡳ࠭ੱ"): bstack1l1l11l_opy_ (u"ࠧࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠪੲ"),
            bstack1l1l11l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫੳ"): {
              bstack1l1l11l_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩੴ"): bstack1l1l11l_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪੵ")
            }
          }
          if bstack111ll1111_opy_.status == bstack1l1l11l_opy_ (u"ࠫࡕࡇࡓࡔࠩ੶"):
            bstack1111ll1l_opy_ = bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪ੷").format(json.dumps(bstack1ll1lllll_opy_))
            driver.execute_script(bstack1111ll1l_opy_)
            bstack1l1111111_opy_ = bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫ੸").format(json.dumps(bstack11l111lll_opy_))
            driver.execute_script(bstack1l1111111_opy_)
          elif bstack111ll1111_opy_.status == bstack1l1l11l_opy_ (u"ࠧࡇࡃࡌࡐࠬ੹"):
            reason = bstack1l1l11l_opy_ (u"ࠣࠤ੺")
            bstack1l111l1ll_opy_ = bstack1llll1ll1_opy_ + bstack1l1l11l_opy_ (u"ࠩࠣࡪࡦ࡯࡬ࡦࡦࠪ੻")
            if bstack111ll1111_opy_.message:
              reason = str(bstack111ll1111_opy_.message)
              bstack1l111l1ll_opy_ = bstack1l111l1ll_opy_ + bstack1l1l11l_opy_ (u"ࠪࠤࡼ࡯ࡴࡩࠢࡨࡶࡷࡵࡲ࠻ࠢࠪ੼") + reason
            bstack1ll1lllll_opy_[bstack1l1l11l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧ੽")] = {
              bstack1l1l11l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫ੾"): bstack1l1l11l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ੿"),
              bstack1l1l11l_opy_ (u"ࠧࡥࡣࡷࡥࠬ઀"): bstack1l111l1ll_opy_
            }
            bstack11l111lll_opy_[bstack1l1l11l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫઁ")] = {
              bstack1l1l11l_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩં"): bstack1l1l11l_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪઃ"),
              bstack1l1l11l_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫ઄"): reason
            }
            bstack1111ll1l_opy_ = bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪઅ").format(json.dumps(bstack1ll1lllll_opy_))
            driver.execute_script(bstack1111ll1l_opy_)
            bstack1l1111111_opy_ = bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࢀࠫઆ").format(json.dumps(bstack11l111lll_opy_))
            driver.execute_script(bstack1l1111111_opy_)
  elif bstack111lll1l1_opy_:
    try:
      data = {}
      bstack1llll1ll1_opy_ = None
      if test:
        bstack1llll1ll1_opy_ = str(test.data)
      if not bstack11l11l11l_opy_ and bstack1llll1ll1_opy_:
        data[bstack1l1l11l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬઇ")] = bstack1llll1ll1_opy_
      if bstack111ll1111_opy_:
        if bstack111ll1111_opy_.status == bstack1l1l11l_opy_ (u"ࠨࡒࡄࡗࡘ࠭ઈ"):
          data[bstack1l1l11l_opy_ (u"ࠩࡶࡸࡦࡺࡵࡴࠩઉ")] = bstack1l1l11l_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪઊ")
        elif bstack111ll1111_opy_.status == bstack1l1l11l_opy_ (u"ࠫࡋࡇࡉࡍࠩઋ"):
          data[bstack1l1l11l_opy_ (u"ࠬࡹࡴࡢࡶࡸࡷࠬઌ")] = bstack1l1l11l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ઍ")
          if bstack111ll1111_opy_.message:
            data[bstack1l1l11l_opy_ (u"ࠧࡳࡧࡤࡷࡴࡴࠧ઎")] = str(bstack111ll1111_opy_.message)
      user = CONFIG[bstack1l1l11l_opy_ (u"ࠨࡷࡶࡩࡷࡔࡡ࡮ࡧࠪએ")]
      key = CONFIG[bstack1l1l11l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬઐ")]
      url = bstack1l1l11l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࢀࢃ࠺ࡼࡿࡃࡥࡵ࡯࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡥࡺࡺ࡯࡮ࡣࡷࡩ࠴ࡹࡥࡴࡵ࡬ࡳࡳࡹ࠯ࡼࡿ࠱࡮ࡸࡵ࡮ࠨઑ").format(user, key, bstack111lll1l1_opy_)
      headers = {
        bstack1l1l11l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲ࡺࡹࡱࡧࠪ઒"): bstack1l1l11l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨઓ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers)
    except Exception as e:
      logger.error(bstack1ll1111l_opy_.format(str(e)))
  if bstack11l1l1l11_opy_:
    bstack11l1ll1ll_opy_(bstack11l1l1l11_opy_)
  if bstack1llllll1l_opy_:
    bstack111ll111_opy_(bstack1llllll1l_opy_)
  bstack11l11llll_opy_(self, test)
def bstack111llll1_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack1ll1lll11l_opy_
  bstack1ll1lll11l_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack111ll1111_opy_
  bstack111ll1111_opy_ = self._test
def bstack11ll1llll_opy_():
  global bstack1llll11l1_opy_
  try:
    if os.path.exists(bstack1llll11l1_opy_):
      os.remove(bstack1llll11l1_opy_)
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡦࡨࡰࡪࡺࡩ࡯ࡩࠣࡶࡴࡨ࡯ࡵࠢࡵࡩࡵࡵࡲࡵࠢࡩ࡭ࡱ࡫࠺ࠡࠩઔ") + str(e))
def bstack1lll1ll11_opy_():
  global bstack1llll11l1_opy_
  bstack1ll1lll1_opy_ = {}
  try:
    if not os.path.isfile(bstack1llll11l1_opy_):
      with open(bstack1llll11l1_opy_, bstack1l1l11l_opy_ (u"ࠧࡸࠩક")):
        pass
      with open(bstack1llll11l1_opy_, bstack1l1l11l_opy_ (u"ࠣࡹ࠮ࠦખ")) as outfile:
        json.dump({}, outfile)
    if os.path.exists(bstack1llll11l1_opy_):
      bstack1ll1lll1_opy_ = json.load(open(bstack1llll11l1_opy_, bstack1l1l11l_opy_ (u"ࠩࡵࡦࠬગ")))
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡸࡥࡢࡦ࡬ࡲ࡬ࠦࡲࡰࡤࡲࡸࠥࡸࡥࡱࡱࡵࡸࠥ࡬ࡩ࡭ࡧ࠽ࠤࠬઘ") + str(e))
  finally:
    return bstack1ll1lll1_opy_
def bstack1lllll111_opy_(platform_index, item_index):
  global bstack1llll11l1_opy_
  try:
    bstack1ll1lll1_opy_ = bstack1lll1ll11_opy_()
    bstack1ll1lll1_opy_[item_index] = platform_index
    with open(bstack1llll11l1_opy_, bstack1l1l11l_opy_ (u"ࠦࡼ࠱ࠢઙ")) as outfile:
      json.dump(bstack1ll1lll1_opy_, outfile)
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡸࡴ࡬ࡸ࡮ࡴࡧࠡࡶࡲࠤࡷࡵࡢࡰࡶࠣࡶࡪࡶ࡯ࡳࡶࠣࡪ࡮ࡲࡥ࠻ࠢࠪચ") + str(e))
def bstack1l1ll11ll_opy_(bstack111l1lll_opy_):
  global CONFIG
  bstack11l11ll11_opy_ = bstack1l1l11l_opy_ (u"࠭ࠧછ")
  if not bstack1l1l11l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪજ") in CONFIG:
    logger.info(bstack1l1l11l_opy_ (u"ࠨࡐࡲࠤࡵࡲࡡࡵࡨࡲࡶࡲࡹࠠࡱࡣࡶࡷࡪࡪࠠࡶࡰࡤࡦࡱ࡫ࠠࡵࡱࠣ࡫ࡪࡴࡥࡳࡣࡷࡩࠥࡸࡥࡱࡱࡵࡸࠥ࡬࡯ࡳࠢࡕࡳࡧࡵࡴࠡࡴࡸࡲࠬઝ"))
  try:
    platform = CONFIG[bstack1l1l11l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬઞ")][bstack111l1lll_opy_]
    if bstack1l1l11l_opy_ (u"ࠪࡳࡸ࠭ટ") in platform:
      bstack11l11ll11_opy_ += str(platform[bstack1l1l11l_opy_ (u"ࠫࡴࡹࠧઠ")]) + bstack1l1l11l_opy_ (u"ࠬ࠲ࠠࠨડ")
    if bstack1l1l11l_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩઢ") in platform:
      bstack11l11ll11_opy_ += str(platform[bstack1l1l11l_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪણ")]) + bstack1l1l11l_opy_ (u"ࠨ࠮ࠣࠫત")
    if bstack1l1l11l_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࡐࡤࡱࡪ࠭થ") in platform:
      bstack11l11ll11_opy_ += str(platform[bstack1l1l11l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧદ")]) + bstack1l1l11l_opy_ (u"ࠫ࠱ࠦࠧધ")
    if bstack1l1l11l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧન") in platform:
      bstack11l11ll11_opy_ += str(platform[bstack1l1l11l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ઩")]) + bstack1l1l11l_opy_ (u"ࠧ࠭ࠢࠪપ")
    if bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ફ") in platform:
      bstack11l11ll11_opy_ += str(platform[bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧબ")]) + bstack1l1l11l_opy_ (u"ࠪ࠰ࠥ࠭ભ")
    if bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬમ") in platform:
      bstack11l11ll11_opy_ += str(platform[bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭ય")]) + bstack1l1l11l_opy_ (u"࠭ࠬࠡࠩર")
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠧࡔࡱࡰࡩࠥ࡫ࡲࡳࡱࡵࠤ࡮ࡴࠠࡨࡧࡱࡩࡷࡧࡴࡪࡰࡪࠤࡵࡲࡡࡵࡨࡲࡶࡲࠦࡳࡵࡴ࡬ࡲ࡬ࠦࡦࡰࡴࠣࡶࡪࡶ࡯ࡳࡶࠣ࡫ࡪࡴࡥࡳࡣࡷ࡭ࡴࡴࠧ઱") + str(e))
  finally:
    if bstack11l11ll11_opy_[len(bstack11l11ll11_opy_) - 2:] == bstack1l1l11l_opy_ (u"ࠨ࠮ࠣࠫલ"):
      bstack11l11ll11_opy_ = bstack11l11ll11_opy_[:-2]
    return bstack11l11ll11_opy_
def bstack111lll11_opy_(path, bstack11l11ll11_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack1l1l11l1_opy_ = ET.parse(path)
    bstack1l1111l1_opy_ = bstack1l1l11l1_opy_.getroot()
    bstack11l1lllll_opy_ = None
    for suite in bstack1l1111l1_opy_.iter(bstack1l1l11l_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨળ")):
      if bstack1l1l11l_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ઴") in suite.attrib:
        suite.attrib[bstack1l1l11l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩવ")] += bstack1l1l11l_opy_ (u"ࠬࠦࠧશ") + bstack11l11ll11_opy_
        bstack11l1lllll_opy_ = suite
    bstack1ll1ll1111_opy_ = None
    for robot in bstack1l1111l1_opy_.iter(bstack1l1l11l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬષ")):
      bstack1ll1ll1111_opy_ = robot
    bstack1llllll1l1_opy_ = len(bstack1ll1ll1111_opy_.findall(bstack1l1l11l_opy_ (u"ࠧࡴࡷ࡬ࡸࡪ࠭સ")))
    if bstack1llllll1l1_opy_ == 1:
      bstack1ll1ll1111_opy_.remove(bstack1ll1ll1111_opy_.findall(bstack1l1l11l_opy_ (u"ࠨࡵࡸ࡭ࡹ࡫ࠧહ"))[0])
      bstack1l1l1lll_opy_ = ET.Element(bstack1l1l11l_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨ઺"), attrib={bstack1l1l11l_opy_ (u"ࠪࡲࡦࡳࡥࠨ઻"): bstack1l1l11l_opy_ (u"ࠫࡘࡻࡩࡵࡧࡶ઼ࠫ"), bstack1l1l11l_opy_ (u"ࠬ࡯ࡤࠨઽ"): bstack1l1l11l_opy_ (u"࠭ࡳ࠱ࠩા")})
      bstack1ll1ll1111_opy_.insert(1, bstack1l1l1lll_opy_)
      bstack1lll1llll_opy_ = None
      for suite in bstack1ll1ll1111_opy_.iter(bstack1l1l11l_opy_ (u"ࠧࡴࡷ࡬ࡸࡪ࠭િ")):
        bstack1lll1llll_opy_ = suite
      bstack1lll1llll_opy_.append(bstack11l1lllll_opy_)
      bstack1l1lll11l_opy_ = None
      for status in bstack11l1lllll_opy_.iter(bstack1l1l11l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨી")):
        bstack1l1lll11l_opy_ = status
      bstack1lll1llll_opy_.append(bstack1l1lll11l_opy_)
    bstack1l1l11l1_opy_.write(path)
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡵࡧࡲࡴ࡫ࡱ࡫ࠥࡽࡨࡪ࡮ࡨࠤ࡬࡫࡮ࡦࡴࡤࡸ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠧુ") + str(e))
def bstack11l1l111_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack1l11llll1_opy_
  global CONFIG
  if bstack1l1l11l_opy_ (u"ࠥࡴࡾࡺࡨࡰࡰࡳࡥࡹ࡮ࠢૂ") in options:
    del options[bstack1l1l11l_opy_ (u"ࠦࡵࡿࡴࡩࡱࡱࡴࡦࡺࡨࠣૃ")]
  bstack1ll1ll1l1_opy_ = bstack1lll1ll11_opy_()
  for bstack1ll1l1l1_opy_ in bstack1ll1ll1l1_opy_.keys():
    path = os.path.join(os.getcwd(), bstack1l1l11l_opy_ (u"ࠬࡶࡡࡣࡱࡷࡣࡷ࡫ࡳࡶ࡮ࡷࡷࠬૄ"), str(bstack1ll1l1l1_opy_), bstack1l1l11l_opy_ (u"࠭࡯ࡶࡶࡳࡹࡹ࠴ࡸ࡮࡮ࠪૅ"))
    bstack111lll11_opy_(path, bstack1l1ll11ll_opy_(bstack1ll1ll1l1_opy_[bstack1ll1l1l1_opy_]))
  bstack11ll1llll_opy_()
  return bstack1l11llll1_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack11lllll11_opy_(self, ff_profile_dir):
  global bstack1l1lll111_opy_
  if not ff_profile_dir:
    return None
  return bstack1l1lll111_opy_(self, ff_profile_dir)
def bstack1lll1l11l_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack11l1ll111_opy_
  bstack1l1lll1l_opy_ = []
  if bstack1l1l11l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪ૆") in CONFIG:
    bstack1l1lll1l_opy_ = CONFIG[bstack1l1l11l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫે")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack1l1l11l_opy_ (u"ࠤࡦࡳࡲࡳࡡ࡯ࡦࠥૈ")],
      pabot_args[bstack1l1l11l_opy_ (u"ࠥࡺࡪࡸࡢࡰࡵࡨࠦૉ")],
      argfile,
      pabot_args.get(bstack1l1l11l_opy_ (u"ࠦ࡭࡯ࡶࡦࠤ૊")),
      pabot_args[bstack1l1l11l_opy_ (u"ࠧࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠣો")],
      platform[0],
      bstack11l1ll111_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack1l1l11l_opy_ (u"ࠨࡡࡳࡩࡸࡱࡪࡴࡴࡧ࡫࡯ࡩࡸࠨૌ")] or [(bstack1l1l11l_opy_ (u"્ࠢࠣ"), None)]
    for platform in enumerate(bstack1l1lll1l_opy_)
  ]
def bstack1l111lll_opy_(self, datasources, outs_dir, options,
                        execution_item, command, verbose, argfile,
                        hive=None, processes=0, platform_index=0, bstack1l11ll1l1_opy_=bstack1l1l11l_opy_ (u"ࠨࠩ૎")):
  global bstack1l11l111l_opy_
  self.platform_index = platform_index
  self.bstack1l11l11l1_opy_ = bstack1l11ll1l1_opy_
  bstack1l11l111l_opy_(self, datasources, outs_dir, options,
                      execution_item, command, verbose, argfile, hive, processes)
def bstack1l1l1l11_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack1lll1l1l11_opy_
  global bstack111ll11l1_opy_
  if not bstack1l1l11l_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ૏") in item.options:
    item.options[bstack1l1l11l_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬૐ")] = []
  for v in item.options[bstack1l1l11l_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭૑")]:
    if bstack1l1l11l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛ࠫ૒") in v:
      item.options[bstack1l1l11l_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ૓")].remove(v)
    if bstack1l1l11l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡃࡍࡋࡄࡖࡌ࡙ࠧ૔") in v:
      item.options[bstack1l1l11l_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ૕")].remove(v)
  item.options[bstack1l1l11l_opy_ (u"ࠩࡹࡥࡷ࡯ࡡࡣ࡮ࡨࠫ૖")].insert(0, bstack1l1l11l_opy_ (u"ࠪࡆࡘ࡚ࡁࡄࡍࡓࡐࡆ࡚ࡆࡐࡔࡐࡍࡓࡊࡅ࡙࠼ࡾࢁࠬ૗").format(item.platform_index))
  item.options[bstack1l1l11l_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭૘")].insert(0, bstack1l1l11l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡉࡋࡆࡍࡑࡆࡅࡑࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓ࠼ࡾࢁࠬ૙").format(item.bstack1l11l11l1_opy_))
  if bstack111ll11l1_opy_:
    item.options[bstack1l1l11l_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ૚")].insert(0, bstack1l1l11l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡃࡍࡋࡄࡖࡌ࡙࠺ࡼࡿࠪ૛").format(bstack111ll11l1_opy_))
  return bstack1lll1l1l11_opy_(caller_id, datasources, is_last, item, outs_dir)
def bstack1111l1ll1_opy_(command, item_index):
  global bstack111ll11l1_opy_
  if bstack111ll11l1_opy_:
    command[0] = command[0].replace(bstack1l1l11l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ૜"), bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠮ࡵࡧ࡯ࠥࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱࠦ࠭࠮ࡤࡶࡸࡦࡩ࡫ࡠ࡫ࡷࡩࡲࡥࡩ࡯ࡦࡨࡼࠥ࠭૝") + str(
      item_index) + bstack1l1l11l_opy_ (u"ࠪࠤࠬ૞") + bstack111ll11l1_opy_, 1)
  else:
    command[0] = command[0].replace(bstack1l1l11l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪ૟"),
                                    bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠱ࡸࡪ࡫ࠡࡴࡲࡦࡴࡺ࠭ࡪࡰࡷࡩࡷࡴࡡ࡭ࠢ࠰࠱ࡧࡹࡴࡢࡥ࡮ࡣ࡮ࡺࡥ࡮ࡡ࡬ࡲࡩ࡫ࡸࠡࠩૠ") + str(item_index), 1)
def bstack1l11ll1l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1llll111_opy_
  bstack1111l1ll1_opy_(command, item_index)
  return bstack1llll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
def bstack1lll1ll11l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1llll111_opy_
  bstack1111l1ll1_opy_(command, item_index)
  return bstack1llll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
def bstack1lll1l11l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1llll111_opy_
  bstack1111l1ll1_opy_(command, item_index)
  return bstack1llll111_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
def bstack1ll1ll111l_opy_(self, runner, quiet=False, capture=True):
  global bstack1l11llll_opy_
  bstack11111llll_opy_ = bstack1l11llll_opy_(self, runner, quiet=False, capture=True)
  if self.exception:
    if not hasattr(runner, bstack1l1l11l_opy_ (u"࠭ࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࡡࡤࡶࡷ࠭ૡ")):
      runner.exception_arr = []
    if not hasattr(runner, bstack1l1l11l_opy_ (u"ࠧࡦࡺࡦࡣࡹࡸࡡࡤࡧࡥࡥࡨࡱ࡟ࡢࡴࡵࠫૢ")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack11111llll_opy_
def bstack11ll11l1l_opy_(self, name, context, *args):
  global bstack1lll1lll_opy_
  if name == bstack1l1l11l_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡨࡨࡥࡹࡻࡲࡦࠩૣ"):
    bstack1lll1lll_opy_(self, name, context, *args)
    try:
      if not bstack11l11l11l_opy_:
        bstack1l11ll1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack1lllll1ll1_opy_(bstack1l1l11l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ૤")) else context.browser
        bstack11ll1l11l_opy_ = str(self.feature.name)
        bstack1ll111ll1_opy_(context, bstack11ll1l11l_opy_)
        bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠠࠨ૥") + json.dumps(bstack11ll1l11l_opy_) + bstack1l1l11l_opy_ (u"ࠫࢂࢃࠧ૦"))
      self.driver_before_scenario = False
    except Exception as e:
      logger.debug(bstack1l1l11l_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨࠤ࡮ࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡧࡧࡤࡸࡺࡸࡥ࠻ࠢࡾࢁࠬ૧").format(str(e)))
  elif name == bstack1l1l11l_opy_ (u"࠭ࡢࡦࡨࡲࡶࡪࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠨ૨"):
    bstack1lll1lll_opy_(self, name, context, *args)
    try:
      if not hasattr(self, bstack1l1l11l_opy_ (u"ࠧࡥࡴ࡬ࡺࡪࡸ࡟ࡣࡧࡩࡳࡷ࡫࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩ૩")):
        self.driver_before_scenario = True
      if (not bstack11l11l11l_opy_):
        scenario_name = args[0].name
        feature_name = bstack11ll1l11l_opy_ = str(self.feature.name)
        bstack11ll1l11l_opy_ = feature_name + bstack1l1l11l_opy_ (u"ࠨࠢ࠰ࠤࠬ૪") + scenario_name
        bstack1l11ll1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack1lllll1ll1_opy_(bstack1l1l11l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ૫")) else context.browser
        if self.driver_before_scenario:
          bstack1ll111ll1_opy_(context, bstack11ll1l11l_opy_)
          bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢ࡯ࡣࡰࡩࠧࡀࠠࠨ૬") + json.dumps(bstack11ll1l11l_opy_) + bstack1l1l11l_opy_ (u"ࠫࢂࢃࠧ૭"))
    except Exception as e:
      logger.debug(bstack1l1l11l_opy_ (u"ࠬࡌࡡࡪ࡮ࡨࡨࠥࡺ࡯ࠡࡵࡨࡸࠥࡹࡥࡴࡵ࡬ࡳࡳࠦ࡮ࡢ࡯ࡨࠤ࡮ࡴࠠࡣࡧࡩࡳࡷ࡫ࠠࡴࡥࡨࡲࡦࡸࡩࡰ࠼ࠣࡿࢂ࠭૮").format(str(e)))
  elif name == bstack1l1l11l_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠧ૯"):
    try:
      bstack1ll1l11l1_opy_ = args[0].status.name
      bstack1l11ll1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack1l1l11l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱࡓࡦࡵࡶ࡭ࡴࡴࡄࡳ࡫ࡹࡩࡷ࠭૰") in threading.current_thread().__dict__.keys() else context.browser
      if str(bstack1ll1l11l1_opy_).lower() == bstack1l1l11l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨ૱"):
        bstack1l1l11ll1_opy_ = bstack1l1l11l_opy_ (u"ࠩࠪ૲")
        bstack11l1l1ll_opy_ = bstack1l1l11l_opy_ (u"ࠪࠫ૳")
        bstack1llll1l1l_opy_ = bstack1l1l11l_opy_ (u"ࠫࠬ૴")
        try:
          import traceback
          bstack1l1l11ll1_opy_ = self.exception.__class__.__name__
          bstack1lll1llll1_opy_ = traceback.format_tb(self.exc_traceback)
          bstack11l1l1ll_opy_ = bstack1l1l11l_opy_ (u"ࠬࠦࠧ૵").join(bstack1lll1llll1_opy_)
          bstack1llll1l1l_opy_ = bstack1lll1llll1_opy_[-1]
        except Exception as e:
          logger.debug(bstack1l1l1l1l1_opy_.format(str(e)))
        bstack1l1l11ll1_opy_ += bstack1llll1l1l_opy_
        bstack1111lll1l_opy_(context, json.dumps(str(args[0].name) + bstack1l1l11l_opy_ (u"ࠨࠠ࠮ࠢࡉࡥ࡮ࡲࡥࡥࠣ࡟ࡲࠧ૶") + str(bstack11l1l1ll_opy_)),
                            bstack1l1l11l_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨ૷"))
        if self.driver_before_scenario:
          bstack11ll11111_opy_(context, bstack1l1l11l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ૸"), bstack1l1l11ll1_opy_)
          bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡥࡣࡷࡥࠧࡀࠧૹ") + json.dumps(str(args[0].name) + bstack1l1l11l_opy_ (u"ࠥࠤ࠲ࠦࡆࡢ࡫࡯ࡩࡩࠧ࡜࡯ࠤૺ") + str(bstack11l1l1ll_opy_)) + bstack1l1l11l_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤࡨࡶࡷࡵࡲࠣࡿࢀࠫૻ"))
        if self.driver_before_scenario:
          bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡸࡺࡡࡵࡷࡶࠦ࠿ࠨࡦࡢ࡫࡯ࡩࡩࠨࠬࠡࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠤࠬૼ") + json.dumps(bstack1l1l11l_opy_ (u"ࠨࡓࡤࡧࡱࡥࡷ࡯࡯ࠡࡨࡤ࡭ࡱ࡫ࡤࠡࡹ࡬ࡸ࡭ࡀࠠ࡝ࡰࠥ૽") + str(bstack1l1l11ll1_opy_)) + bstack1l1l11l_opy_ (u"ࠧࡾࡿࠪ૾"))
      else:
        bstack1111lll1l_opy_(context, bstack1l1l11l_opy_ (u"ࠣࡒࡤࡷࡸ࡫ࡤࠢࠤ૿"), bstack1l1l11l_opy_ (u"ࠤ࡬ࡲ࡫ࡵࠢ଀"))
        if self.driver_before_scenario:
          bstack11ll11111_opy_(context, bstack1l1l11l_opy_ (u"ࠥࡴࡦࡹࡳࡦࡦࠥଁ"))
        bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩଂ") + json.dumps(str(args[0].name) + bstack1l1l11l_opy_ (u"ࠧࠦ࠭ࠡࡒࡤࡷࡸ࡫ࡤࠢࠤଃ")) + bstack1l1l11l_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦ࡮ࡴࡦࡰࠤࢀࢁࠬ଄"))
        if self.driver_before_scenario:
          bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠣࡲࡤࡷࡸ࡫ࡤࠣࡿࢀࠫଅ"))
    except Exception as e:
      logger.debug(bstack1l1l11l_opy_ (u"ࠨࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡲࡧࡲ࡬ࠢࡶࡩࡸࡹࡩࡰࡰࠣࡷࡹࡧࡴࡶࡵࠣ࡭ࡳࠦࡡࡧࡶࡨࡶࠥ࡬ࡥࡢࡶࡸࡶࡪࡀࠠࡼࡿࠪଆ").format(str(e)))
  elif name == bstack1l1l11l_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡨࡨࡥࡹࡻࡲࡦࠩଇ"):
    try:
      bstack1l11ll1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack1lllll1ll1_opy_(bstack1l1l11l_opy_ (u"ࠪࡦࡸࡺࡡࡤ࡭ࡖࡩࡸࡹࡩࡰࡰࡇࡶ࡮ࡼࡥࡳࠩଈ")) else context.browser
      if context.failed is True:
        bstack1lll1lll1_opy_ = []
        bstack1l11lll11_opy_ = []
        bstack1l11lll1l_opy_ = []
        bstack1l1l111ll_opy_ = bstack1l1l11l_opy_ (u"ࠫࠬଉ")
        try:
          import traceback
          for exc in self.exception_arr:
            bstack1lll1lll1_opy_.append(exc.__class__.__name__)
          for exc_tb in self.exc_traceback_arr:
            bstack1lll1llll1_opy_ = traceback.format_tb(exc_tb)
            bstack11ll1ll1_opy_ = bstack1l1l11l_opy_ (u"ࠬࠦࠧଊ").join(bstack1lll1llll1_opy_)
            bstack1l11lll11_opy_.append(bstack11ll1ll1_opy_)
            bstack1l11lll1l_opy_.append(bstack1lll1llll1_opy_[-1])
        except Exception as e:
          logger.debug(bstack1l1l1l1l1_opy_.format(str(e)))
        bstack1l1l11ll1_opy_ = bstack1l1l11l_opy_ (u"࠭ࠧଋ")
        for i in range(len(bstack1lll1lll1_opy_)):
          bstack1l1l11ll1_opy_ += bstack1lll1lll1_opy_[i] + bstack1l11lll1l_opy_[i] + bstack1l1l11l_opy_ (u"ࠧ࡝ࡰࠪଌ")
        bstack1l1l111ll_opy_ = bstack1l1l11l_opy_ (u"ࠨࠢࠪ଍").join(bstack1l11lll11_opy_)
        if not self.driver_before_scenario:
          bstack1111lll1l_opy_(context, bstack1l1l111ll_opy_, bstack1l1l11l_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣ଎"))
          bstack11ll11111_opy_(context, bstack1l1l11l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥଏ"), bstack1l1l11ll1_opy_)
          bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩଐ") + json.dumps(bstack1l1l111ll_opy_) + bstack1l1l11l_opy_ (u"ࠬ࠲ࠠࠣ࡮ࡨࡺࡪࡲࠢ࠻ࠢࠥࡩࡷࡸ࡯ࡳࠤࢀࢁࠬ଑"))
          bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠤ࠯ࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࠧࡹࡴࡢࡶࡸࡷࠧࡀࠢࡧࡣ࡬ࡰࡪࡪࠢ࠭ࠢࠥࡶࡪࡧࡳࡰࡰࠥ࠾ࠥ࠭଒") + json.dumps(bstack1l1l11l_opy_ (u"ࠢࡔࡱࡰࡩࠥࡹࡣࡦࡰࡤࡶ࡮ࡵࡳࠡࡨࡤ࡭ࡱ࡫ࡤ࠻ࠢ࡟ࡲࠧଓ") + str(bstack1l1l11ll1_opy_)) + bstack1l1l11l_opy_ (u"ࠨࡿࢀࠫଔ"))
      else:
        if not self.driver_before_scenario:
          bstack1111lll1l_opy_(context, bstack1l1l11l_opy_ (u"ࠤࡉࡩࡦࡺࡵࡳࡧ࠽ࠤࠧକ") + str(self.feature.name) + bstack1l1l11l_opy_ (u"ࠥࠤࡵࡧࡳࡴࡧࡧࠥࠧଖ"), bstack1l1l11l_opy_ (u"ࠦ࡮ࡴࡦࡰࠤଗ"))
          bstack11ll11111_opy_(context, bstack1l1l11l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧଘ"))
          bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫଙ") + json.dumps(bstack1l1l11l_opy_ (u"ࠢࡇࡧࡤࡸࡺࡸࡥ࠻ࠢࠥଚ") + str(self.feature.name) + bstack1l1l11l_opy_ (u"ࠣࠢࡳࡥࡸࡹࡥࡥࠣࠥଛ")) + bstack1l1l11l_opy_ (u"ࠩ࠯ࠤࠧࡲࡥࡷࡧ࡯ࠦ࠿ࠦࠢࡪࡰࡩࡳࠧࢃࡽࠨଜ"))
          bstack1l11ll1ll_opy_.execute_script(bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡶࡸࡦࡺࡵࡴࠤ࠽ࠦࡵࡧࡳࡴࡧࡧࠦࢂࢃࠧଝ"))
    except Exception as e:
      logger.debug(bstack1l1l11l_opy_ (u"ࠫࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠ࡮ࡣࡵ࡯ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡳࡵࡣࡷࡹࡸࠦࡩ࡯ࠢࡤࡪࡹ࡫ࡲࠡࡨࡨࡥࡹࡻࡲࡦ࠼ࠣࡿࢂ࠭ଞ").format(str(e)))
  else:
    bstack1lll1lll_opy_(self, name, context, *args)
  if name in [bstack1l1l11l_opy_ (u"ࠬࡧࡦࡵࡧࡵࡣ࡫࡫ࡡࡵࡷࡵࡩࠬଟ"), bstack1l1l11l_opy_ (u"࠭ࡡࡧࡶࡨࡶࡤࡹࡣࡦࡰࡤࡶ࡮ࡵࠧଠ")]:
    bstack1lll1lll_opy_(self, name, context, *args)
    if (name == bstack1l1l11l_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡳࡤࡧࡱࡥࡷ࡯࡯ࠨଡ") and self.driver_before_scenario) or (
            name == bstack1l1l11l_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡧࡧࡤࡸࡺࡸࡥࠨଢ") and not self.driver_before_scenario):
      try:
        bstack1l11ll1ll_opy_ = threading.current_thread().bstackSessionDriver if bstack1lllll1ll1_opy_(bstack1l1l11l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨଣ")) else context.browser
        bstack1l11ll1ll_opy_.quit()
      except Exception:
        pass
def bstack1lll1ll1l_opy_(config, startdir):
  return bstack1l1l11l_opy_ (u"ࠥࡨࡷ࡯ࡶࡦࡴ࠽ࠤࢀ࠶ࡽࠣତ").format(bstack1l1l11l_opy_ (u"ࠦࡇࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࠥଥ"))
class Notset:
  def __repr__(self):
    return bstack1l1l11l_opy_ (u"ࠧࡂࡎࡐࡖࡖࡉ࡙ࡄࠢଦ")
notset = Notset()
def bstack1l1l11ll_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack1lll11l11l_opy_
  if str(name).lower() == bstack1l1l11l_opy_ (u"࠭ࡤࡳ࡫ࡹࡩࡷ࠭ଧ"):
    return bstack1l1l11l_opy_ (u"ࠢࡃࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࠨନ")
  else:
    return bstack1lll11l11l_opy_(self, name, default, skip)
def bstack1ll1lllll1_opy_(item, when):
  global bstack11ll111l_opy_
  try:
    bstack11ll111l_opy_(item, when)
  except Exception as e:
    pass
def bstack111l11lll_opy_():
  return
def bstack1l11l11l_opy_(type, name, status, reason, bstack1ll1111l1_opy_, bstack1lll1l1ll1_opy_):
  bstack11l111lll_opy_ = {
    bstack1l1l11l_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨ଩"): type,
    bstack1l1l11l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬପ"): {}
  }
  if type == bstack1l1l11l_opy_ (u"ࠪࡥࡳࡴ࡯ࡵࡣࡷࡩࠬଫ"):
    bstack11l111lll_opy_[bstack1l1l11l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧବ")][bstack1l1l11l_opy_ (u"ࠬࡲࡥࡷࡧ࡯ࠫଭ")] = bstack1ll1111l1_opy_
    bstack11l111lll_opy_[bstack1l1l11l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩମ")][bstack1l1l11l_opy_ (u"ࠧࡥࡣࡷࡥࠬଯ")] = json.dumps(str(bstack1lll1l1ll1_opy_))
  if type == bstack1l1l11l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩର"):
    bstack11l111lll_opy_[bstack1l1l11l_opy_ (u"ࠩࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠬ଱")][bstack1l1l11l_opy_ (u"ࠪࡲࡦࡳࡥࠨଲ")] = name
  if type == bstack1l1l11l_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠧଳ"):
    bstack11l111lll_opy_[bstack1l1l11l_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ଴")][bstack1l1l11l_opy_ (u"࠭ࡳࡵࡣࡷࡹࡸ࠭ଵ")] = status
    if status == bstack1l1l11l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧଶ"):
      bstack11l111lll_opy_[bstack1l1l11l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫଷ")][bstack1l1l11l_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩସ")] = json.dumps(str(reason))
  bstack1l1111111_opy_ = bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࡽࠨହ").format(json.dumps(bstack11l111lll_opy_))
  return bstack1l1111111_opy_
def bstack111l1l1l_opy_(item, call, rep):
  global bstack111ll1l1l_opy_
  global bstack11ll1lll_opy_
  global bstack11l11l11l_opy_
  name = bstack1l1l11l_opy_ (u"ࠫࠬ଺")
  try:
    if rep.when == bstack1l1l11l_opy_ (u"ࠬࡩࡡ࡭࡮ࠪ଻"):
      bstack111lll1l1_opy_ = threading.current_thread().bstack1111ll111_opy_
      try:
        if not bstack11l11l11l_opy_:
          name = str(rep.nodeid)
          bstack111111ll1_opy_ = bstack1l11l11l_opy_(bstack1l1l11l_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫଼ࠧ"), name, bstack1l1l11l_opy_ (u"ࠧࠨଽ"), bstack1l1l11l_opy_ (u"ࠨࠩା"), bstack1l1l11l_opy_ (u"ࠩࠪି"), bstack1l1l11l_opy_ (u"ࠪࠫୀ"))
          for driver in bstack11ll1lll_opy_:
            if bstack111lll1l1_opy_ == driver.session_id:
              driver.execute_script(bstack111111ll1_opy_)
      except Exception as e:
        logger.debug(bstack1l1l11l_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠥ࡬࡯ࡳࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡳࡦࡵࡶ࡭ࡴࡴ࠺ࠡࡽࢀࠫୁ").format(str(e)))
      try:
        status = bstack1l1l11l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬୂ") if rep.outcome.lower() == bstack1l1l11l_opy_ (u"࠭ࡦࡢ࡫࡯ࡩࡩ࠭ୃ") else bstack1l1l11l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧୄ")
        reason = bstack1l1l11l_opy_ (u"ࠨࠩ୅")
        if (reason != bstack1l1l11l_opy_ (u"ࠤࠥ୆")):
          try:
            if (threading.current_thread().bstackTestErrorMessages == None):
              threading.current_thread().bstackTestErrorMessages = []
          except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
          threading.current_thread().bstackTestErrorMessages.append(str(reason))
        if status == bstack1l1l11l_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪେ"):
          reason = rep.longrepr.reprcrash.message
          if (not threading.current_thread().bstackTestErrorMessages):
            threading.current_thread().bstackTestErrorMessages = []
          threading.current_thread().bstackTestErrorMessages.append(reason)
        level = bstack1l1l11l_opy_ (u"ࠫ࡮ࡴࡦࡰࠩୈ") if status == bstack1l1l11l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬ୉") else bstack1l1l11l_opy_ (u"࠭ࡥࡳࡴࡲࡶࠬ୊")
        data = name + bstack1l1l11l_opy_ (u"ࠧࠡࡲࡤࡷࡸ࡫ࡤࠢࠩୋ") if status == bstack1l1l11l_opy_ (u"ࠨࡲࡤࡷࡸ࡫ࡤࠨୌ") else name + bstack1l1l11l_opy_ (u"ࠩࠣࡪࡦ࡯࡬ࡦࡦࠤࠤ୍ࠬ") + reason
        bstack11ll11l11_opy_ = bstack1l11l11l_opy_(bstack1l1l11l_opy_ (u"ࠪࡥࡳࡴ࡯ࡵࡣࡷࡩࠬ୎"), bstack1l1l11l_opy_ (u"ࠫࠬ୏"), bstack1l1l11l_opy_ (u"ࠬ࠭୐"), bstack1l1l11l_opy_ (u"࠭ࠧ୑"), level, data)
        for driver in bstack11ll1lll_opy_:
          if bstack111lll1l1_opy_ == driver.session_id:
            driver.execute_script(bstack11ll11l11_opy_)
      except Exception as e:
        logger.debug(bstack1l1l11l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡶࡩࡹࡺࡩ࡯ࡩࠣࡷࡪࡹࡳࡪࡱࡱࠤࡨࡵ࡮ࡵࡧࡻࡸࠥ࡬࡯ࡳࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡥࡨࡩࠦࡳࡦࡵࡶ࡭ࡴࡴ࠺ࠡࡽࢀࠫ୒").format(str(e)))
  except Exception as e:
    logger.debug(bstack1l1l11l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣ࡫ࡪࡺࡴࡪࡰࡪࠤࡸࡺࡡࡵࡧࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹ࠳ࡢࡥࡦࠣࡸࡪࡹࡴࠡࡵࡷࡥࡹࡻࡳ࠻ࠢࡾࢁࠬ୓").format(str(e)))
  bstack111ll1l1l_opy_(item, call, rep)
def bstack1l1llll11_opy_(framework_name):
  global bstack11l1l11l1_opy_
  global bstack1l1ll1ll_opy_
  global bstack11llll1l_opy_
  bstack11l1l11l1_opy_ = framework_name
  logger.info(bstack1llll11l1l_opy_.format(bstack11l1l11l1_opy_.split(bstack1l1l11l_opy_ (u"ࠩ࠰ࠫ୔"))[0]))
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    if bstack1ll1ll11l_opy_:
      Service.start = bstack1l1l11lll_opy_
      Service.stop = bstack1llll111l_opy_
      webdriver.Remote.get = bstack11111l11l_opy_
      WebDriver.close = bstack1llll1l1ll_opy_
      WebDriver.quit = bstack1lll11l1ll_opy_
      webdriver.Remote.__init__ = bstack1ll1l111l_opy_
    if not bstack1ll1ll11l_opy_ and bstack1llll1lll1_opy_.on():
      webdriver.Remote.__init__ = bstack1llll1111l_opy_
    bstack1l1ll1ll_opy_ = True
  except Exception as e:
    pass
  bstack11l1l1l1_opy_()
  if not bstack1l1ll1ll_opy_:
    bstack1ll111111_opy_(bstack1l1l11l_opy_ (u"ࠥࡔࡦࡩ࡫ࡢࡩࡨࡷࠥࡴ࡯ࡵࠢ࡬ࡲࡸࡺࡡ࡭࡮ࡨࡨࠧ୕"), bstack1l1l1l1l_opy_)
  if bstack1l1l11l11_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      RemoteConnection._get_proxy_url = bstack1llll1l11l_opy_
    except Exception as e:
      logger.error(bstack111lll1l_opy_.format(str(e)))
  if (bstack1l1l11l_opy_ (u"ࠫࡷࡵࡢࡰࡶࠪୖ") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack11lllll11_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack1111l11ll_opy_
      except Exception as e:
        logger.warn(bstack11ll1l1ll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack1lllll1lll_opy_
      except Exception as e:
        logger.debug(bstack1ll1l1111_opy_ + str(e))
    except Exception as e:
      bstack1ll111111_opy_(e, bstack11ll1l1ll_opy_)
    Output.end_test = bstack1lll11lll1_opy_
    TestStatus.__init__ = bstack111llll1_opy_
    QueueItem.__init__ = bstack1l111lll_opy_
    pabot._create_items = bstack1lll1l11l_opy_
    try:
      from pabot import __version__ as bstack11l1ll1l1_opy_
      if version.parse(bstack11l1ll1l1_opy_) >= version.parse(bstack1l1l11l_opy_ (u"ࠬ࠸࠮࠲࠷࠱࠴ࠬୗ")):
        pabot._run = bstack1lll1l11l1_opy_
      elif version.parse(bstack11l1ll1l1_opy_) >= version.parse(bstack1l1l11l_opy_ (u"࠭࠲࠯࠳࠶࠲࠵࠭୘")):
        pabot._run = bstack1lll1ll11l_opy_
      else:
        pabot._run = bstack1l11ll1l_opy_
    except Exception as e:
      pabot._run = bstack1l11ll1l_opy_
    pabot._create_command_for_execution = bstack1l1l1l11_opy_
    pabot._report_results = bstack11l1l111_opy_
  if bstack1l1l11l_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ୙") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll111111_opy_(e, bstack11l1ll1l_opy_)
    Runner.run_hook = bstack11ll11l1l_opy_
    Step.run = bstack1ll1ll111l_opy_
  if bstack1l1l11l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ୚") in str(framework_name).lower():
    if not bstack1ll1ll11l_opy_:
      return
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack1lll1ll1l_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack111l11lll_opy_
      Config.getoption = bstack1l1l11ll_opy_
    except Exception as e:
      pass
    try:
      from _pytest import runner
      runner._update_current_test_var = bstack1ll1lllll1_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack111l1l1l_opy_
    except Exception as e:
      pass
def bstack11l111l1l_opy_():
  global CONFIG
  if bstack1l1l11l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ୛") in CONFIG and int(CONFIG[bstack1l1l11l_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪଡ଼")]) > 1:
    logger.warn(bstack1ll1l1ll_opy_)
def bstack1lll1111l_opy_(arg):
  bstack1l1llll11_opy_(bstack11111111_opy_)
  from behave.__main__ import main as bstack1l11ll11l_opy_
  bstack1l11ll11l_opy_(arg)
def bstack111l1l111_opy_():
  logger.info(bstack1l1lllll1_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack1l1l11l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪଢ଼"), help=bstack1l1l11l_opy_ (u"ࠬࡍࡥ࡯ࡧࡵࡥࡹ࡫ࠠࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡣࡰࡰࡩ࡭࡬࠭୞"))
  parser.add_argument(bstack1l1l11l_opy_ (u"࠭࠭ࡶࠩୟ"), bstack1l1l11l_opy_ (u"ࠧ࠮࠯ࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠫୠ"), help=bstack1l1l11l_opy_ (u"ࠨ࡛ࡲࡹࡷࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡻࡳࡦࡴࡱࡥࡲ࡫ࠧୡ"))
  parser.add_argument(bstack1l1l11l_opy_ (u"ࠩ࠰࡯ࠬୢ"), bstack1l1l11l_opy_ (u"ࠪ࠱࠲ࡱࡥࡺࠩୣ"), help=bstack1l1l11l_opy_ (u"ࠫ࡞ࡵࡵࡳࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡣࡦࡧࡪࡹࡳࠡ࡭ࡨࡽࠬ୤"))
  parser.add_argument(bstack1l1l11l_opy_ (u"ࠬ࠳ࡦࠨ୥"), bstack1l1l11l_opy_ (u"࠭࠭࠮ࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ୦"), help=bstack1l1l11l_opy_ (u"࡚ࠧࡱࡸࡶࠥࡺࡥࡴࡶࠣࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭୧"))
  bstack111l1l11_opy_ = parser.parse_args()
  try:
    bstack1lllll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡨࡧࡱࡩࡷ࡯ࡣ࠯ࡻࡰࡰ࠳ࡹࡡ࡮ࡲ࡯ࡩࠬ୨")
    if bstack111l1l11_opy_.framework and bstack111l1l11_opy_.framework not in (bstack1l1l11l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩ୩"), bstack1l1l11l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠶ࠫ୪")):
      bstack1lllll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠴ࡹ࡮࡮࠱ࡷࡦࡳࡰ࡭ࡧࠪ୫")
    bstack1l111ll1l_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1lllll1ll_opy_)
    bstack111lllll1_opy_ = open(bstack1l111ll1l_opy_, bstack1l1l11l_opy_ (u"ࠬࡸࠧ୬"))
    bstack11ll1l11_opy_ = bstack111lllll1_opy_.read()
    bstack111lllll1_opy_.close()
    if bstack111l1l11_opy_.username:
      bstack11ll1l11_opy_ = bstack11ll1l11_opy_.replace(bstack1l1l11l_opy_ (u"࡙࠭ࡐࡗࡕࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭୭"), bstack111l1l11_opy_.username)
    if bstack111l1l11_opy_.key:
      bstack11ll1l11_opy_ = bstack11ll1l11_opy_.replace(bstack1l1l11l_opy_ (u"࡚ࠧࡑࡘࡖࡤࡇࡃࡄࡇࡖࡗࡤࡑࡅ࡚ࠩ୮"), bstack111l1l11_opy_.key)
    if bstack111l1l11_opy_.framework:
      bstack11ll1l11_opy_ = bstack11ll1l11_opy_.replace(bstack1l1l11l_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩ୯"), bstack111l1l11_opy_.framework)
    file_name = bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰࠬ୰")
    file_path = os.path.abspath(file_name)
    bstack1l11l11ll_opy_ = open(file_path, bstack1l1l11l_opy_ (u"ࠪࡻࠬୱ"))
    bstack1l11l11ll_opy_.write(bstack11ll1l11_opy_)
    bstack1l11l11ll_opy_.close()
    logger.info(bstack111l111ll_opy_)
    try:
      os.environ[bstack1l1l11l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭୲")] = bstack111l1l11_opy_.framework if bstack111l1l11_opy_.framework != None else bstack1l1l11l_opy_ (u"ࠧࠨ୳")
      config = yaml.safe_load(bstack11ll1l11_opy_)
      config[bstack1l1l11l_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭୴")] = bstack1l1l11l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴ࠭ࡴࡧࡷࡹࡵ࠭୵")
      bstack1lllll111l_opy_(bstack1lll1ll111_opy_, config)
    except Exception as e:
      logger.debug(bstack11lll1l11_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack11ll111l1_opy_.format(str(e)))
def bstack1lllll111l_opy_(bstack11l11ll1_opy_, config, bstack11ll1ll11_opy_={}):
  global bstack1ll1ll11l_opy_
  if not config:
    return
  bstack11l1l1ll1_opy_ = bstack1l1ll1111_opy_ if not bstack1ll1ll11l_opy_ else (
    bstack1l1lll1l1_opy_ if bstack1l1l11l_opy_ (u"ࠨࡣࡳࡴࠬ୶") in config else bstack1l111111l_opy_)
  data = {
    bstack1l1l11l_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫ୷"): config[bstack1l1l11l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬ୸")],
    bstack1l1l11l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧ୹"): config[bstack1l1l11l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨ୺")],
    bstack1l1l11l_opy_ (u"࠭ࡥࡷࡧࡱࡸࡤࡺࡹࡱࡧࠪ୻"): bstack11l11ll1_opy_,
    bstack1l1l11l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪ୼"): {
      bstack1l1l11l_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࡢࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭୽"): str(config[bstack1l1l11l_opy_ (u"ࠩࡶࡳࡺࡸࡣࡦࠩ୾")]) if bstack1l1l11l_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪ୿") in config else bstack1l1l11l_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧ஀"),
      bstack1l1l11l_opy_ (u"ࠬࡸࡥࡧࡧࡵࡶࡪࡸࠧ஁"): bstack1l11ll111_opy_(os.getenv(bstack1l1l11l_opy_ (u"ࠨࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠣஂ"), bstack1l1l11l_opy_ (u"ࠢࠣஃ"))),
      bstack1l1l11l_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠪ஄"): bstack1l1l11l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩஅ"),
      bstack1l1l11l_opy_ (u"ࠪࡴࡷࡵࡤࡶࡥࡷࠫஆ"): bstack11l1l1ll1_opy_,
      bstack1l1l11l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧஇ"): config[bstack1l1l11l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨஈ")] if config[bstack1l1l11l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩஉ")] else bstack1l1l11l_opy_ (u"ࠢࡶࡰ࡮ࡲࡴࡽ࡮ࠣஊ"),
      bstack1l1l11l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ஋"): str(config[bstack1l1l11l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ஌")]) if bstack1l1l11l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ஍") in config else bstack1l1l11l_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧஎ"),
      bstack1l1l11l_opy_ (u"ࠬࡵࡳࠨஏ"): sys.platform,
      bstack1l1l11l_opy_ (u"࠭ࡨࡰࡵࡷࡲࡦࡳࡥࠨஐ"): socket.gethostname()
    }
  }
  update(data[bstack1l1l11l_opy_ (u"ࠧࡦࡸࡨࡲࡹࡥࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠪ஑")], bstack11ll1ll11_opy_)
  try:
    response = bstack111111l1_opy_(bstack1l1l11l_opy_ (u"ࠨࡒࡒࡗ࡙࠭ஒ"), bstack1lll111lll_opy_(bstack1l1l11111_opy_), data, {
      bstack1l1l11l_opy_ (u"ࠩࡤࡹࡹ࡮ࠧஓ"): (config[bstack1l1l11l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬஔ")], config[bstack1l1l11l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧக")])
    })
    if response:
      logger.debug(bstack11111l11_opy_.format(bstack11l11ll1_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1111l1l1l_opy_.format(str(e)))
def bstack1l11ll111_opy_(framework):
  return bstack1l1l11l_opy_ (u"ࠧࢁࡽ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࡻࡾࠤ஖").format(str(framework), __version__) if framework else bstack1l1l11l_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࡧࡧࡦࡰࡷ࠳ࢀࢃࠢ஗").format(
    __version__)
def bstack11l11111_opy_():
  global CONFIG
  if bool(CONFIG):
    return
  try:
    bstack111l1ll1l_opy_()
    logger.debug(bstack111l1ll11_opy_.format(str(CONFIG)))
    bstack1l11111l_opy_()
    bstack1l1l1ll11_opy_()
  except Exception as e:
    logger.error(bstack1l1l11l_opy_ (u"ࠢࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࡵࡱ࠮ࠣࡩࡷࡸ࡯ࡳ࠼ࠣࠦ஘") + str(e))
    sys.exit(1)
  sys.excepthook = bstack1lll1l1111_opy_
  atexit.register(bstack1lll1l111_opy_)
  signal.signal(signal.SIGINT, bstack1lll1lllll_opy_)
  signal.signal(signal.SIGTERM, bstack1lll1lllll_opy_)
def bstack1lll1l1111_opy_(exctype, value, traceback):
  global bstack11ll1lll_opy_
  try:
    for driver in bstack11ll1lll_opy_:
      driver.execute_script(
        bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠤࡩࡥ࡮ࡲࡥࡥࠤ࠯ࠤࠧࡸࡥࡢࡵࡲࡲࠧࡀࠠࠨங") + json.dumps(
          bstack1l1l11l_opy_ (u"ࠤࡖࡩࡸࡹࡩࡰࡰࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧச") + str(value)) + bstack1l1l11l_opy_ (u"ࠪࢁࢂ࠭஛"))
  except Exception:
    pass
  bstack11ll11lll_opy_(value)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack11ll11lll_opy_(message=bstack1l1l11l_opy_ (u"ࠫࠬஜ")):
  global CONFIG
  try:
    if message:
      bstack11ll1ll11_opy_ = {
        bstack1l1l11l_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ஝"): str(message)
      }
      bstack1lllll111l_opy_(bstack111l11ll1_opy_, CONFIG, bstack11ll1ll11_opy_)
    else:
      bstack1lllll111l_opy_(bstack111l11ll1_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack11l111111_opy_.format(str(e)))
def bstack11ll11ll1_opy_(bstack1ll11ll1l_opy_, size):
  bstack1llll1ll1l_opy_ = []
  while len(bstack1ll11ll1l_opy_) > size:
    bstack11ll1l111_opy_ = bstack1ll11ll1l_opy_[:size]
    bstack1llll1ll1l_opy_.append(bstack11ll1l111_opy_)
    bstack1ll11ll1l_opy_ = bstack1ll11ll1l_opy_[size:]
  bstack1llll1ll1l_opy_.append(bstack1ll11ll1l_opy_)
  return bstack1llll1ll1l_opy_
def bstack11l1111l_opy_(args):
  if bstack1l1l11l_opy_ (u"࠭࠭࡮ࠩஞ") in args and bstack1l1l11l_opy_ (u"ࠧࡱࡦࡥࠫட") in args:
    return True
  return False
def run_on_browserstack(bstack11llll1l1_opy_=None, bstack1111111l_opy_=None, bstack11lll1ll_opy_=False):
  global CONFIG
  global bstack11ll11l1_opy_
  global bstack11ll1ll1l_opy_
  bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠨࠩ஠")
  if bstack11llll1l1_opy_ and isinstance(bstack11llll1l1_opy_, str):
    bstack11llll1l1_opy_ = eval(bstack11llll1l1_opy_)
  if bstack11llll1l1_opy_:
    CONFIG = bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩ஡")]
    bstack11ll11l1_opy_ = bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫ஢")]
    bstack11ll1ll1l_opy_ = bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ண")]
    bstack1l11l1ll1_opy_.bstack1l11l1l1_opy_(bstack1l1l11l_opy_ (u"ࠬࡏࡓࡠࡃࡓࡔࡤࡇࡕࡕࡑࡐࡅ࡙ࡋࠧத"), bstack11ll1ll1l_opy_)
    bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭஥")
  if not bstack11lll1ll_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack1ll1ll1l1l_opy_)
      return
    if sys.argv[1] == bstack1l1l11l_opy_ (u"ࠧ࠮࠯ࡹࡩࡷࡹࡩࡰࡰࠪ஦") or sys.argv[1] == bstack1l1l11l_opy_ (u"ࠨ࠯ࡹࠫ஧"):
      logger.info(bstack1l1l11l_opy_ (u"ࠩࡅࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡒࡼࡸ࡭ࡵ࡮ࠡࡕࡇࡏࠥࡼࡻࡾࠩந").format(__version__))
      return
    if sys.argv[1] == bstack1l1l11l_opy_ (u"ࠪࡷࡪࡺࡵࡱࠩன"):
      bstack111l1l111_opy_()
      return
  args = sys.argv
  bstack11l11111_opy_()
  global bstack111l1l1ll_opy_
  global bstack1l111l11_opy_
  global bstack1lll1l1lll_opy_
  global bstack1ll1llll1l_opy_
  global bstack11l1ll111_opy_
  global bstack111ll11l1_opy_
  global bstack1ll11ll1_opy_
  global bstack11llll1l_opy_
  if not bstack11llll1ll_opy_:
    if args[1] == bstack1l1l11l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫப") or args[1] == bstack1l1l11l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲ࠸࠭஫"):
      bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭஬")
      args = args[2:]
    elif args[1] == bstack1l1l11l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭஭"):
      bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧம")
      args = args[2:]
    elif args[1] == bstack1l1l11l_opy_ (u"ࠩࡳࡥࡧࡵࡴࠨய"):
      bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩர")
      args = args[2:]
    elif args[1] == bstack1l1l11l_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬற"):
      bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭ல")
      args = args[2:]
    elif args[1] == bstack1l1l11l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭ள"):
      bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧழ")
      args = args[2:]
    elif args[1] == bstack1l1l11l_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨவ"):
      bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩஶ")
      args = args[2:]
    else:
      if not bstack1l1l11l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭ஷ") in CONFIG or str(CONFIG[bstack1l1l11l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧஸ")]).lower() in [bstack1l1l11l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬஹ"), bstack1l1l11l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠹ࠧ஺")]:
        bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧ஻")
        args = args[1:]
      elif str(CONFIG[bstack1l1l11l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ஼")]).lower() == bstack1l1l11l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ஽"):
        bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩா")
        args = args[1:]
      elif str(CONFIG[bstack1l1l11l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠧி")]).lower() == bstack1l1l11l_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫீ"):
        bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬு")
        args = args[1:]
      elif str(CONFIG[bstack1l1l11l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪூ")]).lower() == bstack1l1l11l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ௃"):
        bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠩࡳࡽࡹ࡫ࡳࡵࠩ௄")
        args = args[1:]
      elif str(CONFIG[bstack1l1l11l_opy_ (u"ࠪࡪࡷࡧ࡭ࡦࡹࡲࡶࡰ࠭௅")]).lower() == bstack1l1l11l_opy_ (u"ࠫࡧ࡫ࡨࡢࡸࡨࠫெ"):
        bstack11llll1ll_opy_ = bstack1l1l11l_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬே")
        args = args[1:]
      else:
        os.environ[bstack1l1l11l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡌࡒࡂࡏࡈ࡛ࡔࡘࡋࠨை")] = bstack11llll1ll_opy_
        bstack11llll11_opy_(bstack1lll111ll1_opy_)
  global bstack1llll1ll11_opy_
  if bstack11llll1l1_opy_:
    try:
      os.environ[bstack1l1l11l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡆࡓࡃࡐࡉ࡜ࡕࡒࡌࠩ௉")] = bstack11llll1ll_opy_
      bstack1lllll111l_opy_(bstack1ll1l11l_opy_, CONFIG)
    except Exception as e:
      logger.debug(bstack11l111111_opy_.format(str(e)))
  global bstack1111l1ll_opy_
  global bstack111ll11ll_opy_
  global bstack11l11llll_opy_
  global bstack111ll111_opy_
  global bstack11l1ll1ll_opy_
  global bstack1ll1lll11l_opy_
  global bstack1l1lll111_opy_
  global bstack1llll111_opy_
  global bstack1l11l111l_opy_
  global bstack1lll1l1l11_opy_
  global bstack111ll1ll1_opy_
  global bstack1lll1lll_opy_
  global bstack1l11llll_opy_
  global bstack1ll1ll1l_opy_
  global bstack1ll1ll11_opy_
  global bstack1lll11l11l_opy_
  global bstack11ll111l_opy_
  global bstack1l11llll1_opy_
  global bstack111ll1l1l_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack1111l1ll_opy_ = webdriver.Remote.__init__
    bstack111ll11ll_opy_ = WebDriver.quit
    bstack111ll1ll1_opy_ = WebDriver.close
    bstack1ll1ll1l_opy_ = WebDriver.get
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack1llll1ll11_opy_ = Popen.__init__
  except Exception as e:
    pass
  if bstack111llllll_opy_(CONFIG):
    if bstack1111l1l1_opy_() < version.parse(bstack1lll11l1l_opy_):
      logger.error(bstack11lll1111_opy_.format(bstack1111l1l1_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        bstack1ll1ll11_opy_ = RemoteConnection._get_proxy_url
      except Exception as e:
        logger.error(bstack111lll1l_opy_.format(str(e)))
  if bstack11llll1ll_opy_ != bstack1l1l11l_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨொ") or (bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩோ") and not bstack11llll1l1_opy_):
    bstack111l1111l_opy_()
  if (bstack11llll1ll_opy_ in [bstack1l1l11l_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩௌ"), bstack1l1l11l_opy_ (u"ࠫࡷࡵࡢࡰࡶ்ࠪ"), bstack1l1l11l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷ࠱࡮ࡴࡴࡦࡴࡱࡥࡱ࠭௎")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack11lllll11_opy_
        bstack11l1ll1ll_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack11ll1l1ll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack111ll111_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack1ll1l1111_opy_ + str(e))
    except Exception as e:
      bstack1ll111111_opy_(e, bstack11ll1l1ll_opy_)
    if bstack11llll1ll_opy_ != bstack1l1l11l_opy_ (u"࠭ࡲࡰࡤࡲࡸ࠲࡯࡮ࡵࡧࡵࡲࡦࡲࠧ௏"):
      bstack11ll1llll_opy_()
    bstack11l11llll_opy_ = Output.end_test
    bstack1ll1lll11l_opy_ = TestStatus.__init__
    bstack1llll111_opy_ = pabot._run
    bstack1l11l111l_opy_ = QueueItem.__init__
    bstack1lll1l1l11_opy_ = pabot._create_command_for_execution
    bstack1l11llll1_opy_ = pabot._report_results
  if bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧௐ"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll111111_opy_(e, bstack11l1ll1l_opy_)
    bstack1lll1lll_opy_ = Runner.run_hook
    bstack1l11llll_opy_ = Step.run
  if bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"ࠨࡲࡼࡸࡪࡹࡴࠨ௑"):
    try:
      bstack1llll1lll1_opy_.launch(CONFIG, {
        bstack1l1l11l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࡤࡴࡡ࡮ࡧࠪ௒"): bstack1l1l11l_opy_ (u"ࠪࡔࡾࡺࡥࡴࡶࠪ௓"),
        bstack1l1l11l_opy_ (u"ࠫ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ௔"): bstack1l111ll1_opy_.version(),
        bstack1l1l11l_opy_ (u"ࠬࡹࡤ࡬ࡡࡹࡩࡷࡹࡩࡰࡰࠪ௕"): __version__
      })
      from _pytest.config import Config
      bstack1lll11l11l_opy_ = Config.getoption
      from _pytest import runner
      bstack11ll111l_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warn(e, bstack11111l1ll_opy_)
    try:
      from pytest_bdd import reporting
      bstack111ll1l1l_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack1l1l11l_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡱࡻࡷࡩࡸࡺ࠭ࡣࡦࡧࠤࡹࡵࠠࡳࡷࡱࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡶࡨࡷࡹࡹࠧ௖"))
  if bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧௗ"):
    bstack1l111l11_opy_ = True
    if bstack11llll1l1_opy_ and bstack11lll1ll_opy_:
      bstack11l1ll111_opy_ = CONFIG.get(bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬ௘"), {}).get(bstack1l1l11l_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ௙"))
      bstack1l1llll11_opy_(bstack1llll1l1_opy_)
    elif bstack11llll1l1_opy_:
      bstack11l1ll111_opy_ = CONFIG.get(bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡗࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࡏࡱࡶ࡬ࡳࡳࡹࠧ௚"), {}).get(bstack1l1l11l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭௛"))
      global bstack11ll1lll_opy_
      try:
        if bstack11l1111l_opy_(bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ௜")]) and multiprocessing.current_process().name == bstack1l1l11l_opy_ (u"࠭࠰ࠨ௝"):
          bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ௞")].remove(bstack1l1l11l_opy_ (u"ࠨ࠯ࡰࠫ௟"))
          bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ௠")].remove(bstack1l1l11l_opy_ (u"ࠪࡴࡩࡨࠧ௡"))
          bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ௢")] = bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ௣")][0]
          with open(bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ௤")], bstack1l1l11l_opy_ (u"ࠧࡳࠩ௥")) as f:
            bstack11l1ll11l_opy_ = f.read()
          bstack11l1l1lll_opy_ = bstack1l1l11l_opy_ (u"ࠣࠤࠥࡪࡷࡵ࡭ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡴࡦ࡮ࠤ࡮ࡳࡰࡰࡴࡷࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢ࡭ࡳ࡯ࡴࡪࡣ࡯࡭ࡿ࡫࠻ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡪࡰ࡬ࡸ࡮ࡧ࡬ࡪࡼࡨࠬࢀࢃࠩ࠼ࠢࡩࡶࡴࡳࠠࡱࡦࡥࠤ࡮ࡳࡰࡰࡴࡷࠤࡕࡪࡢ࠼ࠢࡲ࡫ࡤࡪࡢࠡ࠿ࠣࡔࡩࡨ࠮ࡥࡱࡢࡦࡷ࡫ࡡ࡬࠽ࠍࡨࡪ࡬ࠠ࡮ࡱࡧࡣࡧࡸࡥࡢ࡭ࠫࡷࡪࡲࡦ࠭ࠢࡤࡶ࡬࠲ࠠࡵࡧࡰࡴࡴࡸࡡࡳࡻࠣࡁࠥ࠶ࠩ࠻ࠌࠣࠤࡹࡸࡹ࠻ࠌࠣࠤࠥࠦࡡࡳࡩࠣࡁࠥࡹࡴࡳࠪ࡬ࡲࡹ࠮ࡡࡳࡩࠬ࠯࠶࠶ࠩࠋࠢࠣࡩࡽࡩࡥࡱࡶࠣࡉࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡡࡴࠢࡨ࠾ࠏࠦࠠࠡࠢࡳࡥࡸࡹࠊࠡࠢࡲ࡫ࡤࡪࡢࠩࡵࡨࡰ࡫࠲ࡡࡳࡩ࠯ࡸࡪࡳࡰࡰࡴࡤࡶࡾ࠯ࠊࡑࡦࡥ࠲ࡩࡵ࡟ࡣࠢࡀࠤࡲࡵࡤࡠࡤࡵࡩࡦࡱࠊࡑࡦࡥ࠲ࡩࡵ࡟ࡣࡴࡨࡥࡰࠦ࠽ࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠎࡕࡪࡢࠩࠫ࠱ࡷࡪࡺ࡟ࡵࡴࡤࡧࡪ࠮ࠩ࡝ࡰࠥࠦࠧ௦").format(str(bstack11llll1l1_opy_))
          bstack1llll1llll_opy_ = bstack11l1l1lll_opy_ + bstack11l1ll11l_opy_
          bstack1111l11l1_opy_ = bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬ௧")] + bstack1l1l11l_opy_ (u"ࠪࡣࡧࡹࡴࡢࡥ࡮ࡣࡹ࡫࡭ࡱ࠰ࡳࡽࠬ௨")
          with open(bstack1111l11l1_opy_, bstack1l1l11l_opy_ (u"ࠫࡼ࠭௩")):
            pass
          with open(bstack1111l11l1_opy_, bstack1l1l11l_opy_ (u"ࠧࡽࠫࠣ௪")) as f:
            f.write(bstack1llll1llll_opy_)
          import subprocess
          bstack11ll1l1l1_opy_ = subprocess.run([bstack1l1l11l_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࠨ௫"), bstack1111l11l1_opy_])
          if os.path.exists(bstack1111l11l1_opy_):
            os.unlink(bstack1111l11l1_opy_)
          os._exit(bstack11ll1l1l1_opy_.returncode)
        else:
          if bstack11l1111l_opy_(bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ௬")]):
            bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ௭")].remove(bstack1l1l11l_opy_ (u"ࠩ࠰ࡱࠬ௮"))
            bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭௯")].remove(bstack1l1l11l_opy_ (u"ࠫࡵࡪࡢࠨ௰"))
            bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ௱")] = bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ௲")][0]
          bstack1l1llll11_opy_(bstack1llll1l1_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪ௳")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack1l1l11l_opy_ (u"ࠨࡡࡢࡲࡦࡳࡥࡠࡡࠪ௴")] = bstack1l1l11l_opy_ (u"ࠩࡢࡣࡲࡧࡩ࡯ࡡࡢࠫ௵")
          mod_globals[bstack1l1l11l_opy_ (u"ࠪࡣࡤ࡬ࡩ࡭ࡧࡢࡣࠬ௶")] = os.path.abspath(bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧ௷")])
          exec(open(bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨ௸")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack1l1l11l_opy_ (u"࠭ࡃࡢࡷࡪ࡬ࡹࠦࡅࡹࡥࡨࡴࡹ࡯࡯࡯࠼ࠣࡿࢂ࠭௹").format(str(e)))
          for driver in bstack11ll1lll_opy_:
            bstack1111111l_opy_.append({
              bstack1l1l11l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬ௺"): bstack11llll1l1_opy_[bstack1l1l11l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫ௻")],
              bstack1l1l11l_opy_ (u"ࠩࡨࡶࡷࡵࡲࠨ௼"): str(e),
              bstack1l1l11l_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩ௽"): multiprocessing.current_process().name
            })
            driver.execute_script(
              bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡔࡶࡤࡸࡺࡹࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡷࡹࡧࡴࡶࡵࠥ࠾ࠧ࡬ࡡࡪ࡮ࡨࡨࠧ࠲ࠠࠣࡴࡨࡥࡸࡵ࡮ࠣ࠼ࠣࠫ௾") + json.dumps(
                bstack1l1l11l_opy_ (u"࡙ࠧࡥࡴࡵ࡬ࡳࡳࠦࡦࡢ࡫࡯ࡩࡩࠦࡷࡪࡶ࡫࠾ࠥࡢ࡮ࠣ௿") + str(e)) + bstack1l1l11l_opy_ (u"࠭ࡽࡾࠩఀ"))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack11ll1lll_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      bstack1111l111_opy_()
      bstack11l111l1l_opy_()
      bstack1l1l1l111_opy_ = {
        bstack1l1l11l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪఁ"): args[0],
        bstack1l1l11l_opy_ (u"ࠨࡅࡒࡒࡋࡏࡇࠨం"): CONFIG,
        bstack1l1l11l_opy_ (u"ࠩࡋ࡙ࡇࡥࡕࡓࡎࠪః"): bstack11ll11l1_opy_,
        bstack1l1l11l_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬఄ"): bstack11ll1ll1l_opy_
      }
      if bstack1l1l11l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧఅ") in CONFIG:
        bstack1l1l111l1_opy_ = []
        manager = multiprocessing.Manager()
        bstack111lll11l_opy_ = manager.list()
        if bstack11l1111l_opy_(args):
          for index, platform in enumerate(CONFIG[bstack1l1l11l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨఆ")]):
            if index == 0:
              bstack1l1l1l111_opy_[bstack1l1l11l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩఇ")] = args
            bstack1l1l111l1_opy_.append(multiprocessing.Process(name=str(index),
                                                       target=run_on_browserstack,
                                                       args=(bstack1l1l1l111_opy_, bstack111lll11l_opy_)))
        else:
          for index, platform in enumerate(CONFIG[bstack1l1l11l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪఈ")]):
            bstack1l1l111l1_opy_.append(multiprocessing.Process(name=str(index),
                                                       target=run_on_browserstack,
                                                       args=(bstack1l1l1l111_opy_, bstack111lll11l_opy_)))
        for t in bstack1l1l111l1_opy_:
          t.start()
        for t in bstack1l1l111l1_opy_:
          t.join()
        bstack1ll11ll1_opy_ = list(bstack111lll11l_opy_)
      else:
        if bstack11l1111l_opy_(args):
          bstack1l1l1l111_opy_[bstack1l1l11l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫఉ")] = args
          test = multiprocessing.Process(name=str(0),
                                         target=run_on_browserstack, args=(bstack1l1l1l111_opy_,))
          test.start()
          test.join()
        else:
          bstack1l1llll11_opy_(bstack1llll1l1_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack1l1l11l_opy_ (u"ࠩࡢࡣࡳࡧ࡭ࡦࡡࡢࠫఊ")] = bstack1l1l11l_opy_ (u"ࠪࡣࡤࡳࡡࡪࡰࡢࡣࠬఋ")
          mod_globals[bstack1l1l11l_opy_ (u"ࠫࡤࡥࡦࡪ࡮ࡨࡣࡤ࠭ఌ")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"ࠬࡶࡡࡣࡱࡷࠫ఍") or bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬఎ"):
    try:
      from pabot import pabot
    except Exception as e:
      bstack1ll111111_opy_(e, bstack11ll1l1ll_opy_)
    bstack1111l111_opy_()
    bstack1l1llll11_opy_(bstack1l1ll1lll_opy_)
    if bstack1l1l11l_opy_ (u"ࠧ࠮࠯ࡳࡶࡴࡩࡥࡴࡵࡨࡷࠬఏ") in args:
      i = args.index(bstack1l1l11l_opy_ (u"ࠨ࠯࠰ࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭ఐ"))
      args.pop(i)
      args.pop(i)
    args.insert(0, str(bstack111l1l1ll_opy_))
    args.insert(0, str(bstack1l1l11l_opy_ (u"ࠩ࠰࠱ࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠧ఑")))
    pabot.main(args)
  elif bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫఒ"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack1ll111111_opy_(e, bstack11ll1l1ll_opy_)
    for a in args:
      if bstack1l1l11l_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡔࡑࡇࡔࡇࡑࡕࡑࡎࡔࡄࡆ࡚ࠪఓ") in a:
        bstack1ll1llll1l_opy_ = int(a.split(bstack1l1l11l_opy_ (u"ࠬࡀࠧఔ"))[1])
      if bstack1l1l11l_opy_ (u"࠭ࡂࡔࡖࡄࡇࡐࡊࡅࡇࡎࡒࡇࡆࡒࡉࡅࡇࡑࡘࡎࡌࡉࡆࡔࠪక") in a:
        bstack11l1ll111_opy_ = str(a.split(bstack1l1l11l_opy_ (u"ࠧ࠻ࠩఖ"))[1])
      if bstack1l1l11l_opy_ (u"ࠨࡄࡖࡘࡆࡉࡋࡄࡎࡌࡅࡗࡍࡓࠨగ") in a:
        bstack111ll11l1_opy_ = str(a.split(bstack1l1l11l_opy_ (u"ࠩ࠽ࠫఘ"))[1])
    bstack111l1111_opy_ = None
    if bstack1l1l11l_opy_ (u"ࠪ࠱࠲ࡨࡳࡵࡣࡦ࡯ࡤ࡯ࡴࡦ࡯ࡢ࡭ࡳࡪࡥࡹࠩఙ") in args:
      i = args.index(bstack1l1l11l_opy_ (u"ࠫ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡩࡵࡧࡰࡣ࡮ࡴࡤࡦࡺࠪచ"))
      args.pop(i)
      bstack111l1111_opy_ = args.pop(i)
    if bstack111l1111_opy_ is not None:
      global bstack1llll11lll_opy_
      bstack1llll11lll_opy_ = bstack111l1111_opy_
    bstack1l1llll11_opy_(bstack1l1ll1lll_opy_)
    run_cli(args)
  elif bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬఛ"):
    bstack11ll1111_opy_ = bstack1l111ll1_opy_(args, logger, CONFIG, bstack1ll1ll11l_opy_)
    bstack11ll1111_opy_.bstack11ll1111l_opy_()
    bstack1111l111_opy_()
    bstack11llll1l_opy_ = bstack11ll1111_opy_.bstack1l1111l1l_opy_()
    bstack11ll1111_opy_.bstack1l1l1l111_opy_(bstack11l11l11l_opy_)
    bstack1lll1l1lll_opy_ = True
    bstack111111111_opy_ = bstack11ll1111_opy_.bstack1ll1ll11l1_opy_()
    bstack11ll1111_opy_.bstack1lll11l1_opy_(bstack111111111_opy_, bstack1l1llll11_opy_)
  elif bstack11llll1ll_opy_ == bstack1l1l11l_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭జ"):
    try:
      from behave.__main__ import main as bstack1l11ll11l_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack1ll111111_opy_(e, bstack11l1ll1l_opy_)
    bstack1111l111_opy_()
    bstack1lll1l1lll_opy_ = True
    bstack11lll111_opy_ = 1
    if bstack1l1l11l_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧఝ") in CONFIG:
      bstack11lll111_opy_ = CONFIG[bstack1l1l11l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨఞ")]
    bstack11lllllll_opy_ = int(bstack11lll111_opy_) * int(len(CONFIG[bstack1l1l11l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬట")]))
    config = Configuration(args)
    bstack1l11111l1_opy_ = config.paths
    if len(bstack1l11111l1_opy_) == 0:
      import glob
      pattern = bstack1l1l11l_opy_ (u"ࠪ࠮࠯࠵ࠪ࠯ࡨࡨࡥࡹࡻࡲࡦࠩఠ")
      bstack11lll1lll_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack11lll1lll_opy_)
      config = Configuration(args)
      bstack1l11111l1_opy_ = config.paths
    bstack1ll1ll11ll_opy_ = [os.path.normpath(item) for item in bstack1l11111l1_opy_]
    bstack11111l1l1_opy_ = [os.path.normpath(item) for item in args]
    bstack111111l1l_opy_ = [item for item in bstack11111l1l1_opy_ if item not in bstack1ll1ll11ll_opy_]
    import platform as pf
    if pf.system().lower() == bstack1l1l11l_opy_ (u"ࠫࡼ࡯࡮ࡥࡱࡺࡷࠬడ"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1ll1ll11ll_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11111l111_opy_)))
                    for bstack11111l111_opy_ in bstack1ll1ll11ll_opy_]
    bstack1l11l111_opy_ = []
    for spec in bstack1ll1ll11ll_opy_:
      bstack11ll11ll_opy_ = []
      bstack11ll11ll_opy_ += bstack111111l1l_opy_
      bstack11ll11ll_opy_.append(spec)
      bstack1l11l111_opy_.append(bstack11ll11ll_opy_)
    execution_items = []
    for bstack11ll11ll_opy_ in bstack1l11l111_opy_:
      for index, _ in enumerate(CONFIG[bstack1l1l11l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨఢ")]):
        item = {}
        item[bstack1l1l11l_opy_ (u"࠭ࡡࡳࡩࠪణ")] = bstack1l1l11l_opy_ (u"ࠧࠡࠩత").join(bstack11ll11ll_opy_)
        item[bstack1l1l11l_opy_ (u"ࠨ࡫ࡱࡨࡪࡾࠧథ")] = index
        execution_items.append(item)
    bstack111111111_opy_ = bstack11ll11ll1_opy_(execution_items, bstack11lllllll_opy_)
    for execution_item in bstack111111111_opy_:
      bstack1l1l111l1_opy_ = []
      for item in execution_item:
        bstack1l1l111l1_opy_.append(bstack1lll1lll11_opy_(name=str(item[bstack1l1l11l_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨద")]),
                                             target=bstack1lll1111l_opy_,
                                             args=(item[bstack1l1l11l_opy_ (u"ࠪࡥࡷ࡭ࠧధ")],)))
      for t in bstack1l1l111l1_opy_:
        t.start()
      for t in bstack1l1l111l1_opy_:
        t.join()
  else:
    bstack11llll11_opy_(bstack1lll111ll1_opy_)
  if not bstack11llll1l1_opy_:
    bstack11l111l1_opy_()
def browserstack_initialize(bstack1ll11lll_opy_=None):
  run_on_browserstack(bstack1ll11lll_opy_, None, True)
def bstack11l111l1_opy_():
  bstack1llll1lll1_opy_.stop()
  bstack1llll1lll1_opy_.bstack1l1ll1l1_opy_()
  [bstack11l111l11_opy_, bstack11lllll1_opy_] = bstack1l111l1l_opy_()
  if bstack11l111l11_opy_ is not None and bstack11l11lll_opy_() != -1:
    sessions = bstack1ll1ll1l11_opy_(bstack11l111l11_opy_)
    bstack1llllll1ll_opy_(sessions, bstack11lllll1_opy_)
def bstack1l111llll_opy_(bstack111ll1ll_opy_):
  if bstack111ll1ll_opy_:
    return bstack111ll1ll_opy_.capitalize()
  else:
    return bstack111ll1ll_opy_
def bstack1l1lll1ll_opy_(bstack1lll1111ll_opy_):
  if bstack1l1l11l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩన") in bstack1lll1111ll_opy_ and bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ఩")] != bstack1l1l11l_opy_ (u"࠭ࠧప"):
    return bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬఫ")]
  else:
    bstack1llll1ll1_opy_ = bstack1l1l11l_opy_ (u"ࠣࠤబ")
    if bstack1l1l11l_opy_ (u"ࠩࡧࡩࡻ࡯ࡣࡦࠩభ") in bstack1lll1111ll_opy_ and bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪమ")] != None:
      bstack1llll1ll1_opy_ += bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫయ")] + bstack1l1l11l_opy_ (u"ࠧ࠲ࠠࠣర")
      if bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"࠭࡯ࡴࠩఱ")] == bstack1l1l11l_opy_ (u"ࠢࡪࡱࡶࠦల"):
        bstack1llll1ll1_opy_ += bstack1l1l11l_opy_ (u"ࠣ࡫ࡒࡗࠥࠨళ")
      bstack1llll1ll1_opy_ += (bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ఴ")] or bstack1l1l11l_opy_ (u"ࠪࠫవ"))
      return bstack1llll1ll1_opy_
    else:
      bstack1llll1ll1_opy_ += bstack1l111llll_opy_(bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬశ")]) + bstack1l1l11l_opy_ (u"ࠧࠦࠢష") + (
              bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸ࡟ࡷࡧࡵࡷ࡮ࡵ࡮ࠨస")] or bstack1l1l11l_opy_ (u"ࠧࠨహ")) + bstack1l1l11l_opy_ (u"ࠣ࠮ࠣࠦ఺")
      if bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠩࡲࡷࠬ఻")] == bstack1l1l11l_opy_ (u"࡛ࠥ࡮ࡴࡤࡰࡹࡶ఼ࠦ"):
        bstack1llll1ll1_opy_ += bstack1l1l11l_opy_ (u"ࠦ࡜࡯࡮ࠡࠤఽ")
      bstack1llll1ll1_opy_ += bstack1lll1111ll_opy_[bstack1l1l11l_opy_ (u"ࠬࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠩా")] or bstack1l1l11l_opy_ (u"࠭ࠧి")
      return bstack1llll1ll1_opy_
def bstack1111ll11l_opy_(bstack1ll11l1l1_opy_):
  if bstack1ll11l1l1_opy_ == bstack1l1l11l_opy_ (u"ࠢࡥࡱࡱࡩࠧీ"):
    return bstack1l1l11l_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽࡫ࡷ࡫ࡥ࡯࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥ࡫ࡷ࡫ࡥ࡯ࠤࡁࡇࡴࡳࡰ࡭ࡧࡷࡩࡩࡂ࠯ࡧࡱࡱࡸࡃࡂ࠯ࡵࡦࡁࠫు")
  elif bstack1ll11l1l1_opy_ == bstack1l1l11l_opy_ (u"ࠤࡩࡥ࡮ࡲࡥࡥࠤూ"):
    return bstack1l1l11l_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࡸࡥࡥ࠽ࠥࡂࡁ࡬࡯࡯ࡶࠣࡧࡴࡲ࡯ࡳ࠿ࠥࡶࡪࡪࠢ࠿ࡈࡤ࡭ࡱ࡫ࡤ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ృ")
  elif bstack1ll11l1l1_opy_ == bstack1l1l11l_opy_ (u"ࠦࡵࡧࡳࡴࡧࡧࠦౄ"):
    return bstack1l1l11l_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡨࡴࡨࡩࡳࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡨࡴࡨࡩࡳࠨ࠾ࡑࡣࡶࡷࡪࡪ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ౅")
  elif bstack1ll11l1l1_opy_ == bstack1l1l11l_opy_ (u"ࠨࡥࡳࡴࡲࡶࠧె"):
    return bstack1l1l11l_opy_ (u"ࠧ࠽ࡶࡧࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡵࡩࡩࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡳࡧࡧࠦࡃࡋࡲࡳࡱࡵࡀ࠴࡬࡯࡯ࡶࡁࡀ࠴ࡺࡤ࠿ࠩే")
  elif bstack1ll11l1l1_opy_ == bstack1l1l11l_opy_ (u"ࠣࡶ࡬ࡱࡪࡵࡵࡵࠤై"):
    return bstack1l1l11l_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾ࠨ࡫ࡥࡢ࠵࠵࠺ࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࠣࡦࡧࡤ࠷࠷࠼ࠢ࠿ࡖ࡬ࡱࡪࡵࡵࡵ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧ౉")
  elif bstack1ll11l1l1_opy_ == bstack1l1l11l_opy_ (u"ࠥࡶࡺࡴ࡮ࡪࡰࡪࠦొ"):
    return bstack1l1l11l_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡢ࡭ࡣࡦ࡯ࡀࠨ࠾࠽ࡨࡲࡲࡹࠦࡣࡰ࡮ࡲࡶࡂࠨࡢ࡭ࡣࡦ࡯ࠧࡄࡒࡶࡰࡱ࡭ࡳ࡭࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬో")
  else:
    return bstack1l1l11l_opy_ (u"ࠬࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡤ࡯ࡥࡨࡱ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡤ࡯ࡥࡨࡱࠢ࠿ࠩౌ") + bstack1l111llll_opy_(
      bstack1ll11l1l1_opy_) + bstack1l1l11l_opy_ (u"࠭࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂ్ࠬ")
def bstack1ll1ll1ll_opy_(session):
  return bstack1l1l11l_opy_ (u"ࠧ࠽ࡶࡵࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡷࡵࡷࠣࡀ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠤࡸ࡫ࡳࡴ࡫ࡲࡲ࠲ࡴࡡ࡮ࡧࠥࡂࡁࡧࠠࡩࡴࡨࡪࡂࠨࡻࡾࠤࠣࡸࡦࡸࡧࡦࡶࡀࠦࡤࡨ࡬ࡢࡰ࡮ࠦࡃࢁࡽ࠽࠱ࡤࡂࡁ࠵ࡴࡥࡀࡾࢁࢀࢃ࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࡁࡿࢂࡂ࠯ࡵࡦࡁࡀࡹࡪࠠࡢ࡮࡬࡫ࡳࡃࠢࡤࡧࡱࡸࡪࡸࠢࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨ࠾ࡼࡿ࠿࠳ࡹࡪ࠾࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࡂࢀࢃ࠼࠰ࡶࡧࡂࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢ࠿ࡽࢀࡀ࠴ࡺࡤ࠿࠾࠲ࡸࡷࡄࠧ౎").format(
    session[bstack1l1l11l_opy_ (u"ࠨࡲࡸࡦࡱ࡯ࡣࡠࡷࡵࡰࠬ౏")], bstack1l1lll1ll_opy_(session), bstack1111ll11l_opy_(session[bstack1l1l11l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡵࡷࡥࡹࡻࡳࠨ౐")]),
    bstack1111ll11l_opy_(session[bstack1l1l11l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪ౑")]),
    bstack1l111llll_opy_(session[bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࠬ౒")] or session[bstack1l1l11l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬ౓")] or bstack1l1l11l_opy_ (u"࠭ࠧ౔")) + bstack1l1l11l_opy_ (u"ࠢࠡࠤౕ") + (session[bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡡࡹࡩࡷࡹࡩࡰࡰౖࠪ")] or bstack1l1l11l_opy_ (u"ࠩࠪ౗")),
    session[bstack1l1l11l_opy_ (u"ࠪࡳࡸ࠭ౘ")] + bstack1l1l11l_opy_ (u"ࠦࠥࠨౙ") + session[bstack1l1l11l_opy_ (u"ࠬࡵࡳࡠࡸࡨࡶࡸ࡯࡯࡯ࠩౚ")], session[bstack1l1l11l_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࠨ౛")] or bstack1l1l11l_opy_ (u"ࠧࠨ౜"),
    session[bstack1l1l11l_opy_ (u"ࠨࡥࡵࡩࡦࡺࡥࡥࡡࡤࡸࠬౝ")] if session[bstack1l1l11l_opy_ (u"ࠩࡦࡶࡪࡧࡴࡦࡦࡢࡥࡹ࠭౞")] else bstack1l1l11l_opy_ (u"ࠪࠫ౟"))
def bstack1llllll1ll_opy_(sessions, bstack11lllll1_opy_):
  try:
    bstack11l111ll_opy_ = bstack1l1l11l_opy_ (u"ࠦࠧౠ")
    if not os.path.exists(bstack1l111lll1_opy_):
      os.mkdir(bstack1l111lll1_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1l11l_opy_ (u"ࠬࡧࡳࡴࡧࡷࡷ࠴ࡸࡥࡱࡱࡵࡸ࠳࡮ࡴ࡮࡮ࠪౡ")), bstack1l1l11l_opy_ (u"࠭ࡲࠨౢ")) as f:
      bstack11l111ll_opy_ = f.read()
    bstack11l111ll_opy_ = bstack11l111ll_opy_.replace(bstack1l1l11l_opy_ (u"ࠧࡼࠧࡕࡉࡘ࡛ࡌࡕࡕࡢࡇࡔ࡛ࡎࡕࠧࢀࠫౣ"), str(len(sessions)))
    bstack11l111ll_opy_ = bstack11l111ll_opy_.replace(bstack1l1l11l_opy_ (u"ࠨࡽࠨࡆ࡚ࡏࡌࡅࡡࡘࡖࡑࠫࡽࠨ౤"), bstack11lllll1_opy_)
    bstack11l111ll_opy_ = bstack11l111ll_opy_.replace(bstack1l1l11l_opy_ (u"ࠩࡾࠩࡇ࡛ࡉࡍࡆࡢࡒࡆࡓࡅࠦࡿࠪ౥"),
                                              sessions[0].get(bstack1l1l11l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡࡱࡥࡲ࡫ࠧ౦")) if sessions[0] else bstack1l1l11l_opy_ (u"ࠫࠬ౧"))
    with open(os.path.join(bstack1l111lll1_opy_, bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠱ࡷ࡫ࡰࡰࡴࡷ࠲࡭ࡺ࡭࡭ࠩ౨")), bstack1l1l11l_opy_ (u"࠭ࡷࠨ౩")) as stream:
      stream.write(bstack11l111ll_opy_.split(bstack1l1l11l_opy_ (u"ࠧࡼࠧࡖࡉࡘ࡙ࡉࡐࡐࡖࡣࡉࡇࡔࡂࠧࢀࠫ౪"))[0])
      for session in sessions:
        stream.write(bstack1ll1ll1ll_opy_(session))
      stream.write(bstack11l111ll_opy_.split(bstack1l1l11l_opy_ (u"ࠨࡽࠨࡗࡊ࡙ࡓࡊࡑࡑࡗࡤࡊࡁࡕࡃࠨࢁࠬ౫"))[1])
    logger.info(bstack1l1l11l_opy_ (u"ࠩࡊࡩࡳ࡫ࡲࡢࡶࡨࡨࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡧࡻࡩ࡭ࡦࠣࡥࡷࡺࡩࡧࡣࡦࡸࡸࠦࡡࡵࠢࡾࢁࠬ౬").format(bstack1l111lll1_opy_));
  except Exception as e:
    logger.debug(bstack1llll1lll_opy_.format(str(e)))
def bstack1ll1ll1l11_opy_(bstack11l111l11_opy_):
  global CONFIG
  try:
    host = bstack1l1l11l_opy_ (u"ࠪࡥࡵ࡯࠭ࡤ࡮ࡲࡹࡩ࠭౭") if bstack1l1l11l_opy_ (u"ࠫࡦࡶࡰࠨ౮") in CONFIG else bstack1l1l11l_opy_ (u"ࠬࡧࡰࡪࠩ౯")
    user = CONFIG[bstack1l1l11l_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨ౰")]
    key = CONFIG[bstack1l1l11l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪ౱")]
    bstack1l11l1111_opy_ = bstack1l1l11l_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ౲") if bstack1l1l11l_opy_ (u"ࠩࡤࡴࡵ࠭౳") in CONFIG else bstack1l1l11l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬ౴")
    url = bstack1l1l11l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࢁࡽ࠻ࡽࢀࡄࢀࢃ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡿࢂ࠵ࡢࡶ࡫࡯ࡨࡸ࠵ࡻࡾ࠱ࡶࡩࡸࡹࡩࡰࡰࡶ࠲࡯ࡹ࡯࡯ࠩ౵").format(user, key, host, bstack1l11l1111_opy_,
                                                                                bstack11l111l11_opy_)
    headers = {
      bstack1l1l11l_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡴࡺࡲࡨࠫ౶"): bstack1l1l11l_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩ౷"),
    }
    proxies = bstack1l1l1111_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.json():
      return list(map(lambda session: session[bstack1l1l11l_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡸ࡫ࡳࡴ࡫ࡲࡲࠬ౸")], response.json()))
  except Exception as e:
    logger.debug(bstack1ll1llll_opy_.format(str(e)))
def bstack1l111l1l_opy_():
  global CONFIG
  try:
    if bstack1l1l11l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ౹") in CONFIG:
      host = bstack1l1l11l_opy_ (u"ࠩࡤࡴ࡮࠳ࡣ࡭ࡱࡸࡨࠬ౺") if bstack1l1l11l_opy_ (u"ࠪࡥࡵࡶࠧ౻") in CONFIG else bstack1l1l11l_opy_ (u"ࠫࡦࡶࡩࠨ౼")
      user = CONFIG[bstack1l1l11l_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ౽")]
      key = CONFIG[bstack1l1l11l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ౾")]
      bstack1l11l1111_opy_ = bstack1l1l11l_opy_ (u"ࠧࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭౿") if bstack1l1l11l_opy_ (u"ࠨࡣࡳࡴࠬಀ") in CONFIG else bstack1l1l11l_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫಁ")
      url = bstack1l1l11l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴ࠼࠲࠳ࢀࢃ࠺ࡼࡿࡃࡿࢂ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡾࢁ࠴ࡨࡵࡪ࡮ࡧࡷ࠳ࡰࡳࡰࡰࠪಂ").format(user, key, host, bstack1l11l1111_opy_)
      headers = {
        bstack1l1l11l_opy_ (u"ࠫࡈࡵ࡮ࡵࡧࡱࡸ࠲ࡺࡹࡱࡧࠪಃ"): bstack1l1l11l_opy_ (u"ࠬࡧࡰࡱ࡮࡬ࡧࡦࡺࡩࡰࡰ࠲࡮ࡸࡵ࡮ࠨ಄"),
      }
      if bstack1l1l11l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨಅ") in CONFIG:
        params = {bstack1l1l11l_opy_ (u"ࠧ࡯ࡣࡰࡩࠬಆ"): CONFIG[bstack1l1l11l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫಇ")], bstack1l1l11l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡠ࡫ࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬಈ"): CONFIG[bstack1l1l11l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬಉ")]}
      else:
        params = {bstack1l1l11l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩಊ"): CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨಋ")]}
      proxies = bstack1l1l1111_opy_(CONFIG, url)
      response = requests.get(url, params=params, headers=headers, proxies=proxies)
      if response.json():
        bstack1lllllll11_opy_ = response.json()[0][bstack1l1l11l_opy_ (u"࠭ࡡࡶࡶࡲࡱࡦࡺࡩࡰࡰࡢࡦࡺ࡯࡬ࡥࠩಌ")]
        if bstack1lllllll11_opy_:
          bstack11lllll1_opy_ = bstack1lllllll11_opy_[bstack1l1l11l_opy_ (u"ࠧࡱࡷࡥࡰ࡮ࡩ࡟ࡶࡴ࡯ࠫ಍")].split(bstack1l1l11l_opy_ (u"ࠨࡲࡸࡦࡱ࡯ࡣ࠮ࡤࡸ࡭ࡱࡪࠧಎ"))[0] + bstack1l1l11l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡴ࠱ࠪಏ") + bstack1lllllll11_opy_[
            bstack1l1l11l_opy_ (u"ࠪ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ಐ")]
          logger.info(bstack11ll1l1l_opy_.format(bstack11lllll1_opy_))
          bstack1lll111l_opy_ = CONFIG[bstack1l1l11l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ಑")]
          if bstack1l1l11l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧಒ") in CONFIG:
            bstack1lll111l_opy_ += bstack1l1l11l_opy_ (u"࠭ࠠࠨಓ") + CONFIG[bstack1l1l11l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩಔ")]
          if bstack1lll111l_opy_ != bstack1lllllll11_opy_[bstack1l1l11l_opy_ (u"ࠨࡰࡤࡱࡪ࠭ಕ")]:
            logger.debug(bstack1llll11ll_opy_.format(bstack1lllllll11_opy_[bstack1l1l11l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧಖ")], bstack1lll111l_opy_))
          return [bstack1lllllll11_opy_[bstack1l1l11l_opy_ (u"ࠪ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩ࠭ಗ")], bstack11lllll1_opy_]
    else:
      logger.warn(bstack1l1l1l11l_opy_)
  except Exception as e:
    logger.debug(bstack1ll1l1l11_opy_.format(str(e)))
  return [None, None]
def bstack1l1ll11l1_opy_(url, bstack11111lll_opy_=False):
  global CONFIG
  global bstack11l1l1111_opy_
  if not bstack11l1l1111_opy_:
    hostname = bstack11llllll1_opy_(url)
    is_private = bstack1111l1lll_opy_(hostname)
    if (bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨಘ") in CONFIG and not CONFIG[bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩಙ")]) and (is_private or bstack11111lll_opy_):
      bstack11l1l1111_opy_ = hostname
def bstack11llllll1_opy_(url):
  return urlparse(url).hostname
def bstack1111l1lll_opy_(hostname):
  for bstack1ll1lll11_opy_ in bstack11l1l11ll_opy_:
    regex = re.compile(bstack1ll1lll11_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack1lllll1ll1_opy_(key_name):
  return True if key_name in threading.current_thread().__dict__.keys() else False