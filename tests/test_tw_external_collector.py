from market_phase_detector.collectors.tw_external import (
    parse_cbc_m2_from_homepage,
    parse_cier_pmi_article,
    parse_cier_pmi_history_page,
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
