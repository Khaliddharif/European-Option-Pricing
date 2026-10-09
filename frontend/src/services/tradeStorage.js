
const STORAGE_KEY = "european-option-pricing:trade-journal:v1";

export function loadTrades() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];

    const trades = JSON.parse(raw);
    return Array.isArray(trades) ? trades : [];
  } catch (error) {
    console.warn("Could not load the saved trade journal.", error);
    return [];
  }
}

export function saveTrades(trades) {
  try {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(trades)
    );
  } catch (error) {
    console.warn("Could not save the trade journal.", error);
  }
}
