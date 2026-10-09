
import { useEffect, useRef, useState } from "react";
import "./App.css";
import { loadTrades, saveTrades } from "./services/tradeStorage";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const fmt = (value, decimals = 2) =>
  value === null || value === undefined || !Number.isFinite(Number(value))
    ? "—"
    : Number(value).toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });

const money = (value) => fmt(value, 2);

const percent = (value) =>
  value === null || value === undefined || !Number.isFinite(Number(value))
    ? "—"
    : `${fmt(Number(value) * 100, 1)}%`;

const errorText = (error) =>
  error instanceof Error ? error.message : "An unexpected error occurred.";

function tradePnl(trade) {
  const current =
    trade.position.asset_type === "Future"
      ? Number(trade.spot)
      : Number(trade.analytics?.price);

  if (!Number.isFinite(current)) return null;

  const entry = Number(trade.position.entry_price);
  const quantity = Number(trade.position.quantity);
  const direction = trade.position.position === "Short" ? -1 : 1;

  const multiplier = trade.position.asset_type === "Future" ? Number(trade.position.contract_multiplier ?? 1) : 1;
  return (current - entry) * quantity * direction * multiplier;
}

function HelpTip({ text }) {
  // Use the browser's native title tooltip only. A custom tooltip plus title
  // caused duplicate messages and could cover the delete dialog.
  return (
    <button
      type="button"
      className="help-tip"
      tabIndex={-1}
      aria-label={`Help: ${text}`}
      title={text}
    >
      ?
    </button>
  );
}

function Metric({ label, value, hint, help }) {
  return (
    <div className="metric">
      <span className="metric-label">{label}{help && <HelpTip text={help} />}</span>
      <strong className="metric-value">{value}</strong>
      {hint && <span className="metric-hint">{hint}</span>}
    </div>
  );
}

/*
 * Match the Excel Matrix sheet:
 * Spot Variation: -20.0%, -10.0%, 0.0%, 10.0%, 20.0%
 * IV Variation:   -10.0%, -5.0%, 0.0%, 5.0%, 10.0%
 *
 * The backend supplies absolute scenario values. Convert them to
 * variations relative to the base spot or base implied volatility.
 * Positive labels intentionally do not include a leading plus sign,
 * matching the Excel headings.
 */
function scenarioLabels(scenarios, base, type) {
  if (!Array.isArray(scenarios)) return [];

  return scenarios.map((value) => {
    let variation;

    if (type === "volatility") {
      variation = (Number(value) - Number(base)) * 100;
    } else {
      if (!Number(base)) return fmt(value);
      variation = (Number(value) / Number(base) - 1) * 100;
    }

    const rounded = Math.round(variation);
    const normalized = Object.is(rounded, -0) ? 0 : rounded;

    return `${normalized}%`;
  });
}

function SensitivityTable({ title, subtitle, data, labels }) {
  const rows = [
    { label: "Delta", values: data?.delta, decimals: 4 },
    { label: "Gamma", values: data?.gamma, decimals: 4 },
    { label: "Theta", values: data?.theta, decimals: 4 },
    { label: "Vega", values: data?.vega, decimals: 4 },
    { label: "P&L", values: data?.pnl, decimals: 2 },
  ];

  return (
    <section className="card sensitivity-card">
      <div className="card-header">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
        <span className="badge">5 Scenarios</span>
      </div>

      {!data ? (
        <div className="placeholder">
          <p>Sensitivity analysis is available for European options.</p>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="sensitivity-table">
            <thead>
              <tr>
                <th>Metric</th>
                {labels.map((label, index) => (
                  <th className="scenario-label" key={`${label}-${index}`}>{label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.label}>
                  <td>{row.label}<HelpTip text={{ Delta: "Sensitivity to a one-unit underlying price move.", Gamma: "Change in delta as the underlying moves.", Theta: "Time decay estimate per day.", Vega: "Sensitivity to volatility changes.", "P&L": "Indicative profit or loss in this scenario." }[row.label]} /></td>
                  {(row.values ?? []).map((value, index) => {
                    const isPnl = row.label === "P&L";
                    const numericValue = Number(value);
                    const className =
                      isPnl && numericValue > 0
                        ? "positive-value"
                        : isPnl && numericValue < 0
                          ? "negative-value"
                          : "";

                    return (
                      <td
                        className={className}
                        key={`${row.label}-${index}`}
                      >
                        {fmt(value, row.decimals)}
                      </td>
                    );
                  })}

                  {Array.from({
                    length: Math.max(
                      0,
                      labels.length - (row.values ?? []).length
                    ),
                  }).map((_, index) => (
                    <td key={`empty-${row.label}-${index}`}>—</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function DeleteConfirmation({ trade, onCancel, onConfirm, deleting }) {
  const cancelRef = useRef(null);

  useEffect(() => {
    if (!trade) return;

    cancelRef.current?.focus();

    const handleKeyDown = (event) => {
      if (event.key === "Escape" && !deleting) onCancel();
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [trade, onCancel, deleting]);

  if (!trade) return null;

  const p = trade.position;

  return (
    <div
      className="modal-backdrop"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !deleting) onCancel();
      }}
    >
      <section
        className="confirmation-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="delete-title"
        aria-describedby="delete-description"
      >
        <div className="confirmation-icon" aria-hidden="true">
          !
        </div>

        <h2 className="confirmation-title" id="delete-title">
          Delete trade?
        </h2>

        <p className="confirmation-message" id="delete-description">
          Are you sure you want to delete this trade and its information from
          the journal? This action cannot be undone.
        </p>

        <div className="confirmation-details">
          <div className="confirmation-trade-id">
            <span>Trade ID:</span>
            <strong>#{trade.id}</strong>
          </div>

          <div className="confirmation-trade-description">
            <strong>
              {p.asset_type} · {p.position}
            </strong>
          </div>

          <div className="confirmation-detail-row">
            <span>Quantity <HelpTip text="Number of option units or futures contracts in the position." /></span>
            <strong>{fmt(p.quantity, 0)}</strong>
          </div>

          <div className="confirmation-detail-row">
            <span>Entry price <HelpTip text={p.asset_type === "Future" ? "The futures price when you opened the position. P&L compares the current futures price with this entry price." : "The option premium per unit you paid (Long) or received (Short) when opening the position. P&L compares the current model value with this entry premium."} /></span>
            <strong>{money(p.entry_price)}</strong>
          </div>

          {p.asset_type === "Future" && (
            <>
              <div className="confirmation-detail-row"><span>Contract multiplier <HelpTip text="Units represented by one futures contract; used to scale P&L and exposure." /></span><strong>{fmt(p.contract_multiplier ?? 1, 4)}</strong></div>
              <div className="confirmation-detail-row"><span>Expiry / delivery</span><strong>{p.expiry_month || "Not specified"}</strong></div>
              <div className="confirmation-detail-row"><span>Currency</span><strong>{p.currency || "EUR"}</strong></div>
              <div className="confirmation-detail-row"><span>Settlement</span><strong>{p.settlement_convention || "Daily mark-to-market"}</strong></div>
            </>
          )}
          {p.asset_type !== "Future" && (
            <>
              <div className="confirmation-detail-row">
                <span>Strike price <HelpTip text="The option exercise price used in the Black–Scholes valuation." /></span>
                <strong>{money(p.strike)}</strong>
              </div>

              <div className="confirmation-detail-row">
                <span>Implied volatility</span>
                <strong>{percent(p.volatility)}</strong>
              </div>

              <div className="confirmation-detail-row">
                <span>Time to maturity</span>
                <strong>{fmt(p.maturity, 3)} years</strong>
              </div>
            </>
          )}
        </div>

        <div className="confirmation-actions">
          <button
            ref={cancelRef}
            type="button"
            className="cancel-button"
            onClick={onCancel}
            disabled={deleting}
          >
            No — Cancel
          </button>

          <button
            type="button"
            className="confirm-delete-button"
            onClick={onConfirm}
            disabled={deleting}
          >
            {deleting ? "Deleting…" : "Yes — Delete"}
          </button>
        </div>
      </section>
    </div>
  );
}

const csvCell = (value) => {
  const text = value === null || value === undefined ? "" : String(value);
  return `"${text.replace(/"/g, '""')}"`;
};

function exportTradesCsv(trades) {
  const headers = [
    "Trade ID", "Instrument", "Side", "Quantity", "Entry Price", "Current Model Value / Futures Price",
    "Model P&L", "Spot / Futures Price", "Strike", "Volatility", "Maturity (years)",
    "Contract Multiplier", "Expiry / Delivery Month", "Currency", "Tick Size", "Tick Value",
    "Initial Margin / Contract", "Maintenance Margin / Contract", "Settlement Convention", "Created At"
  ];
  const rows = trades.map((trade) => {
    const p = trade.position;
    return [trade.id, p.asset_type, p.position, p.quantity, p.entry_price,
    p.asset_type === "Future" ? trade.spot : trade.analytics?.price,
    tradePnl(trade), trade.spot, p.strike, p.volatility, p.maturity,
    p.contract_multiplier, p.expiry_month, p.currency, p.tick_size, p.tick_value,
    p.initial_margin, p.maintenance_margin, p.settlement_convention, trade.createdAt];
  });
  const csv = [headers, ...rows].map((row) => row.map(csvCell).join(",")).join("\r\n");
  const blob = new Blob(["\uFEFF", csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `trade-journal-${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function App() {
  const [assetType, setAssetType] = useState("Call");
  const [position, setPosition] = useState("Long");
  const [spot, setSpot] = useState("");
  const [strike, setStrike] = useState("");
  const [volatility, setVolatility] = useState("");
  const [rate, setRate] = useState("");
  const [dividendYield, setDividendYield] = useState("");
  const [maturity, setMaturity] = useState("");
  const [entryPrice, setEntryPrice] = useState("");
  const [quantity, setQuantity] = useState("");
  const [contractMultiplier, setContractMultiplier] = useState("");
  const [expiryMonth, setExpiryMonth] = useState("");
  const [currency, setCurrency] = useState("EUR");
  const [tickSize, setTickSize] = useState("");
  const [tickValue, setTickValue] = useState("");
  const [initialMargin, setInitialMargin] = useState("");
  const [maintenanceMargin, setMaintenanceMargin] = useState("");
  const [settlementConvention, setSettlementConvention] = useState("Daily mark-to-market");

  const [trades, setTrades] = useState(() => loadTrades());
  const [results, setResults] = useState(null);
  const [sensitivity, setSensitivity] = useState(null);
  const [portfolioResults, setPortfolioResults] = useState(null);
  const [pendingDeleteTrade, setPendingDeleteTrade] = useState(null);
  const [loading, setLoading] = useState(false);
  const [deletingTradeId, setDeletingTradeId] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    saveTrades(trades);
  }, [trades]);

  const isOption = assetType === "Call" || assetType === "Put";

  async function requestJson(path, body) {
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      const detail = payload.detail;
      throw new Error(
        detail
          ? typeof detail === "string"
            ? detail
            : JSON.stringify(detail)
          : `Request failed (${response.status})`
      );
    }

    return payload;
  }

  // Keep the backend's required "asset" field in the portfolio request.
  function makePortfolioPayload(tradeList) {
    return {
      positions: tradeList.map(({ position: p }) => ({
        asset: p.asset_type,
        position: p.position,
        quantity: Number(p.quantity),
        entry_price: Number(p.entry_price),
        maturity: p.maturity == null ? null : Number(p.maturity),
        strike: p.strike == null ? null : Number(p.strike),
        volatility: p.volatility == null ? null : Number(p.volatility),
        contract_multiplier: Number(p.contract_multiplier ?? 1),
        expiry_month: p.expiry_month || null,
        currency: p.currency || "EUR",
        tick_size: p.tick_size == null || p.tick_size === "" ? null : Number(p.tick_size),
        tick_value: p.tick_value == null || p.tick_value === "" ? null : Number(p.tick_value),
        initial_margin: Number(p.initial_margin ?? 0),
        maintenance_margin: Number(p.maintenance_margin ?? 0),
        settlement_convention: p.settlement_convention || "Daily mark-to-market",
      })),
      spot: Number(spot),
      rate: Number(rate) / 100,
      dividend_yield: Number(dividendYield) / 100,
    };
  }

  async function handleCompute(event) {
    event.preventDefault();
    setError("");

    const s = Number(spot);
    const k = Number(strike);
    const v = Number(volatility) / 100;
    const r = Number(rate) / 100;
    const q = Number(dividendYield) / 100;
    const t = Number(maturity);
    const entry = Number(entryPrice);
    const qty = Number(quantity);
    const multiplier = Number(contractMultiplier);
    const initialMarginValue = Number(initialMargin);
    const maintenanceMarginValue = Number(maintenanceMargin);
    const tickSizeValue = tickSize === "" ? null : Number(tickSize);
    const tickValueValue = tickValue === "" ? null : Number(tickValue);

    if (
      !Number.isFinite(s) ||
      s <= 0 ||
      !Number.isFinite(entry) ||
      entry < 0 ||
      !Number.isFinite(qty) ||
      qty <= 0 ||
      !Number.isFinite(r) ||
      !Number.isFinite(q)
    ) {
      setError("Enter a valid current price, entry price, quantity, and rate values.");
      return;
    }

    if (
      isOption &&
      (!Number.isFinite(k) ||
        k <= 0 ||
        !Number.isFinite(v) ||
        v <= 0 ||
        !Number.isFinite(t) ||
        t <= 0)
    ) {
      setError("Options require a positive strike, volatility, and maturity.");
      return;
    }

    if (
      assetType === "Future" &&
      (!Number.isFinite(multiplier) || multiplier <= 0 ||
        !Number.isFinite(initialMarginValue) || initialMarginValue < 0 ||
        !Number.isFinite(maintenanceMarginValue) || maintenanceMarginValue < 0 ||
        (tickSizeValue !== null && (!Number.isFinite(tickSizeValue) || tickSizeValue <= 0)) ||
        (tickValueValue !== null && (!Number.isFinite(tickValueValue) || tickValueValue <= 0)) ||
        (initialMarginValue > 0 && maintenanceMarginValue > initialMarginValue))
    ) {
      setError("For futures, check the contract multiplier, tick values, and margin inputs. Maintenance margin must not exceed a positive initial margin.");
      return;
    }

    setLoading(true);

    try {
      const positionData = {
        asset_type: assetType,
        position,
        entry_price: entry,
        quantity: qty,
        strike: isOption ? k : null,
        volatility: isOption ? v : null,
        maturity: isOption ? t : null,
        contract_multiplier: assetType === "Future" ? multiplier : 1,
        expiry_month: assetType === "Future" ? expiryMonth.trim() || null : null,
        currency: assetType === "Future" ? currency.toUpperCase() : "EUR",
        tick_size: assetType === "Future" ? tickSizeValue : null,
        tick_value: assetType === "Future" ? tickValueValue : null,
        initial_margin: assetType === "Future" ? initialMarginValue : 0,
        maintenance_margin: assetType === "Future" ? maintenanceMarginValue : 0,
        settlement_convention: assetType === "Future" ? settlementConvention : "Daily mark-to-market",
      };

      let pricingData = null;
      let sensitivityData = null;

      if (isOption) {
        pricingData = await requestJson("/pricing", {
          option_type: assetType,
          spot: s,
          strike: k,
          volatility: v,
          rate: r,
          maturity: t,
          dividend_yield: q,
        });

        sensitivityData = await requestJson("/sensitivity", {
          option_type: assetType,
          spot: s,
          strike: k,
          volatility: v,
          rate: r,
          maturity: t,
          dividend_yield: q,
          entry_price: entry,
          position,
          quantity: qty,
        });
      }

      const newTrade = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        position: positionData,
        analytics: pricingData,
        spot: s,
        createdAt: new Date().toISOString(),
      };

      const updatedTrades = [...trades, newTrade];
      const updatedPortfolio = await requestJson(
        "/portfolio",
        makePortfolioPayload(updatedTrades)
      );

      setTrades(updatedTrades);
      setResults(pricingData);
      setSensitivity(sensitivityData);
      setPortfolioResults(updatedPortfolio);
    } catch (requestError) {
      setError(errorText(requestError));
    } finally {
      setLoading(false);
    }
  }



  async function handleConfirmDelete() {
    if (!pendingDeleteTrade) return;

    const tradeToDelete = pendingDeleteTrade;
    const updatedTrades = trades.filter(
      (trade) => trade.id !== tradeToDelete.id
    );

    setDeletingTradeId(tradeToDelete.id);
    setError("");

    // Delete locally first; the useEffect saves the journal.
    setTrades(updatedTrades);
    setPortfolioResults(null);
    setPendingDeleteTrade(null);

    const validSpot = Number(spot) > 0 && Number.isFinite(Number(spot));

    if (updatedTrades.length === 0 || !validSpot) {
      setDeletingTradeId(null);
      return;
    }

    try {
      const updatedPortfolio = await requestJson(
        "/portfolio",
        makePortfolioPayload(updatedTrades)
      );
      setPortfolioResults(updatedPortfolio);
    } catch (requestError) {
      setError(
        `Trade deleted, but the portfolio summary could not be refreshed. ${errorText(requestError)}`
      );
    } finally {
      setDeletingTradeId(null);
    }
  }



  const spotLabels = scenarioLabels(
    sensitivity?.spot_scenarios,
    Number(spot),
    "spot"
  );

  const volLabels = scenarioLabels(
    sensitivity?.volatility_scenarios,
    Number(volatility) / 100,
    "volatility"
  );

  const currentPnl = results
    ? tradePnl({
      position: {
        asset_type: assetType,
        position,
        entry_price: Number(entryPrice),
        quantity: Number(quantity),
      },
      analytics: results,
      spot: Number(spot),
    })
    : null;

  const pnlClass =
    currentPnl > 0
      ? "positive-value"
      : currentPnl < 0
        ? "negative-value"
        : "neutral-value";

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="app-eyebrow">TRADING WORKSPACE</div>
          <h1>European Option Pricing - Risk &amp; Portfolio Analytics</h1>
          <p>Pricing · Greeks · Scenario Analysis · Portfolio Monitoring</p>
          <span className="coming-soon-badge"><span className="coming-soon-dot" /> Live market data · Coming soon</span>
        </div>

        <span className="status-indicator">
          <span className="status-dot" />
          Analytics workspace
        </span>
      </header>

      <main className="dashboard">
        <section className="card input-card">
          <div className="card-header">
            <div>
              <h2>Trade Inputs</h2>
              <p>Configure a trade and calculate its risk profile.</p>
            </div>
          </div>

          <form onSubmit={handleCompute}>
            <div className="form-grid">
              <label>
                <span>Instrument <HelpTip text="Choose a European Call, European Put, or a simplified linear futures position." /></span>
                <select
                  value={assetType}
                  onChange={(event) => setAssetType(event.target.value)}
                >
                  <option value="Call">Call</option>
                  <option value="Put">Put</option>
                  <option value="Future">Future</option>
                </select>
              </label>

              <label>
                <span>Position <HelpTip text="Long benefits from a rise in value; Short benefits from a fall in value, all else equal." /></span>
                <select
                  value={position}
                  onChange={(event) => setPosition(event.target.value)}
                >
                  <option value="Long">Long</option>
                  <option value="Short">Short</option>
                </select>
              </label>

              <label>
                <span>{assetType === "Future" ? "Current futures price" : "Current spot price"} <HelpTip text={assetType === "Future" ? "The manually entered current price of the futures contract, used to estimate its current value and P&L. No live market data is connected." : "The manually entered current market price of the underlying asset, used by the option model to calculate theoretical value and Greeks. This is not the price you paid for the option."} /></span>
                <input
                  type="number"
                  min="0.000001"
                  step="any"
                  value={spot}
                  onChange={(event) => setSpot(event.target.value)}
                  required
                />
              </label>

              {isOption && (
                <label>
                  <span>Strike price <HelpTip text="The option exercise price used in the Black–Scholes valuation." /></span>
                  <input
                    type="number"
                    min="0.000001"
                    step="any"
                    value={strike}
                    onChange={(event) => setStrike(event.target.value)}
                    required
                  />
                </label>
              )}

              <label>
                <span>Entry price <HelpTip text={assetType === "Future" ? "The futures price when you opened the position. P&L compares the current futures price with this entry price." : "The option premium per unit you paid (Long) or received (Short) when opening the position. P&L compares the current model value with this entry premium."} /></span>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={entryPrice}
                  onChange={(event) => setEntryPrice(event.target.value)}
                  required
                />
              </label>

              <label>
                <span>Quantity <HelpTip text="Number of option units or futures contracts in the position." /></span>
                <input
                  type="number"
                  min="0.000001"
                  step="any"
                  value={quantity}
                  onChange={(event) => setQuantity(event.target.value)}
                  required
                />
              </label>

              {isOption && (
                <label>
                  <span>Implied volatility (%) <HelpTip text="Annualized volatility assumption entered as a percentage; 20 means 20%." /></span>
                  <input
                    type="number"
                    min="0.000001"
                    step="any"
                    value={volatility}
                    onChange={(event) => setVolatility(event.target.value)}
                    required
                  />
                </label>
              )}

              {isOption && <label>
                <span>Risk-free rate (%) <HelpTip text="Annualized risk-free interest rate assumption, entered as a percentage." /></span>
                <input
                  type="number"
                  step="any"
                  value={rate}
                  onChange={(event) => setRate(event.target.value)}
                  required
                />
              </label>}

              {isOption && <label>
                <span>Dividend yield (%) <HelpTip text="Annualized continuous dividend yield assumption, entered as a percentage." /></span>
                <input
                  type="number"
                  step="any"
                  value={dividendYield}
                  onChange={(event) => setDividendYield(event.target.value)}
                  required
                />
              </label>}

              {isOption && (
                <label>
                  <span>Time to maturity (years) <HelpTip text="Time remaining until option maturity, represented in years." /></span>
                  <input
                    type="number"
                    min="0.000001"
                    step="any"
                    value={maturity}
                    onChange={(event) => setMaturity(event.target.value)}
                    required
                  />
                </label>
              )}

              {assetType === "Future" && <>
                <label>
                  <span>Contract multiplier <HelpTip text="Units represented by one futures contract; used to scale P&L and exposure." /></span>
                  <input type="number" min="0.000001" step="any" value={contractMultiplier} onChange={(event) => setContractMultiplier(event.target.value)} required />
                </label>
                <label>
                  <span>Expiry / delivery month <HelpTip text="Contract expiry or delivery month as defined by the relevant exchange specification." /></span>
                  <input type="month" value={expiryMonth} onChange={(event) => setExpiryMonth(event.target.value)} />
                </label>
                <label>
                  <span>Currency (3-letter code) <HelpTip text="Currency in which this contract is quoted or settled. Informational only in this version." /></span>
                  <input type="text" minLength="3" maxLength="3" pattern="[A-Za-z]{3}" value={currency} onChange={(event) => setCurrency(event.target.value.toUpperCase())} required />
                </label>
                <label>
                  <span>Tick size (optional) <HelpTip text="Minimum permitted price increment for the selected contract." /></span>
                  <input type="number" min="0.000001" step="any" value={tickSize} onChange={(event) => setTickSize(event.target.value)} />
                </label>
                <label>
                  <span>Tick value per contract (optional) <HelpTip text="Monetary value of one tick for one contract, according to the contract specification." /></span>
                  <input type="number" min="0.000001" step="any" value={tickValue} onChange={(event) => setTickValue(event.target.value)} />
                </label>
                <label>
                  <span>Initial margin per contract <HelpTip text="Manual per-contract margin estimate used to summarize portfolio margin." /></span>
                  <input type="number" min="0" step="any" value={initialMargin} onChange={(event) => setInitialMargin(event.target.value)} required />
                </label>
                <label>
                  <span>Maintenance margin per contract <HelpTip text="Manual per-contract maintenance margin estimate; verify current broker/exchange rules." /></span>
                  <input type="number" min="0" step="any" value={maintenanceMargin} onChange={(event) => setMaintenanceMargin(event.target.value)} required />
                </label>
                <label>
                  <span>Settlement convention <HelpTip text="Describes the selected settlement convention; this app does not simulate delivery or daily settlement cash flows." /></span>
                  <select value={settlementConvention} onChange={(event) => setSettlementConvention(event.target.value)}>
                    <option value="Daily mark-to-market">Daily mark-to-market</option>
                    <option value="Cash">Cash settlement</option>
                    <option value="Physical">Physical delivery</option>
                    <option value="Other">Other / verify contract rules</option>
                  </select>
                </label>
              </>}


            </div>

            {error && (
              <div className="error-message" role="alert">
                {error}
              </div>
            )}

            <button
              className="calculate-button"
              type="submit"
              disabled={loading}
            >
              {loading ? "Calculating…" : "Calculate & Add Trade"}
            </button>
          </form>
        </section>

        <section className="card results-card">
          <div className="card-header">
            <div>
              <h2>Instrument Analytics</h2>
              <p>Model valuation and risk measures for the current calculation.</p>
            </div>
            <span className="badge">Black–Scholes</span>
          </div>

          {!results ? (
            <div className="placeholder">
              <p>
                {assetType === "Future"
                  ? "Option valuation and Greeks are not applicable to futures."
                  : "Calculate an option trade to view its theoretical valuation and Greeks."}
              </p>
            </div>
          ) : (
            <>
              <div className="metrics-grid">
                <Metric
                  label="Theoretical value"
                  value={money(results.price)}
                  hint="Model price per unit"
                  help="Black–Scholes theoretical price per option unit using the entered underlying price, strike, volatility, rate, dividend yield, and maturity."
                />
                <Metric label="Delta" value={fmt(results.delta, 4)} help="Approximate change in option value for a one-unit change in the underlying price." />
                <Metric label="Gamma" value={fmt(results.gamma, 4)} help="How quickly option delta changes as the underlying price moves." />
                <Metric label="Theta / day" value={fmt(results.theta, 4)} help="Estimated option value change for one day passing, with other model inputs held constant." />
                <Metric label="Vega" value={fmt(results.vega, 4)} help="Approximate option value change for a 1.00 change in volatility (100 percentage points); the portfolio summary displays per-volatility-point context." />
                <Metric label="Rho" value={fmt(results.rho, 4)} help="Approximate option value sensitivity to a 1.00 change in the risk-free rate." />
              </div>

              <div className="trade-summary">
                <div className="trade-summary-header">
                  <h3>Current Trade Summary</h3>
                  <span className={`trade-direction ${position.toLowerCase()}`}>
                    {position}
                  </span>
                </div>

                <div className="trade-summary-grid">
                  <Metric
                    label="Entry price"
                    value={money(Number(entryPrice))}
                    help="Price recorded when entering the current trade; used as the reference for indicative P&L."
                  />
                  <Metric
                    label="Quantity"
                    value={fmt(Number(quantity), 0)}
                    help="Number of option units or futures contracts entered for this trade."
                  />
                  <Metric
                    label="Model-based P&L"
                    value={money(currentPnl)}
                    hint="Excludes fees and slippage"
                    help="Indicative P&L versus entry price; futures include the entered contract multiplier. Fees, financing, and settlement cash flows are excluded."
                  />
                </div>

                <p className={`trade-pnl ${pnlClass}`}>
                  Model-based P&amp;L: {money(currentPnl)}
                </p>
              </div>
            </>
          )}
        </section>

        <SensitivityTable
          title="Spot Variation"
          subtitle="Underlying price variation · Implied volatility held constant"
          data={sensitivity?.spot_sensitivity}
          labels={spotLabels}
        />

        <SensitivityTable
          title="Implied Volatility Variation"
          subtitle="Implied volatility variation · Underlying price held constant"
          data={sensitivity?.volatility_sensitivity}
          labels={volLabels}
        />

        <section className="card portfolio-risk-card">
          <div className="card-header">
            <div>
              <h2>Portfolio Summary</h2>
              <p>Overview of the trades currently held in this session.</p>
            </div>
            <span className="badge">{trades.length} Trades</span>
          </div>

          {trades.length === 0 ? (
            <div className="placeholder">
              <p>Add a trade to start building your portfolio.</p>
            </div>
          ) : (
            <>
              <div className="metrics-grid">
                <Metric label="Open trades" value={trades.length} help="Number of trades currently recorded in this session journal." />
                <Metric
                  label="Long trades"
                  help="Number of trades marked Long in the current session."
                  value={
                    trades.filter((trade) => trade.position.position === "Long")
                      .length
                  }
                />
                <Metric
                  label="Short trades"
                  help="Number of trades marked Short in the current session."
                  value={
                    trades.filter((trade) => trade.position.position === "Short")
                      .length
                  }
                />
                <Metric
                  label="Options"
                  help="Count of Call and Put positions currently in the journal."
                  value={
                    trades.filter(
                      (trade) => trade.position.asset_type !== "Future"
                    ).length
                  }
                />
                <Metric
                  label="Futures"
                  help="Count of futures positions currently in the journal."
                  value={
                    trades.filter(
                      (trade) => trade.position.asset_type === "Future"
                    ).length
                  }
                />
              </div>

              {portfolioResults && (
                <>
                  <div className="portfolio-api-summary">
                    <Metric
                      label="Portfolio P&L"
                      value={money(portfolioResults.pnl)}
                      hint="Signed mark-to-model P&L versus entry prices"
                      help="Sum of each position's model value minus entry price, adjusted for side, quantity, and futures multiplier. Excludes fees and cash settlement flows."
                    />
                    <Metric
                      label="Signed market value"
                      value={money(portfolioResults.market_value)}
                      hint="Long positions positive; short positions negative"
                      help="The modelled exposure represented by positions, signed positive for long and negative for short. It is not necessarily the cash paid to open a futures position."
                    />
                    <Metric
                      label="Estimated Initial Margin"
                      value={money(portfolioResults.initial_margin ?? 0)}
                      hint="Sum of user-entered per-contract estimates"
                      help="Quantity multiplied by the initial margin you entered per contract. This is a manual estimate, not an exchange or broker quote."
                    />
                    <Metric
                      label="Estimated Maintenance Margin"
                      value={money(portfolioResults.maintenance_margin ?? 0)}
                      hint="Not live exchange margin requirements"
                      help="Quantity multiplied by the maintenance margin you entered per contract. Verify the applicable contract and broker requirements separately."
                    />
                    <Metric
                      label="Portfolio Delta"
                      value={fmt(portfolioResults.delta, 4)}
                      help="Approximate change in portfolio value for a one-unit move in the underlying, under the model assumptions. Futures delta includes the contract multiplier."
                    />
                    <Metric
                      label="Portfolio Gamma"
                      value={fmt(portfolioResults.gamma, 4)}
                      help="Rate of change of delta for a one-unit move in the underlying. The simplified futures model has zero gamma."
                    />
                    <Metric
                      label="Portfolio Theta / day"
                      value={fmt(portfolioResults.theta, 4)}
                      help="Model-estimated value change from one day less to expiry, expressed per day. It is not calculated for futures in this app."
                    />
                    <Metric
                      label="Portfolio Vega / 1 vol pt"
                      value={fmt(portfolioResults.vega, 4)}
                      hint="Change for a 1 percentage-point volatility move"
                      help="Approximate option value change if volatility moves by one percentage point (for example, 20% to 21%). Futures have zero vega in this simplified model."
                    />
                  </div>
                </>
              )}
            </>
          )}
        </section>

        <section className="card journal-card">
          <div className="card-header">
            <div>
              <h2>Trade Journal</h2>
              <p>Review session trades and remove individual records safely.</p>
            </div>

            {trades.length > 0 && (
              <div className="journal-actions">
                <button className="secondary-button" type="button" onClick={() => exportTradesCsv(trades)}>
                  Export CSV
                </button>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => {
                    setTrades([]);
                    setPortfolioResults(null);
                    setError("");
                  }}
                >
                  Clear Journal
                </button>
              </div>
            )}
          </div>

          {trades.length === 0 ? (
            <div className="placeholder">
              <p>Your trade journal is empty.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="trader-table portfolio-table">
                <thead>
                  <tr>
                    <th>Trade ID</th>
                    <th>Instrument</th>
                    <th>Side</th>
                    <th>Quantity</th>
                    <th>Entry Price</th>
                    <th>Model Value / Spot</th>
                    <th>Model P&amp;L</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>
                  {trades.map((trade) => {
                    const p = trade.position;
                    const pnl = tradePnl(trade);
                    const pnlValueClass =
                      pnl > 0
                        ? "positive-value"
                        : pnl < 0
                          ? "negative-value"
                          : "neutral-value";

                    return (
                      <tr key={trade.id}>
                        <td className="trade-id-cell">
                          <span title={trade.id}>#{trade.id}</span>
                        </td>
                        <td>{p.asset_type}</td>
                        <td>
                          <span
                            className={`journal-side ${p.position.toLowerCase()}`}
                          >
                            {p.position}
                          </span>
                        </td>
                        <td>{fmt(p.quantity, 0)}</td>
                        <td>{money(p.entry_price)}</td>
                        <td>
                          {money(
                            p.asset_type === "Future"
                              ? trade.spot
                              : trade.analytics?.price
                          )}
                        </td>
                        <td className={pnlValueClass}>{money(pnl)}</td>
                        <td>
                          <button
                            className="remove-button"
                            type="button"
                            onClick={() => setPendingDeleteTrade(trade)}
                            aria-label={`Delete trade ${trade.id}`}
                            disabled={deletingTradeId === trade.id}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          <p className="journal-disclaimer">
            Model P&amp;L is indicative and excludes fees, slippage, financing,
            and settlement cash flows. Futures multipliers are applied; margin is
            based only on the estimates entered for each contract.
          </p>
        </section>
      </main>

      <DeleteConfirmation
        trade={pendingDeleteTrade}
        onCancel={() => {
          if (!deletingTradeId) setPendingDeleteTrade(null);
        }}
        onConfirm={handleConfirmDelete}
        deleting={Boolean(deletingTradeId)}
      />
      <footer className="app-footer">
        <span>Developed by <strong>Khalid Dharif</strong></span>
        <span className="footer-roadmap">Live market data: coming soon, subject to provider permissions.</span>
        <a href="mailto:khalid.dharif@gmail.com">khalid.dharif@gmail.com</a>
        <a href="https://github.com/Khaliddharif" target="_blank" rel="noreferrer">GitHub: Khaliddharif</a>
      </footer>
    </div>
  );
}

export default App;
