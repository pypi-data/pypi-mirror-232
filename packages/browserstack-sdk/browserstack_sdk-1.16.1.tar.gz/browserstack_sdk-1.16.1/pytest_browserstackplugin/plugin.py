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
import datetime
import inspect
import os
import threading
from uuid import uuid4
import pytest
from bstack_utils.capture import bstack1ll11l1lll_opy_
from bstack_utils.bstack1l1l1ll111_opy_ import bstack1l1l1ll11l_opy_
from bstack_utils.helper import bstack1l1llll11l_opy_, bstack1ll111l1ll_opy_, bstack1lll111ll_opy_, bstack1l1lllll11_opy_, \
    bstack1ll11111l1_opy_
from bstack_utils.bstack1l1111lll_opy_ import bstack1llll1lll1_opy_
try:
    from playwright.sync_api import (
        BrowserContext,
        Page
    )
except:
    pass
import json
_1l11ll1l1l_opy_ = {}
bstack1l11ll1lll_opy_ = None
_1l11l111l1_opy_ = {}
def bstack1ll111ll1_opy_(page, bstack11ll1l11l_opy_):
    try:
        page.evaluate(bstack1l1l11l_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨზ"),
                      bstack1l1l11l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪთ") + json.dumps(
                          bstack11ll1l11l_opy_) + bstack1l1l11l_opy_ (u"ࠢࡾࡿࠥი"))
    except Exception as e:
        print(bstack1l1l11l_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨკ"), e)
def bstack1111lll1l_opy_(page, message, level):
    try:
        page.evaluate(bstack1l1l11l_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥლ"), bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨმ") + json.dumps(
            message) + bstack1l1l11l_opy_ (u"ࠫ࠱ࠨ࡬ࡦࡸࡨࡰࠧࡀࠧნ") + json.dumps(level) + bstack1l1l11l_opy_ (u"ࠬࢃࡽࠨო"))
    except Exception as e:
        print(bstack1l1l11l_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡤࡲࡳࡵࡴࡢࡶ࡬ࡳࡳࠦࡻࡾࠤპ"), e)
def bstack11ll11111_opy_(page, status, message=bstack1l1l11l_opy_ (u"ࠢࠣჟ")):
    try:
        if (status == bstack1l1l11l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣრ")):
            page.evaluate(bstack1l1l11l_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥს"),
                          bstack1l1l11l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠫტ") + json.dumps(
                              bstack1l1l11l_opy_ (u"ࠦࡘࡩࡥ࡯ࡣࡵ࡭ࡴࠦࡦࡢ࡫࡯ࡩࡩࠦࡷࡪࡶ࡫࠾ࠥࠨუ") + str(message)) + bstack1l1l11l_opy_ (u"ࠬ࠲ࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠩფ") + json.dumps(status) + bstack1l1l11l_opy_ (u"ࠨࡽࡾࠤქ"))
        else:
            page.evaluate(bstack1l1l11l_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣღ"),
                          bstack1l1l11l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠩყ") + json.dumps(
                              status) + bstack1l1l11l_opy_ (u"ࠤࢀࢁࠧშ"))
    except Exception as e:
        print(bstack1l1l11l_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤࢀࢃࠢჩ"), e)
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    bstack1l11l11l1l_opy_ = item.config.getoption(bstack1l1l11l_opy_ (u"ࠫࡸࡱࡩࡱࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪ࠭ც"))
    plugins = item.config.getoption(bstack1l1l11l_opy_ (u"ࠧࡶ࡬ࡶࡩ࡬ࡲࡸࠨძ"))
    report = outcome.get_result()
    bstack1l11l11lll_opy_(item, call, report)
    if bstack1l1l11l_opy_ (u"ࠨࡰࡺࡶࡨࡷࡹࡥࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡵࡲࡵࡨ࡫ࡱࠦწ") not in plugins:
        return
    summary = []
    driver = getattr(item, bstack1l1l11l_opy_ (u"ࠢࡠࡦࡵ࡭ࡻ࡫ࡲࠣჭ"), None)
    page = getattr(item, bstack1l1l11l_opy_ (u"ࠣࡡࡳࡥ࡬࡫ࠢხ"), None)
    try:
        if (driver == None):
            driver = threading.current_thread().bstackSessionDriver
    except:
        pass
    item._driver = driver
    if (driver is not None):
        bstack1l11l11l11_opy_(item, report, summary, bstack1l11l11l1l_opy_)
    if (page is not None):
        bstack1l11l1lll1_opy_(item, report, summary, bstack1l11l11l1l_opy_)
def bstack1l11l11l11_opy_(item, report, summary, bstack1l11l11l1l_opy_):
    if report.when in [bstack1l1l11l_opy_ (u"ࠤࡶࡩࡹࡻࡰࠣჯ"), bstack1l1l11l_opy_ (u"ࠥࡸࡪࡧࡲࡥࡱࡺࡲࠧჰ")]:
        return
    if not bstack1ll111l1ll_opy_():
        return
    if (str(bstack1l11l11l1l_opy_).lower() != bstack1l1l11l_opy_ (u"ࠫࡹࡸࡵࡦࠩჱ")):
        item._driver.execute_script(
            bstack1l1l11l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪჲ") + json.dumps(
                report.nodeid) + bstack1l1l11l_opy_ (u"࠭ࡽࡾࠩჳ"))
    passed = report.passed or (report.failed and hasattr(report, bstack1l1l11l_opy_ (u"ࠢࡸࡣࡶࡼ࡫ࡧࡩ࡭ࠤჴ")))
    bstack1l1l11ll1_opy_ = bstack1l1l11l_opy_ (u"ࠣࠤჵ")
    if not passed:
        try:
            bstack1l1l11ll1_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1l1l11l_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡥࡧࡷࡩࡷࡳࡩ࡯ࡧࠣࡪࡦ࡯࡬ࡶࡴࡨࠤࡷ࡫ࡡࡴࡱࡱ࠾ࠥࢁ࠰ࡾࠤჶ").format(e)
            )
    if (bstack1l1l11ll1_opy_ != bstack1l1l11l_opy_ (u"ࠥࠦჷ")):
        try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
        except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
        threading.current_thread().bstackTestErrorMessages.append(str(bstack1l1l11ll1_opy_))
    try:
        if (passed):
            item._driver.execute_script(
                bstack1l1l11l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡤࡲࡳࡵࡴࡢࡶࡨࠦ࠱ࠦ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡧࡲࡨࡷࡰࡩࡳࡺࡳࠣ࠼ࠣࡿࡡࠐࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤ࡬ࡲ࡫ࡵࠢ࠭ࠢ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠧࡪࡡࡵࡣࠥ࠾ࠥ࠭ჸ")
                + json.dumps(bstack1l1l11l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠦࠨჹ"))
                + bstack1l1l11l_opy_ (u"ࠨ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࢂࡢࠊࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽࠣჺ")
            )
        else:
            item._driver.execute_script(
                bstack1l1l11l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࡠࠏࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠢ࠭ࠢ࡟ࠎࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡫ࡲࡳࡱࡵࠦ࠱ࠦ࡜ࠋࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠤࡧࡥࡹࡧࠢ࠻ࠢࠪ჻")
                + json.dumps(str(bstack1l1l11ll1_opy_))
                + bstack1l1l11l_opy_ (u"ࠣ࡞ࠍࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࡽ࡝ࠌࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࠢࠣࠤࠥࠦࠠࠡࡿࠥჼ")
            )
    except Exception as e:
        summary.append(bstack1l1l11l_opy_ (u"ࠤ࡚ࡅࡗࡔࡉࡏࡉ࠽ࠤࡋࡧࡩ࡭ࡧࡧࠤࡹࡵࠠࡢࡰࡱࡳࡹࡧࡴࡦ࠼ࠣࡿ࠵ࢃࠢჽ").format(e))
def bstack1l11l1lll1_opy_(item, report, summary, bstack1l11l11l1l_opy_):
    if report.when in [bstack1l1l11l_opy_ (u"ࠥࡷࡪࡺࡵࡱࠤჾ"), bstack1l1l11l_opy_ (u"ࠦࡹ࡫ࡡࡳࡦࡲࡻࡳࠨჿ")]:
        return
    if (str(bstack1l11l11l1l_opy_).lower() != bstack1l1l11l_opy_ (u"ࠬࡺࡲࡶࡧࠪᄀ")):
        bstack1ll111ll1_opy_(item._page, report.nodeid)
    passed = report.passed or (report.failed and hasattr(report, bstack1l1l11l_opy_ (u"ࠨࡷࡢࡵࡻࡪࡦ࡯࡬ࠣᄁ")))
    bstack1l1l11ll1_opy_ = bstack1l1l11l_opy_ (u"ࠢࠣᄂ")
    if not passed:
        try:
            bstack1l1l11ll1_opy_ = report.longrepr.reprcrash
        except Exception as e:
            summary.append(
                bstack1l1l11l_opy_ (u"࡙ࠣࡄࡖࡓࡏࡎࡈ࠼ࠣࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡤࡦࡶࡨࡶࡲ࡯࡮ࡦࠢࡩࡥ࡮ࡲࡵࡳࡧࠣࡶࡪࡧࡳࡰࡰ࠽ࠤࢀ࠶ࡽࠣᄃ").format(e)
            )
    try:
        if passed:
            bstack11ll11111_opy_(item._page, bstack1l1l11l_opy_ (u"ࠤࡳࡥࡸࡹࡥࡥࠤᄄ"))
        else:
            if bstack1l1l11ll1_opy_:
                bstack1111lll1l_opy_(item._page, str(bstack1l1l11ll1_opy_), bstack1l1l11l_opy_ (u"ࠥࡩࡷࡸ࡯ࡳࠤᄅ"))
                bstack11ll11111_opy_(item._page, bstack1l1l11l_opy_ (u"ࠦ࡫ࡧࡩ࡭ࡧࡧࠦᄆ"), str(bstack1l1l11ll1_opy_))
            else:
                bstack11ll11111_opy_(item._page, bstack1l1l11l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧᄇ"))
    except Exception as e:
        summary.append(bstack1l1l11l_opy_ (u"ࠨࡗࡂࡔࡑࡍࡓࡍ࠺ࠡࡈࡤ࡭ࡱ࡫ࡤࠡࡶࡲࠤࡺࡶࡤࡢࡶࡨࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷ࠿ࠦࡻ࠱ࡿࠥᄈ").format(e))
try:
    from typing import Generator
    import pytest_playwright.pytest_playwright as p
    @pytest.fixture
    def page(context: BrowserContext, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
        page = context.new_page()
        request.node._page = page
        yield page
except:
    pass
def pytest_addoption(parser):
    parser.addoption(bstack1l1l11l_opy_ (u"ࠢ࠮࠯ࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠦᄉ"), default=bstack1l1l11l_opy_ (u"ࠣࡈࡤࡰࡸ࡫ࠢᄊ"), help=bstack1l1l11l_opy_ (u"ࠤࡄࡹࡹࡵ࡭ࡢࡶ࡬ࡧࠥࡹࡥࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡲࡦࡳࡥࠣᄋ"))
    try:
        import pytest_selenium.pytest_selenium
    except:
        parser.addoption(bstack1l1l11l_opy_ (u"ࠥ࠱࠲ࡪࡲࡪࡸࡨࡶࠧᄌ"), action=bstack1l1l11l_opy_ (u"ࠦࡸࡺ࡯ࡳࡧࠥᄍ"), default=bstack1l1l11l_opy_ (u"ࠧࡩࡨࡳࡱࡰࡩࠧᄎ"),
                         help=bstack1l1l11l_opy_ (u"ࠨࡄࡳ࡫ࡹࡩࡷࠦࡴࡰࠢࡵࡹࡳࠦࡴࡦࡵࡷࡷࠧᄏ"))
def bstack1l11ll11l1_opy_(log):
    if log[bstack1l1l11l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᄐ")] == bstack1l1l11l_opy_ (u"ࠨ࡞ࡱࠫᄑ"):
        return
    bstack1llll1lll1_opy_.bstack1l1l111111_opy_([{
        bstack1l1l11l_opy_ (u"ࠩ࡯ࡩࡻ࡫࡬ࠨᄒ"): log[bstack1l1l11l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩᄓ")],
        bstack1l1l11l_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧᄔ"): datetime.datetime.utcnow().isoformat() + bstack1l1l11l_opy_ (u"ࠬࡠࠧᄕ"),
        bstack1l1l11l_opy_ (u"࠭࡭ࡦࡵࡶࡥ࡬࡫ࠧᄖ"): log[bstack1l1l11l_opy_ (u"ࠧ࡮ࡧࡶࡷࡦ࡭ࡥࠨᄗ")],
        bstack1l1l11l_opy_ (u"ࠨࡶࡨࡷࡹࡥࡲࡶࡰࡢࡹࡺ࡯ࡤࠨᄘ"): bstack1l11ll1lll_opy_
    }])
bstack1l11ll1l11_opy_ = bstack1ll11l1lll_opy_(bstack1l11ll11l1_opy_)
def pytest_runtest_call(item):
    try:
        if not bstack1llll1lll1_opy_.on():
            return
        global bstack1l11ll1lll_opy_, bstack1l11ll1l11_opy_
        bstack1l11ll1l11_opy_.start()
        bstack1l11ll111l_opy_ = {
            bstack1l1l11l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧᄙ"): uuid4().__str__(),
            bstack1l1l11l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᄚ"): datetime.datetime.utcnow().isoformat() + bstack1l1l11l_opy_ (u"ࠫ࡟࠭ᄛ")
        }
        bstack1l11ll1lll_opy_ = bstack1l11ll111l_opy_[bstack1l1l11l_opy_ (u"ࠬࡻࡵࡪࡦࠪᄜ")]
        threading.current_thread().bstack1l11ll1lll_opy_ = bstack1l11ll1lll_opy_
        _1l11ll1l1l_opy_[item.nodeid] = {**_1l11ll1l1l_opy_[item.nodeid], **bstack1l11ll111l_opy_}
        bstack1l11l1ll1l_opy_(item, _1l11ll1l1l_opy_[item.nodeid], bstack1l1l11l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧᄝ"))
    except Exception as err:
        print(bstack1l1l11l_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡰࡺࡶࡨࡷࡹࡥࡲࡶࡰࡷࡩࡸࡺ࡟ࡤࡣ࡯ࡰ࠿ࠦࡻࡾࠩᄞ"), str(err))
def pytest_runtest_setup(item):
    try:
        if not bstack1llll1lll1_opy_.on():
            return
        uuid = uuid4().__str__()
        bstack1l11ll111l_opy_ = {
            bstack1l1l11l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ᄟ"): uuid,
            bstack1l1l11l_opy_ (u"ࠩࡶࡸࡦࡸࡴࡦࡦࡢࡥࡹ࠭ᄠ"): datetime.datetime.utcnow().isoformat() + bstack1l1l11l_opy_ (u"ࠪ࡞ࠬᄡ"),
            bstack1l1l11l_opy_ (u"ࠫࡹࡿࡰࡦࠩᄢ"): bstack1l1l11l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࠪᄣ"),
            bstack1l1l11l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩᄤ"): bstack1l1l11l_opy_ (u"ࠧࡃࡇࡉࡓࡗࡋ࡟ࡆࡃࡆࡌࠬᄥ")
        }
        threading.current_thread().bstack1l11l1l1ll_opy_ = uuid
        if not _1l11ll1l1l_opy_.get(item.nodeid, None):
            _1l11ll1l1l_opy_[item.nodeid] = {bstack1l1l11l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧᄦ"): []}
        _1l11ll1l1l_opy_[item.nodeid][bstack1l1l11l_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨᄧ")].append(bstack1l11ll111l_opy_[bstack1l1l11l_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᄨ")])
        _1l11ll1l1l_opy_[item.nodeid + bstack1l1l11l_opy_ (u"ࠫ࠲ࡹࡥࡵࡷࡳࠫᄩ")] = bstack1l11ll111l_opy_
        bstack1l11l1ll11_opy_(item, bstack1l11ll111l_opy_, bstack1l1l11l_opy_ (u"ࠬࡎ࡯ࡰ࡭ࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭ᄪ"))
    except Exception as err:
        print(bstack1l1l11l_opy_ (u"࠭ࡅࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶࡹࡵࡧࡶࡸࡤࡸࡵ࡯ࡶࡨࡷࡹࡥࡳࡦࡶࡸࡴ࠿ࠦࡻࡾࠩᄫ"), str(err))
def pytest_runtest_teardown(item):
    try:
        if not bstack1llll1lll1_opy_.on():
            return
        bstack1l11ll111l_opy_ = {
            bstack1l1l11l_opy_ (u"ࠧࡶࡷ࡬ࡨࠬᄬ"): uuid4().__str__(),
            bstack1l1l11l_opy_ (u"ࠨࡵࡷࡥࡷࡺࡥࡥࡡࡤࡸࠬᄭ"): datetime.datetime.utcnow().isoformat() + bstack1l1l11l_opy_ (u"ࠩ࡝ࠫᄮ"),
            bstack1l1l11l_opy_ (u"ࠪࡸࡾࡶࡥࠨᄯ"): bstack1l1l11l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࠩᄰ"),
            bstack1l1l11l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡸࡾࡶࡥࠨᄱ"): bstack1l1l11l_opy_ (u"࠭ࡁࡇࡖࡈࡖࡤࡋࡁࡄࡊࠪᄲ")
        }
        _1l11ll1l1l_opy_[item.nodeid + bstack1l1l11l_opy_ (u"ࠧ࠮ࡶࡨࡥࡷࡪ࡯ࡸࡰࠪᄳ")] = bstack1l11ll111l_opy_
        bstack1l11l1ll11_opy_(item, bstack1l11ll111l_opy_, bstack1l1l11l_opy_ (u"ࠨࡊࡲࡳࡰࡘࡵ࡯ࡕࡷࡥࡷࡺࡥࡥࠩᄴ"))
    except Exception as err:
        print(bstack1l1l11l_opy_ (u"ࠩࡈࡼࡨ࡫ࡰࡵ࡫ࡲࡲࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴࡠࡴࡸࡲࡹ࡫ࡳࡵࡡࡷࡩࡦࡸࡤࡰࡹࡱ࠾ࠥࢁࡽࠨᄵ"), str(err))
@pytest.hookimpl(hookwrapper=True)
def pytest_fixture_setup(fixturedef):
    start_time = datetime.datetime.now()
    outcome = yield
    try:
        if not bstack1llll1lll1_opy_.on():
            return
        bstack1l11l1l11l_opy_ = threading.current_thread().bstack1l11l1l1ll_opy_
        log = {
            bstack1l1l11l_opy_ (u"ࠪ࡯࡮ࡴࡤࠨᄶ"): bstack1l1l11l_opy_ (u"࡙ࠫࡋࡓࡕࡡࡖࡘࡊࡖࠧᄷ"),
            bstack1l1l11l_opy_ (u"ࠬࡳࡥࡴࡵࡤ࡫ࡪ࠭ᄸ"): fixturedef.argname,
            bstack1l1l11l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡷࡻ࡮ࡠࡷࡸ࡭ࡩ࠭ᄹ"): threading.current_thread().bstack1l11l1l1ll_opy_,
            bstack1l1l11l_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪᄺ"): bstack1lll111ll_opy_(),
            bstack1l1l11l_opy_ (u"ࠨ࡮ࡨࡺࡪࡲࠧᄻ"): bstack1l1lllll11_opy_(outcome),
            bstack1l1l11l_opy_ (u"ࠩࡧࡹࡷࡧࡴࡪࡱࡱࠫᄼ"): (datetime.datetime.now() - start_time).total_seconds() * 1000,
        }
        if log[bstack1l1l11l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩᄽ")] == bstack1l1l11l_opy_ (u"ࠫ࡫ࡧࡩ࡭ࡧࡧࠫᄾ"):
            log[bstack1l1l11l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡸࡶࡪࡥࡴࡺࡲࡨࠫᄿ")] = bstack1l1l11l_opy_ (u"࠭ࡕ࡯ࡪࡤࡲࡩࡲࡥࡥࡇࡵࡶࡴࡸࠧᅀ")
            log[bstack1l1l11l_opy_ (u"ࠧࡧࡣ࡬ࡰࡺࡸࡥࠨᅁ")] = outcome.exception.__str__()
        if not _1l11l111l1_opy_.get(bstack1l11l1l11l_opy_, None):
            _1l11l111l1_opy_[bstack1l11l1l11l_opy_] = []
        _1l11l111l1_opy_[bstack1l11l1l11l_opy_].append(log)
    except Exception as err:
        print(bstack1l1l11l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱࡻࡷࡩࡸࡺ࡟ࡧ࡫ࡻࡸࡺࡸࡥࡠࡵࡨࡸࡺࡶ࠺ࠡࡽࢀࠫᅂ"), str(err))
@bstack1llll1lll1_opy_.bstack1l1l11l11l_opy_
def bstack1l11l11lll_opy_(item, call, report):
    try:
        if report.when == bstack1l1l11l_opy_ (u"ࠩࡦࡥࡱࡲࠧᅃ"):
            bstack1l11ll1l11_opy_.reset()
        if report.when == bstack1l1l11l_opy_ (u"ࠪࡧࡦࡲ࡬ࠨᅄ"):
            _1l11ll1l1l_opy_[item.nodeid][bstack1l1l11l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩᅅ")] = datetime.datetime.utcfromtimestamp(report.stop).isoformat() + bstack1l1l11l_opy_ (u"ࠬࡠࠧᅆ")
            bstack1l11l1ll1l_opy_(item, _1l11ll1l1l_opy_[item.nodeid], bstack1l1l11l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡆࡪࡰ࡬ࡷ࡭࡫ࡤࠨᅇ"), report, call)
        elif report.when in [bstack1l1l11l_opy_ (u"ࠧࡴࡧࡷࡹࡵ࠭ᅈ"), bstack1l1l11l_opy_ (u"ࠨࡶࡨࡥࡷࡪ࡯ࡸࡰࠪᅉ")]:
            bstack1l11l111ll_opy_ = item.nodeid + bstack1l1l11l_opy_ (u"ࠩ࠰ࠫᅊ") + report.when
            if report.skipped:
                hook_type = bstack1l1l11l_opy_ (u"ࠪࡆࡊࡌࡏࡓࡇࡢࡉࡆࡉࡈࠨᅋ") if report.when == bstack1l1l11l_opy_ (u"ࠫࡸ࡫ࡴࡶࡲࠪᅌ") else bstack1l1l11l_opy_ (u"ࠬࡇࡆࡕࡇࡕࡣࡊࡇࡃࡉࠩᅍ")
                _1l11ll1l1l_opy_[bstack1l11l111ll_opy_] = {
                    bstack1l1l11l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫᅎ"): uuid4().__str__(),
                    bstack1l1l11l_opy_ (u"ࠧࡴࡶࡤࡶࡹ࡫ࡤࡠࡣࡷࠫᅏ"): datetime.datetime.utcfromtimestamp(report.start).isoformat() + bstack1l1l11l_opy_ (u"ࠨ࡜ࠪᅐ"),
                    bstack1l1l11l_opy_ (u"ࠩ࡫ࡳࡴࡱ࡟ࡵࡻࡳࡩࠬᅑ"): hook_type
                }
            _1l11ll1l1l_opy_[bstack1l11l111ll_opy_][bstack1l1l11l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨᅒ")] = datetime.datetime.utcfromtimestamp(report.stop).isoformat() + bstack1l1l11l_opy_ (u"ࠫ࡟࠭ᅓ")
            if report.when == bstack1l1l11l_opy_ (u"ࠬࡹࡥࡵࡷࡳࠫᅔ"):
                bstack1l11l1l11l_opy_ = _1l11ll1l1l_opy_[bstack1l11l111ll_opy_][bstack1l1l11l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫᅕ")]
                if _1l11l111l1_opy_.get(bstack1l11l1l11l_opy_, None):
                    bstack1llll1lll1_opy_.bstack1l1l11ll1l_opy_(_1l11l111l1_opy_[bstack1l11l1l11l_opy_])
            bstack1l11l1ll11_opy_(item, _1l11ll1l1l_opy_[bstack1l11l111ll_opy_], bstack1l1l11l_opy_ (u"ࠧࡉࡱࡲ࡯ࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩᅖ"), report, call)
            if report.when == bstack1l1l11l_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧᅗ"):
                if report.outcome == bstack1l1l11l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩᅘ"):
                    bstack1l11ll111l_opy_ = {
                        bstack1l1l11l_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᅙ"): uuid4().__str__(),
                        bstack1l1l11l_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨᅚ"): bstack1lll111ll_opy_(),
                        bstack1l1l11l_opy_ (u"ࠬ࡬ࡩ࡯࡫ࡶ࡬ࡪࡪ࡟ࡢࡶࠪᅛ"): bstack1lll111ll_opy_()
                    }
                    _1l11ll1l1l_opy_[item.nodeid] = {**_1l11ll1l1l_opy_[item.nodeid], **bstack1l11ll111l_opy_}
                    bstack1l11l1ll1l_opy_(item, _1l11ll1l1l_opy_[item.nodeid], bstack1l1l11l_opy_ (u"࠭ࡔࡦࡵࡷࡖࡺࡴࡓࡵࡣࡵࡸࡪࡪࠧᅜ"))
                    bstack1l11l1ll1l_opy_(item, _1l11ll1l1l_opy_[item.nodeid], bstack1l1l11l_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡇ࡫ࡱ࡭ࡸ࡮ࡥࡥࠩᅝ"), report, call)
    except Exception as err:
        print(bstack1l1l11l_opy_ (u"ࠨࡇࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡩࡣࡱࡨࡱ࡫࡟ࡰ࠳࠴ࡽࡤࡺࡥࡴࡶࡢࡩࡻ࡫࡮ࡵ࠼ࠣࡿࢂ࠭ᅞ"), str(err))
def bstack1l11l1l111_opy_(test, bstack1l11ll111l_opy_, result=None, call=None, bstack11l11ll1_opy_=None):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    bstack1l11l1llll_opy_ = {
        bstack1l1l11l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧᅟ"): bstack1l11ll111l_opy_[bstack1l1l11l_opy_ (u"ࠪࡹࡺ࡯ࡤࠨᅠ")],
        bstack1l1l11l_opy_ (u"ࠫࡹࡿࡰࡦࠩᅡ"): bstack1l1l11l_opy_ (u"ࠬࡺࡥࡴࡶࠪᅢ"),
        bstack1l1l11l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫᅣ"): test.name,
        bstack1l1l11l_opy_ (u"ࠧࡣࡱࡧࡽࠬᅤ"): {
            bstack1l1l11l_opy_ (u"ࠨ࡮ࡤࡲ࡬࠭ᅥ"): bstack1l1l11l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩᅦ"),
            bstack1l1l11l_opy_ (u"ࠪࡧࡴࡪࡥࠨᅧ"): inspect.getsource(test.obj)
        },
        bstack1l1l11l_opy_ (u"ࠫ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨᅨ"): test.name,
        bstack1l1l11l_opy_ (u"ࠬࡹࡣࡰࡲࡨࠫᅩ"): test.name,
        bstack1l1l11l_opy_ (u"࠭ࡳࡤࡱࡳࡩࡸ࠭ᅪ"): bstack1llll1lll1_opy_.bstack1l1l111l1l_opy_(test),
        bstack1l1l11l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪᅫ"): file_path,
        bstack1l1l11l_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࠪᅬ"): file_path,
        bstack1l1l11l_opy_ (u"ࠩࡵࡩࡸࡻ࡬ࡵࠩᅭ"): bstack1l1l11l_opy_ (u"ࠪࡴࡪࡴࡤࡪࡰࡪࠫᅮ"),
        bstack1l1l11l_opy_ (u"ࠫࡻࡩ࡟ࡧ࡫࡯ࡩࡵࡧࡴࡩࠩᅯ"): file_path,
        bstack1l1l11l_opy_ (u"ࠬࡹࡴࡢࡴࡷࡩࡩࡥࡡࡵࠩᅰ"): bstack1l11ll111l_opy_[bstack1l1l11l_opy_ (u"࠭ࡳࡵࡣࡵࡸࡪࡪ࡟ࡢࡶࠪᅱ")],
        bstack1l1l11l_opy_ (u"ࠧࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪᅲ"): bstack1l1l11l_opy_ (u"ࠨࡒࡼࡸࡪࡹࡴࠨᅳ"),
        bstack1l1l11l_opy_ (u"ࠩࡦࡹࡸࡺ࡯࡮ࡔࡨࡶࡺࡴࡐࡢࡴࡤࡱࠬᅴ"): {
            bstack1l1l11l_opy_ (u"ࠪࡶࡪࡸࡵ࡯ࡡࡱࡥࡲ࡫ࠧᅵ"): test.nodeid
        },
        bstack1l1l11l_opy_ (u"ࠫࡹࡧࡧࡴࠩᅶ"): bstack1ll11111l1_opy_(test.own_markers)
    }
    if bstack11l11ll1_opy_ == bstack1l1l11l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙࡫ࡪࡲࡳࡩࡩ࠭ᅷ"):
        bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"࠭ࡲࡦࡵࡸࡰࡹ࠭ᅸ")] = bstack1l1l11l_opy_ (u"ࠧࡴ࡭࡬ࡴࡵ࡫ࡤࠨᅹ")
        bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"ࠨࡪࡲࡳࡰࡹࠧᅺ")] = bstack1l11ll111l_opy_[bstack1l1l11l_opy_ (u"ࠩ࡫ࡳࡴࡱࡳࠨᅻ")]
        bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"ࠪࡪ࡮ࡴࡩࡴࡪࡨࡨࡤࡧࡴࠨᅼ")] = bstack1l11ll111l_opy_[bstack1l1l11l_opy_ (u"ࠫ࡫࡯࡮ࡪࡵ࡫ࡩࡩࡥࡡࡵࠩᅽ")]
    if result:
        bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬᅾ")] = result.outcome
        bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧᅿ")] = result.duration * 1000
        bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬᆀ")] = bstack1l11ll111l_opy_[bstack1l1l11l_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ᆁ")]
        if result.failed:
            bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨᆂ")] = bstack1llll1lll1_opy_.bstack1l1l1111l1_opy_(call.excinfo.typename)
            bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫᆃ")] = bstack1llll1lll1_opy_.bstack1l11lll1l1_opy_(call.excinfo, result)
        bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"ࠫ࡭ࡵ࡯࡬ࡵࠪᆄ")] = bstack1l11ll111l_opy_[bstack1l1l11l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡶࠫᆅ")]
    return bstack1l11l1llll_opy_
def bstack1l11l1l1l1_opy_(test, bstack1l11ll1111_opy_, bstack11l11ll1_opy_, result, call):
    file_path = os.path.relpath(test.fspath.strpath, start=os.getcwd())
    hook_type = bstack1l11ll1111_opy_[bstack1l1l11l_opy_ (u"࠭ࡨࡰࡱ࡮ࡣࡹࡿࡰࡦࠩᆆ")]
    hook_data = {
        bstack1l1l11l_opy_ (u"ࠧࡶࡷ࡬ࡨࠬᆇ"): bstack1l11ll1111_opy_[bstack1l1l11l_opy_ (u"ࠨࡷࡸ࡭ࡩ࠭ᆈ")],
        bstack1l1l11l_opy_ (u"ࠩࡷࡽࡵ࡫ࠧᆉ"): bstack1l1l11l_opy_ (u"ࠪ࡬ࡴࡵ࡫ࠨᆊ"),
        bstack1l1l11l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩᆋ"): bstack1l1l11l_opy_ (u"ࠬࢁࡽࠡࡨࡲࡶࠥࢁࡽࠨᆌ").format(bstack1llll1lll1_opy_.bstack1l1l1l1111_opy_(hook_type), test.name),
        bstack1l1l11l_opy_ (u"࠭ࡢࡰࡦࡼࠫᆍ"): {
            bstack1l1l11l_opy_ (u"ࠧ࡭ࡣࡱ࡫ࠬᆎ"): bstack1l1l11l_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨᆏ"),
            bstack1l1l11l_opy_ (u"ࠩࡦࡳࡩ࡫ࠧᆐ"): None
        },
        bstack1l1l11l_opy_ (u"ࠪࡷࡨࡵࡰࡦࠩᆑ"): test.name,
        bstack1l1l11l_opy_ (u"ࠫࡸࡩ࡯ࡱࡧࡶࠫᆒ"): bstack1llll1lll1_opy_.bstack1l1l111l1l_opy_(test),
        bstack1l1l11l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨᆓ"): file_path,
        bstack1l1l11l_opy_ (u"࠭࡬ࡰࡥࡤࡸ࡮ࡵ࡮ࠨᆔ"): file_path,
        bstack1l1l11l_opy_ (u"ࠧࡳࡧࡶࡹࡱࡺࠧᆕ"): bstack1l1l11l_opy_ (u"ࠨࡲࡨࡲࡩ࡯࡮ࡨࠩᆖ"),
        bstack1l1l11l_opy_ (u"ࠩࡹࡧࡤ࡬ࡩ࡭ࡧࡳࡥࡹ࡮ࠧᆗ"): file_path,
        bstack1l1l11l_opy_ (u"ࠪࡷࡹࡧࡲࡵࡧࡧࡣࡦࡺࠧᆘ"): bstack1l11ll1111_opy_[bstack1l1l11l_opy_ (u"ࠫࡸࡺࡡࡳࡶࡨࡨࡤࡧࡴࠨᆙ")],
        bstack1l1l11l_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨᆚ"): bstack1l1l11l_opy_ (u"࠭ࡐࡺࡶࡨࡷࡹ࠭ᆛ"),
        bstack1l1l11l_opy_ (u"ࠧࡩࡱࡲ࡯ࡤࡺࡹࡱࡧࠪᆜ"): bstack1l11ll1111_opy_[bstack1l1l11l_opy_ (u"ࠨࡪࡲࡳࡰࡥࡴࡺࡲࡨࠫᆝ")]
    }
    if _1l11ll1l1l_opy_.get(test.nodeid, None) is not None and _1l11ll1l1l_opy_[test.nodeid].get(bstack1l1l11l_opy_ (u"ࠩࡸࡹ࡮ࡪࠧᆞ"), None):
        hook_data[bstack1l1l11l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࡤ࡯ࡤࠨᆟ")] = _1l11ll1l1l_opy_[test.nodeid][bstack1l1l11l_opy_ (u"ࠫࡺࡻࡩࡥࠩᆠ")]
    if result:
        hook_data[bstack1l1l11l_opy_ (u"ࠬࡸࡥࡴࡷ࡯ࡸࠬᆡ")] = result.outcome
        hook_data[bstack1l1l11l_opy_ (u"࠭ࡤࡶࡴࡤࡸ࡮ࡵ࡮ࡠ࡫ࡱࡣࡲࡹࠧᆢ")] = result.duration * 1000
        hook_data[bstack1l1l11l_opy_ (u"ࠧࡧ࡫ࡱ࡭ࡸ࡮ࡥࡥࡡࡤࡸࠬᆣ")] = bstack1l11ll1111_opy_[bstack1l1l11l_opy_ (u"ࠨࡨ࡬ࡲ࡮ࡹࡨࡦࡦࡢࡥࡹ࠭ᆤ")]
        if result.failed:
            hook_data[bstack1l1l11l_opy_ (u"ࠩࡩࡥ࡮ࡲࡵࡳࡧࡢࡸࡾࡶࡥࠨᆥ")] = bstack1llll1lll1_opy_.bstack1l1l1111l1_opy_(call.excinfo.typename)
            hook_data[bstack1l1l11l_opy_ (u"ࠪࡪࡦ࡯࡬ࡶࡴࡨࠫᆦ")] = bstack1llll1lll1_opy_.bstack1l11lll1l1_opy_(call.excinfo, result)
    return hook_data
def bstack1l11l1ll1l_opy_(test, bstack1l11ll111l_opy_, bstack11l11ll1_opy_, result=None, call=None):
    bstack1l11l1llll_opy_ = bstack1l11l1l111_opy_(test, bstack1l11ll111l_opy_, result, call, bstack11l11ll1_opy_)
    driver = getattr(test, bstack1l1l11l_opy_ (u"ࠫࡤࡪࡲࡪࡸࡨࡶࠬᆧ"), None)
    if bstack11l11ll1_opy_ == bstack1l1l11l_opy_ (u"࡚ࠬࡥࡴࡶࡕࡹࡳ࡙ࡴࡢࡴࡷࡩࡩ࠭ᆨ") and driver:
        bstack1l11l1llll_opy_[bstack1l1l11l_opy_ (u"࠭ࡩ࡯ࡶࡨ࡫ࡷࡧࡴࡪࡱࡱࡷࠬᆩ")] = bstack1llll1lll1_opy_.bstack1l11lll11l_opy_(driver)
    if bstack11l11ll1_opy_ == bstack1l1l11l_opy_ (u"ࠧࡕࡧࡶࡸࡗࡻ࡮ࡔ࡭࡬ࡴࡵ࡫ࡤࠨᆪ"):
        bstack11l11ll1_opy_ = bstack1l1l11l_opy_ (u"ࠨࡖࡨࡷࡹࡘࡵ࡯ࡈ࡬ࡲ࡮ࡹࡨࡦࡦࠪᆫ")
    bstack1l11ll11ll_opy_ = {
        bstack1l1l11l_opy_ (u"ࠩࡨࡺࡪࡴࡴࡠࡶࡼࡴࡪ࠭ᆬ"): bstack11l11ll1_opy_,
        bstack1l1l11l_opy_ (u"ࠪࡸࡪࡹࡴࡠࡴࡸࡲࠬᆭ"): bstack1l11l1llll_opy_
    }
    bstack1llll1lll1_opy_.bstack1l1l1l11l1_opy_(bstack1l11ll11ll_opy_)
def bstack1l11l1ll11_opy_(test, bstack1l11ll111l_opy_, bstack11l11ll1_opy_, result=None, call=None):
    hook_data = bstack1l11l1l1l1_opy_(test, bstack1l11ll111l_opy_, bstack11l11ll1_opy_, result, call)
    bstack1l11ll11ll_opy_ = {
        bstack1l1l11l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡸࡾࡶࡥࠨᆮ"): bstack11l11ll1_opy_,
        bstack1l1l11l_opy_ (u"ࠬ࡮࡯ࡰ࡭ࡢࡶࡺࡴࠧᆯ"): hook_data
    }
    bstack1llll1lll1_opy_.bstack1l1l1l11l1_opy_(bstack1l11ll11ll_opy_)
@pytest.fixture(autouse=True)
def second_fixture(caplog, request):
    yield
    try:
        if not bstack1llll1lll1_opy_.on():
            return
        records = caplog.get_records(bstack1l1l11l_opy_ (u"࠭ࡣࡢ࡮࡯ࠫᆰ"))
        bstack1l1l1l11ll_opy_ = []
        for record in records:
            if record.message == bstack1l1l11l_opy_ (u"ࠧ࡝ࡰࠪᆱ"):
                continue
            bstack1l1l1l11ll_opy_.append({
                bstack1l1l11l_opy_ (u"ࠨࡶ࡬ࡱࡪࡹࡴࡢ࡯ࡳࠫᆲ"): datetime.datetime.utcfromtimestamp(record.created).isoformat() + bstack1l1l11l_opy_ (u"ࠩ࡝ࠫᆳ"),
                bstack1l1l11l_opy_ (u"ࠪࡰࡪࡼࡥ࡭ࠩᆴ"): record.levelname,
                bstack1l1l11l_opy_ (u"ࠫࡲ࡫ࡳࡴࡣࡪࡩࠬᆵ"): record.message,
                bstack1l1l11l_opy_ (u"ࠬࡺࡥࡴࡶࡢࡶࡺࡴ࡟ࡶࡷ࡬ࡨࠬᆶ"): _1l11ll1l1l_opy_.get(request.node.nodeid).get(bstack1l1l11l_opy_ (u"࠭ࡵࡶ࡫ࡧࠫᆷ"))
            })
        bstack1llll1lll1_opy_.bstack1l1l111111_opy_(bstack1l1l1l11ll_opy_)
    except Exception as err:
        print(bstack1l1l11l_opy_ (u"ࠧࡆࡺࡦࡩࡵࡺࡩࡰࡰࠣ࡭ࡳࠦࡳࡦࡥࡲࡲࡩࡥࡦࡪࡺࡷࡹࡷ࡫࠺ࠡࡽࢀࠫᆸ"), str(err))
def bstack1l11l11ll1_opy_(driver_command, response):
    if driver_command == bstack1l1l11l_opy_ (u"ࠨࡵࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࠬᆹ"):
        bstack1llll1lll1_opy_.bstack1l1l11llll_opy_({
            bstack1l1l11l_opy_ (u"ࠩ࡬ࡱࡦ࡭ࡥࠨᆺ"): response[bstack1l1l11l_opy_ (u"ࠪࡺࡦࡲࡵࡦࠩᆻ")],
            bstack1l1l11l_opy_ (u"ࠫࡹ࡫ࡳࡵࡡࡵࡹࡳࡥࡵࡶ࡫ࡧࠫᆼ"): bstack1l11ll1lll_opy_
        })
@bstack1llll1lll1_opy_.bstack1l1l11l11l_opy_
def bstack1l11ll1ll1_opy_():
    if bstack1l1llll11l_opy_():
        bstack1l1l1ll11l_opy_(bstack1l11l11ll1_opy_)
bstack1l11ll1ll1_opy_()