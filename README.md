# 💰 Ultimate Budget Tracker

A comprehensive, feature-rich budgeting application built with Streamlit that helps you manage your personal finances with ease.

## 🌟 Features

### 📝 Transaction Management
- Add income and expenses with detailed categorization
- Tag transactions for easy filtering
- Add notes to transactions
- Quick filtering by type, category, and date range
- Easy deletion of transactions

### 📊 Interactive Dashboard
- Real-time financial overview
- Visual charts showing income vs expenses
- Spending trends over time
- Category breakdowns with pie charts
- Top spending categories analysis

### 🎯 Budget Planning
- Set monthly budgets by category
- Track budget vs actual spending
- Visual progress bars for each category
- Budget alerts for overspending
- Multi-month budget planning

### 💎 Savings Goals
- Create multiple savings goals
- Track progress with visual indicators
- Set deadlines and priorities
- Calculate required monthly savings
- Add contributions directly to goals

### 📈 Advanced Reports
- Monthly summary reports
- Category analysis
- Spending pattern insights
- Year-over-year comparisons
- Cash flow analysis
- Tax summary reports

### 🔄 Recurring Transactions
- Set up recurring income/expenses
- Daily, weekly, bi-weekly, monthly, and yearly frequencies
- Automatic transaction creation
- Pause/resume recurring transactions
- Track last processed dates

### ⚙️ Customizable Categories
- Custom expense categories
- Custom income categories
- Easy category management
- Emoji support for visual identification

### 📱 Financial Insights
- Personalized recommendations
- Spending trend analysis
- Financial health score
- Month-over-month comparisons
- Smart alerts and warnings

### 💾 Data Management
- Automatic local data persistence
- Export to CSV
- Import/restore functionality
- Clear data option with safety confirmation

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
streamlit run budget_app.py
```

3. **Access the app:**
   - The app will automatically open in your default browser
   - Or navigate to `http://localhost:8501`

## 📖 How to Use

### Getting Started

1. **Add Your First Transaction**
   - Go to the "Transactions" tab
   - Select Income or Expense
   - Choose a category
   - Enter the amount and description
   - Click "Add Transaction"

2. **Set Up Your Budget**
   - Navigate to the "Budget" tab
   - Enter budget amounts for each category
   - The app will track your spending against these budgets

3. **Create Savings Goals**
   - Go to the "Goals" tab
   - Enter goal details (name, target amount, deadline)
   - Add contributions as you save
   - Track your progress visually

4. **View Your Dashboard**
   - The "Dashboard" tab shows your financial overview
   - Customize date ranges to see different periods
   - View charts and graphs of your spending patterns

5. **Set Up Recurring Transactions**
   - Use the "Recurring" tab for regular income/expenses
   - The app will automatically add these transactions

### Tips for Best Results

- **Be Consistent**: Add transactions regularly for accurate tracking
- **Use Categories**: Proper categorization helps with analysis
- **Set Realistic Budgets**: Base budgets on your actual spending patterns
- **Review Monthly**: Check the Dashboard and Reports tabs monthly
- **Track Goals**: Update goal progress to stay motivated

## 📊 Features Breakdown

### Transaction Categories

**Default Expense Categories:**
- Housing, Transportation, Food & Dining, Groceries
- Utilities, Phone & Internet, Healthcare, Insurance
- Education, Entertainment, Clothing, Personal Care
- Gifts & Donations, Debt Payments, Savings, Shopping
- Pets, Maintenance, Other

**Default Income Categories:**
- Salary, Freelance, Investments, Gifts
- Bonus, Business, Other Income

### Budget Features
- Category-specific budgets
- Monthly budget planning
- Visual progress tracking
- Budget vs actual comparisons
- Overspending alerts

### Reports Available
1. **Monthly Summary**: Income, expenses, and savings by month
2. **Category Analysis**: Deep dive into spending categories
3. **Spending Patterns**: Day of week and day of month analysis
4. **Cash Flow Analysis**: Weekly cash flow tracking
5. **Tax Summary**: Annual income and deduction summary

### Financial Health Score
The app calculates a score (0-100) based on:
- Income vs Expenses (30 points)
- Savings Rate (25 points)
- Budget Adherence (25 points)
- Goal Progress (20 points)

## 💡 Advanced Features

### Custom Insights
- Automatic spending trend detection
- Personalized recommendations
- Category performance tracking
- Savings rate optimization suggestions

### Data Persistence
All data is stored locally in JSON files in the `budget_data` folder:
- `transactions.json`: All transactions
- `categories.json`: Custom categories
- `goals.json`: Savings goals
- `budgets.json`: Monthly budgets
- `recurring.json`: Recurring transactions

### Export & Backup
- Export all data to CSV
- Manual save/reload functionality
- Clear data with confirmation

## 🎨 User Interface

- **Clean, modern design** with emoji icons
- **Responsive layout** that works on different screen sizes
- **Interactive charts** using Plotly
- **Color-coded metrics** (green for positive, red for negative)
- **Progress bars** for goals and budgets
- **Tab-based navigation** for easy access

## ⚠️ Important Notes

- Data is stored locally on your machine
- No internet connection required after installation
- Regular backups recommended (use Export feature)
- The app runs entirely in your browser

## 🔧 Troubleshooting

**App won't start:**
- Ensure all dependencies are installed
- Check Python version (3.8+)
- Try reinstalling requirements

**Data not saving:**
- Check folder permissions
- Ensure `budget_data` folder exists
- Click "Save Data" button manually

**Charts not displaying:**
- Update Plotly: `pip install --upgrade plotly`
- Clear browser cache
- Restart the Streamlit server

## 📝 Future Enhancement Ideas

- Mobile app version
- Cloud sync capabilities
- Bill reminders
- Receipt photo uploads
- Multi-currency support
- Investment tracking
- Debt payoff calculator
- Net worth tracking

## 🤝 Contributing

Feel free to customize and extend this app for your needs!

## 📄 License

This project is open source and available for personal use.

---

**Happy Budgeting! 💰**
