# LinkedIn draft — Day 9

🧪 **Day 9 of my 30 Days, 30 Projects challenge: Product A/B Experiment Analysis**

Today I built an experiment analysis workflow to estimate conversion lift, check assignment balance, explore a device segment, and review a revenue-per-user guardrail.

What I worked on:
• Generated 24,000 synthetic users with a 1:1 control/treatment assignment
• Used SQL to summarize experiment results by variant, device, and day
• Calculated conversion-rate lift, a 95% confidence interval, a two-proportion z-test, and a sample-ratio check
• Compared revenue per assigned user with a Welch interval and test

📊 **In the seeded simulation:**
• Control conversion rate: **9.63%**; treatment: **11.23%**
• Estimated lift: **+1.61 percentage points** (95% CI: **+0.84 to +2.38 pp**; p = **0.000046**)
• Revenue per user was **8.0% higher** in treatment, but the interval included zero (p = **0.072**)
• The estimated mobile conversion lift was **+2.62 pp**; this subgroup view is exploratory

The key lesson: a primary metric can improve while a guardrail remains uncertain. Looking at both helps frame the decision.

Important context: all users and outcomes are synthetic, and the generator intentionally encodes treatment effects. The significance results demonstrate the workflow; they are not evidence about a real product or experiment.

Project and charts: https://github.com/Sanchay20Shukla/30days30projects/tree/main/day-09-product-ab-experiment-analysis

#30Days30Projects #SQL #Python #DataAnalytics #ABTesting #Experimentation #ProductAnalytics
