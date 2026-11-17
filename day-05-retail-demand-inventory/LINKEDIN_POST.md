# LinkedIn draft — Day 5

📦 **Day 5 of my 30 Days, 30 Projects challenge: Retail Demand Forecasting & Inventory Replenishment**

Today I built a small end-to-end analytics workflow to compare demand forecasting baselines and translate forecasts into an inventory planning view.

What I worked on:
• Generated a reproducible synthetic dataset with 24 products and 8,760 daily product records
• Compared seasonal-naive, trailing-average, and weekday-average forecasting baselines
• Used October for per-product model selection, then evaluated on a November–December holdout
• Created rolling one-day-ahead forecasts, SQL sales summaries, and an illustrative replenishment plan

📊 **What the experiment showed:**
• Weekday-average baseline: **17.05% WAPE** on the holdout
• Per-product validation-selected baseline: **17.27% WAPE**, with **-9.44% bias** (under-forecasting)
• The sample reorder logic flagged **17 of 24 products**, for **2,778 units** in total

A useful reminder from this exercise: selecting a model on validation data does not guarantee it will beat every baseline on a later period. Holdout evaluation and bias checks matter.

The data and inventory snapshot are entirely synthetic. These results are for learning and demonstration; the reorder quantities are not operational purchasing advice.

Project and charts: https://github.com/Sanchay20Shukla/30days30projects/tree/main/day-05-retail-demand-inventory

#30Days30Projects #SQL #Python #DataAnalytics #Forecasting #RetailAnalytics #InventoryManagement
