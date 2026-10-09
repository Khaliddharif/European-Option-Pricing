UI refinement v3

Replace these files in your project:
- frontend/src/App.jsx with App_final_ui_v3.jsx
- frontend/src/App.css with App_final_ui_v3.css

Changes:
- Numeric trade inputs start empty rather than containing sample values. Instrument and position selectors remain preselected. Currency and settlement convention retain sensible defaults; optional futures contract details remain blank.
- Sensitivity scenario headings now show whole percentages (for example, -20%, -10%, 0%, 10%, 20%) and use stronger bold styling. Greek values remain unchanged.

After replacing the files, run `npm run build` from the frontend directory and manually test a Call, a Put, and a Future. Empty fields should prompt entry rather than silently using example numbers.
