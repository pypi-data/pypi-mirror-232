"""
@Author: kang.yang
@Date: 2023/8/21 17:05
"""
import kuto
from kuto.ios import Elem
from kuto.ocr import OCRElem

"""
ocr识别可以配合安卓应用或者IOS应用进行使用
"""


class OcrPage(kuto.Page):
    searchBtn = Elem(text="搜索", className="XCUIElementTypeSearchField", desc='搜索框入口')
    searchInput = Elem(className="XCUIElementTypeSearchField", desc='搜索框')
    searchResult = Elem(xpath="//Table/Cell[2]", desc='搜索结果')
    schoolEntry = OCRElem(text="校园场馆", pos=12)

