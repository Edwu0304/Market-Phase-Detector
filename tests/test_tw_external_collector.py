from market_phase_detector.collectors.tw_external import (
    fetch_latest_twse_margin,
    fetch_mol_claims_annual,
    parse_ncu_cci_archive_page,
    parse_ncu_cci_pdf_text,
    parse_cbc_m2_from_homepage,
    parse_cier_pmi_article,
    parse_cier_pmi_history_page,
    parse_ncu_cci_from_news,
    parse_tw_revenue_snapshot,
    parse_twse_market_snapshot,
)


def test_parse_cier_pmi_article_extracts_month_and_value() -> None:
    html = """
    <html>
      <body>
        <p>2026年3月台灣製造業採購經理人指數(PMI) (2026年4月1日發布)</p>
        <p>
          整體季節調整後之台灣製造業PMI下滑3.1個百分點至55.4%，
          未來六個月展望指數為61.0%。
        </p>
      </body>
    </html>
    """

    record = parse_cier_pmi_article(html, "https://example.com/pmi")

    assert record == {
        "date": "2026-03",
        "pmi": 55.4,
        "source_url": "https://example.com/pmi",
    }


def test_parse_cier_pmi_history_page_extracts_monthly_rows() -> None:
    html = """
    <div
      class="eael-google-chart"
      data-data='[
        ["月份","臺灣製造業PMI","化學暨生技醫療"],
        ["2025/12",55.3,48.4],
        ["2026/01",57.2,55.9],
        ["2026/02",58.5,47.5],
        ["2026/03",55.4,52.9]
      ]'
    ></div>
    """

    records = parse_cier_pmi_history_page(html, "https://example.com/pmi-trend")

    assert records == [
        {"date": "2025-12", "pmi": 55.3, "source_url": "https://example.com/pmi-trend"},
        {"date": "2026-01", "pmi": 57.2, "source_url": "https://example.com/pmi-trend"},
        {"date": "2026-02", "pmi": 58.5, "source_url": "https://example.com/pmi-trend"},
        {"date": "2026-03", "pmi": 55.4, "source_url": "https://example.com/pmi-trend"},
    ]


def test_parse_cbc_m2_from_homepage_extracts_latest_value() -> None:
    html = """
    <div class="tabItem">
      <a href="#" title="貨幣總計數M2年增率">
        <h3>貨幣總計數M2年增率</h3>
        <span class="date">2026-03-19</span>
        <span class="info"><em>5.38%</em></span>
      </a>
    </div>
    """

    record = parse_cbc_m2_from_homepage(html)

    assert record == {
        "date": "2026-03",
        "m2_yoy": 5.38,
        "source_date": "2026-03-19",
    }


def test_parse_ncu_cci_from_news_extracts_latest_month_and_value() -> None:
    html = """
    <html>
      <body>
        <h2>115年3月消費者信心指數(CCI)調查總數為62.3點</h2>
        <p>較上月上升0.1點。</p>
      </body>
    </html>
    """

    record = parse_ncu_cci_from_news(html)

    assert record == {
        "date": "2026-03",
        "cci_total": 62.3,
    }


def test_parse_ncu_cci_archive_page_returns_latest_report_pdf() -> None:
    html = """
    <table>
      <tbody>
        <tr>
          <td><a href="cci/cci_news1150127.pdf">消費者信心指數新聞稿1150127</a></td>
          <td><a href="cci/cci_1150127.pdf">115年01月份消費者信心指數調查報告</a></td>
        </tr>
        <tr>
          <td><a href="cci/cci_news1150327.pdf">消費者信心指數新聞稿1150327</a></td>
          <td><a href="cci/cci_1150327.pdf">115年03月份消費者信心指數調查報告</a></td>
        </tr>
      </tbody>
    </table>
    """

    record = parse_ncu_cci_archive_page(html, "https://rcted.ncu.edu.tw/cci.asp")

    assert record == {
        "date": "2026-03",
        "source_url": "https://rcted.ncu.edu.tw/cci/cci_1150327.pdf",
    }


def test_parse_ncu_cci_pdf_text_extracts_total_index() -> None:
    pdf_text = """
    115年03月份消費者信心指數調查報告
    本月消費者信心指數(CCI)總指數為62.3點，與上個月比較上升0.1點。
    """

    record = parse_ncu_cci_pdf_text(pdf_text, "2026-03", "https://rcted.ncu.edu.tw/cci/cci_1150327.pdf")

    assert record == {
        "date": "2026-03",
        "cci_total": 62.3,
        "source_url": "https://rcted.ncu.edu.tw/cci/cci_1150327.pdf",
    }


def test_fetch_mol_claims_annual_ignores_notes_and_extracts_latest_year(monkeypatch) -> None:
    csv_text = """
" Year ",""," Cases of first"," Cases of re-application"," Grand total"," Cases of first"," Cases of re-confirm","  Amount","  Placement","  (Person)",
" 111年  2022 ","331983","70160","261823","330071","68056","262015","8120524","58875","5943",
" 112年  2023 ","396517","88124","308393","392193","85534","306659","9868584","70055","7680",
" 3.領滿失業給付期間者，自領滿之日起2年內再次請領失業給付，其失業給付以發給原給付期間之二分之一為 ","","","","     insurance program shall be added","","","","","",
    """.strip()

    class StubResponse:
        def __init__(self, content: bytes) -> None:
            self.content = content

        def raise_for_status(self) -> None:
            return None

    def stub_get(url: str, timeout: int, verify: bool = False):
        return StubResponse(csv_text.encode("big5", errors="replace"))

    monkeypatch.setattr("market_phase_detector.collectors.tw_external.requests.get", stub_get)

    rows = fetch_mol_claims_annual(None)

    assert rows == [
        {"date": "2022", "initial_claims": 70160, "year": 2022},
        {"date": "2023", "initial_claims": 88124, "year": 2023},
    ]


def test_fetch_latest_twse_margin_prefers_first_row_when_api_is_descending(monkeypatch) -> None:
    payload = {
        "chart": {
            "margin": [
                ["4/17", 8557238, 427120349, 183334],
                ["4/16", 8454685, 422408757, 178392],
                ["3/5", 7959571, 379166593, 225312],
            ]
        }
    }

    class StubResponse:
        def json(self):
            return payload

    def stub_get(url: str, timeout: int):
        return StubResponse()

    monkeypatch.setattr("market_phase_detector.collectors.tw_external.requests.get", stub_get)

    record = fetch_latest_twse_margin(None)

    assert record == {
        "date": "4/17",
        "margin_shares": 8557238,
        "margin_amount": 427120349,
        "short_shares": 183334,
    }


def test_parse_twse_market_snapshot_extracts_breadth_and_sector_leadership() -> None:
    payload = {
        "tables": [
            {
                "title": "115年04月10日 價格指數(臺灣證券交易所)",
                "fields": ["指數", "收盤指數", "漲跌(+/-)", "漲跌點數", "漲跌百分比(%)", "特殊處理註記"],
                "data": [
                    ["水泥類指數", "126.89", "+", "0.55", "0.44", ""],
                    ["塑膠類指數", "188.63", "-", "4.71", "-2.44", ""],
                    ["電機機械類指數", "473.53", "+", "8.54", "1.84", ""],
                ],
            },
            {
                "title": "漲跌證券數合計",
                "fields": ["類型", "整體市場", "股票"],
                "data": [
                    ["上漲(漲停)", "8,084(208)", "520(39)"],
                    ["下跌(跌停)", "3,989(78)", "452(1)"],
                    ["持平", "691", "94"],
                ],
            },
        ]
    }

    record = parse_twse_market_snapshot(payload, "2026-04-10")

    assert record == {
        "date": "2026-04-10",
        "advance_count": 520,
        "decline_count": 452,
        "unchanged_count": 94,
        "advance_decline_spread": 68,
        "breadth_ratio": 1.1504,
        "sector_advance_count": 2,
        "sector_decline_count": 1,
        "sector_breadth_ratio": 2.0,
        "sector_leader": "電機機械類指數",
        "sector_leader_return": 1.84,
        "sector_laggard": "塑膠類指數",
        "sector_laggard_return": -2.44,
    }


def test_parse_tw_revenue_snapshot_aggregates_yoy_growth() -> None:
    listed = [
        {"資料年月": "11503", "營業收入-當月營收": "100", "營業收入-去年當月營收": "80"},
        {"資料年月": "11503", "營業收入-當月營收": "200", "營業收入-去年當月營收": "160"},
    ]
    otc = [
        {"資料年月": "11503", "營業收入-當月營收": "150", "營業收入-去年當月營收": "120"},
    ]

    record = parse_tw_revenue_snapshot(listed, otc)

    assert record == {
        "date": "2026-03",
        "revenue_current_total": 450.0,
        "revenue_year_ago_total": 360.0,
        "revenue_yoy": 25.0,
    }
