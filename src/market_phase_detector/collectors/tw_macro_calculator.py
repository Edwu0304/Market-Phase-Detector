"""
台灣總經指標計算器

策略：全部使用 NDC ZIP 內的真實資料 + 計算衍生指標

NDC ZIP 內可用的真實指標：
- 領先/同時/落後指標綜合指數
- 景氣對策信號綜合分數
- 失業率
- 五大銀行新承做放款平均利率
- 全體金融機構放款與投資
- 貨幣總計數 M1B
- 股價指數
- 工業生產指數
- 工業及服務業加班工時
- 海關出口值
- 機械及電機設備進口值
- 製造業銷售量指數
- 批發、零售及餐飲業營業額
- 製造業存貨價值
"""

from statistics import mean


def compute_sahm_rule(unemployment_history: list[float]) -> float | None:
    """計算台灣版薩姆規則（SAHM Rule）
    
    原始公式：失業率 3 個月移動平均 - 過去 12 個月最低失業率 >= 0.5%
    
    Args:
        unemployment_history: 最近 12 個月的失業率列表
    
    Returns:
        SAHM 值，若 >= 0.5 表示衰退訊號
    """
    if len(unemployment_history) < 12:
        return None
    
    recent_3m_avg = mean(unemployment_history[-3:])
    trailing_12m_low = min(unemployment_history[-12:])
    
    return round(recent_3m_avg - trailing_12m_low, 4)


def compute_inventory_to_sales_ratio(
    inventory: float | None,
    inventory_prev: float | None,
    retail_sales: float | None,
    retail_sales_prev: float | None,
) -> dict | None:
    """計算庫存/銷售比（愛榭克榮景訊號）
    
    Args:
        inventory: 製造業存貨價值
        retail_sales: 批發、零售及餐飲業營業額
    
    Returns:
        庫存銷售比及趨勢
    """
    if not all([inventory, inventory_prev, retail_sales, retail_sales_prev]):
        return None
    
    inventory_yoy = (inventory - inventory_prev) / inventory_prev * 100 if inventory_prev else 0
    sales_yoy = (retail_sales - retail_sales_prev) / retail_sales_prev * 100 if retail_sales_prev else 0
    
    # 庫存/銷售比變化
    ratio_change = inventory_yoy - sales_yoy
    
    return {
        "inventory_yoy": round(inventory_yoy, 4),
        "sales_yoy": round(sales_yoy, 4),
        "ratio_change": round(ratio_change, 4),
        "trend": "accumulating" if ratio_change > 2 else ("clearing" if ratio_change < -2 else "stable"),
    }


def compute_real_interest_rate(
    bank_lending_rate: float | None,
    cpi_yoy: float | None,
) -> float | None:
    """計算實質利率（費雪方程式近似）
    
    實質利率 = 名目利率 - 通膨率
    
    Args:
        bank_lending_rate: 五大銀行新承做放款平均利率
        cpi_yoy: CPI 年增率
    
    Returns:
        實質利率
    """
    if bank_lending_rate is None or cpi_yoy is None:
        return None
    
    return round(bank_lending_rate - cpi_yoy, 4)


def compute_credit_impulse(
    total_credit: float | None,
    total_credit_prev: float | None,
    total_credit_prev2: float | None,
) -> float | None:
    """計算信用動能（Credit Impulse）
    
    信用動能 = 本期信用變化 - 上期信用變化
    正值表示信用擴張加速
    """
    if not all([total_credit, total_credit_prev, total_credit_prev2]):
        return None
    
    current_change = total_credit - total_credit_prev
    prev_change = total_credit_prev - total_credit_prev2
    
    return round(current_change - prev_change, 4)


def compute_tw_full_metrics(metrics: dict) -> dict:
    """計算完整的台灣總經指標（三位大師需要的所有指標）
    
    Args:
        metrics: 從 extract_ndc_history_metrics 取得的單一月份資料
    
    Returns:
        包含所有衍生指標的完整字典
    """
    result = {
        # 原始指標直接帶入
        **metrics,
    }
    
    # ===== 愛榭克指標 =====
    
    # 工業生產趨勢
    if metrics.get("industrial_production") and metrics.get("industrial_production_prev"):
        ip_change = metrics["industrial_production"] - metrics["industrial_production_prev"]
        result["industrial_production_change"] = ip_change
        result["industrial_production_trend"] = (
            "improving" if ip_change > 0.5 else 
            ("deteriorating" if ip_change < -0.5 else "stable")
        )
    else:
        result["industrial_production_change"] = None
        result["industrial_production_trend"] = "stable"
    
    # 加班工時趨勢（代表企業急單/趕工）
    if metrics.get("overtime_hours") and metrics.get("overtime_hours_prev"):
        ot_change = metrics["overtime_hours"] - metrics["overtime_hours_prev"]
        result["overtime_hours_change"] = ot_change
        result["overtime_trend"] = (
            "rising" if ot_change > 0.5 else 
            ("falling" if ot_change < -0.5 else "stable")
        )
    else:
        result["overtime_hours_change"] = None
        result["overtime_trend"] = "stable"
    
    # 機械進口趨勢（代表民間投資/資本支出）
    if metrics.get("machinery_import") and metrics.get("machinery_import_prev"):
        mi_yoy = (metrics["machinery_import"] - metrics["machinery_import_prev"]) / metrics["machinery_import_prev"] * 100
        result["machinery_import_yoy"] = mi_yoy
        result["investment_trend"] = (
            "expanding" if mi_yoy > 2 else 
            ("contracting" if mi_yoy < -2 else "stable")
        )
    else:
        result["machinery_import_yoy"] = None
        result["investment_trend"] = "stable"
    
    # 零售/消費趨勢
    if metrics.get("retail_sales") and metrics.get("retail_sales_prev"):
        retail_change = metrics["retail_sales"] - metrics["retail_sales_prev"]
        result["retail_sales_change"] = retail_change
        result["consumption_trend"] = (
            "expanding" if retail_change > 0 else "contracting"
        )
    else:
        result["retail_sales_change"] = None
        result["consumption_trend"] = "stable"
    
    # 庫存趨勢
    if metrics.get("inventory") and metrics.get("inventory_prev"):
        inv_change = metrics["inventory"] - metrics["inventory_prev"]
        result["inventory_change"] = inv_change
        result["inventory_trend"] = (
            "accumulating" if inv_change > 0 else "clearing"
        )
    else:
        result["inventory_change"] = None
        result["inventory_trend"] = "stable"
    
    # 庫存/銷售比
    inv_sales = compute_inventory_to_sales_ratio(
        metrics.get("inventory"),
        metrics.get("inventory_prev"),
        metrics.get("retail_sales"),
        metrics.get("retail_sales_prev"),
    )
    result["inventory_sales_ratio"] = inv_sales
    
    # 出口年增率
    if metrics.get("export_value") and metrics.get("export_value_year_ago"):
        exports_yoy = (metrics["export_value"] - metrics["export_value_year_ago"]) / metrics["export_value_year_ago"] * 100
        result["exports_yoy"] = exports_yoy
        result["export_trend"] = (
            "expanding" if exports_yoy > 2 else 
            ("contracting" if exports_yoy < -2 else "stable")
        )
    else:
        result["exports_yoy"] = None
        result["export_trend"] = "stable"
    
    # ===== 浦上邦雄指標 =====
    
    # 銀行放款利率趨勢
    if metrics.get("bank_lending_rate") and metrics.get("bank_lending_rate_prev"):
        rate_change = metrics["bank_lending_rate"] - metrics["bank_lending_rate_prev"]
        result["bank_lending_rate_change"] = rate_change
        result["rate_trend"] = (
            "rising" if rate_change > 0.01 else 
            ("falling" if rate_change < -0.01 else "stable")
        )
    else:
        result["bank_lending_rate_change"] = None
        result["rate_trend"] = "stable"
    
    # 信用擴張趨勢
    if metrics.get("total_credit") and metrics.get("total_credit_prev"):
        credit_change = metrics["total_credit"] - metrics["total_credit_prev"]
        result["credit_change"] = credit_change
        result["credit_trend"] = (
            "expanding" if credit_change > 0 else "contracting"
        )
    else:
        result["credit_change"] = None
        result["credit_trend"] = "stable"
    
    # M1B 趨勢
    if metrics.get("m1b") and metrics.get("m1b_prev"):
        m1b_change = metrics["m1b"] - metrics["m1b_prev"]
        result["m1b_change"] = m1b_change
        result["money_supply_trend"] = (
            "expanding" if m1b_change > 0 else "contracting"
        )
    else:
        result["m1b_change"] = None
        result["money_supply_trend"] = "stable"
    
    # 股價指數趨勢
    if metrics.get("stock_index") and metrics.get("stock_index_prev"):
        stock_yoy = (metrics["stock_index"] - metrics["stock_index_prev"]) / metrics["stock_index_prev"] * 100
        result["stock_index_yoy"] = stock_yoy
        result["stock_trend"] = (
            "bullish" if stock_yoy > 5 else 
            ("bearish" if stock_yoy < -5 else "neutral")
        )
    else:
        result["stock_index_yoy"] = None
        result["stock_trend"] = "neutral"
    
    # 製造業銷售趨勢
    if metrics.get("manufacturing_sales") and metrics.get("manufacturing_sales_prev"):
        mfg_change = metrics["manufacturing_sales"] - metrics["manufacturing_sales_prev"]
        result["manufacturing_sales_change"] = mfg_change
        result["mfg_sales_trend"] = (
            "improving" if mfg_change > 0 else "deteriorating"
        )
    else:
        result["manufacturing_sales_change"] = None
        result["mfg_sales_trend"] = "stable"
    
    # ===== 馬克斯指標 =====
    
    # 信用/庫存比（風險指標）
    if metrics.get("total_credit") and metrics.get("inventory"):
        credit_inventory_ratio = metrics["total_credit"] / metrics["inventory"] if metrics["inventory"] else None
        result["credit_inventory_ratio"] = credit_inventory_ratio
    else:
        result["credit_inventory_ratio"] = None
    
    return result
