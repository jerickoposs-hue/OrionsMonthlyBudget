import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import calendar

# Page configuration
st.set_page_config(
    page_title="💰 Ultimate Budget Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }
</style>
""", unsafe_allow_html=True)

# Data storage path
DATA_DIR = Path("budget_data")
DATA_DIR.mkdir(exist_ok=True)
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
GOALS_FILE = DATA_DIR / "goals.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"
RECURRING_FILE = DATA_DIR / "recurring.json"

# Default categories
DEFAULT_EXPENSE_CATEGORIES = [
    "🏠 Housing", "🚗 Transportation", "🍔 Food & Dining", "🛒 Groceries",
    "⚡ Utilities", "📱 Phone & Internet", "🏥 Healthcare", "💊 Insurance",
    "🎓 Education", "🎬 Entertainment", "👕 Clothing", "💇 Personal Care",
    "🎁 Gifts & Donations", "💳 Debt Payments", "📦 Shopping",
    "🐕 Pets", "🔧 Maintenance", "🚙 Auto & Gas", "💡 Other Expenses"
]

DEFAULT_INCOME_CATEGORIES = [
    "💼 Salary", "💵 Freelance", "📈 Investments", "🎁 Gifts Received", 
    "💰 Bonus", "🏢 Business Income", "🏦 Interest", "💸 Refunds", "📊 Other Income"
]

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'categories' not in st.session_state:
    st.session_state.categories = {
        'expense': DEFAULT_EXPENSE_CATEGORIES,
        'income': DEFAULT_INCOME_CATEGORIES
    }
if 'goals' not in st.session_state:
    st.session_state.goals = []
if 'budgets' not in st.session_state:
    st.session_state.budgets = {}
if 'recurring' not in st.session_state:
    st.session_state.recurring = []

# Data persistence functions
def save_data():
    """Save all data to JSON files"""
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump(st.session_state.transactions, f)
    with open(CATEGORIES_FILE, 'w') as f:
        json.dump(st.session_state.categories, f)
    with open(GOALS_FILE, 'w') as f:
        json.dump(st.session_state.goals, f)
    with open(BUDGETS_FILE, 'w') as f:
        json.dump(st.session_state.budgets, f)
    with open(RECURRING_FILE, 'w') as f:
        json.dump(st.session_state.recurring, f)

def load_data():
    """Load all data from JSON files"""
    if TRANSACTIONS_FILE.exists():
        with open(TRANSACTIONS_FILE, 'r') as f:
            st.session_state.transactions = json.load(f)
    if CATEGORIES_FILE.exists():
        with open(CATEGORIES_FILE, 'r') as f:
            st.session_state.categories = json.load(f)
    if GOALS_FILE.exists():
        with open(GOALS_FILE, 'r') as f:
            st.session_state.goals = json.load(f)
    if BUDGETS_FILE.exists():
        with open(BUDGETS_FILE, 'r') as f:
            st.session_state.budgets = json.load(f)
    if RECURRING_FILE.exists():
        with open(RECURRING_FILE, 'r') as f:
            st.session_state.recurring = json.load(f)

# Load data on startup
load_data()

# Process recurring transactions
def process_recurring_transactions():
    """Add recurring transactions that are due"""
    today = datetime.now().date()
    for recurring in st.session_state.recurring:
        if recurring.get('active', True):
            last_processed = datetime.fromisoformat(recurring['last_processed']).date() if recurring.get('last_processed') else None
            start_date = datetime.fromisoformat(recurring['start_date']).date()
            
            if last_processed is None and today >= start_date:
                # First time processing
                add_transaction_from_recurring(recurring)
                recurring['last_processed'] = today.isoformat()
            elif last_processed:
                # Check if it's time for next occurrence
                frequency = recurring['frequency']
                if frequency == 'Daily' and (today - last_processed).days >= 1:
                    add_transaction_from_recurring(recurring)
                    recurring['last_processed'] = today.isoformat()
                elif frequency == 'Weekly' and (today - last_processed).days >= 7:
                    add_transaction_from_recurring(recurring)
                    recurring['last_processed'] = today.isoformat()
                elif frequency == 'Bi-weekly' and (today - last_processed).days >= 14:
                    add_transaction_from_recurring(recurring)
                    recurring['last_processed'] = today.isoformat()
                elif frequency == 'Monthly' and (today.month != last_processed.month or today.year != last_processed.year):
                    add_transaction_from_recurring(recurring)
                    recurring['last_processed'] = today.isoformat()
                elif frequency == 'Yearly' and (today.year != last_processed.year):
                    add_transaction_from_recurring(recurring)
                    recurring['last_processed'] = today.isoformat()

def add_transaction_from_recurring(recurring):
    """Add a transaction from a recurring template"""
    transaction = {
        'date': datetime.now().date().isoformat(),
        'type': recurring['type'],
        'category': recurring['category'],
        'amount': recurring['amount'],
        'description': recurring['description'] + " (Recurring)",
        'tags': recurring.get('tags', []),
        'recurring': True
    }
    st.session_state.transactions.append(transaction)

# Process recurring transactions
process_recurring_transactions()

# Helper functions
def get_transactions_df():
    """Convert transactions to DataFrame"""
    if not st.session_state.transactions:
        return pd.DataFrame()
    df = pd.DataFrame(st.session_state.transactions)
    df['date'] = pd.to_datetime(df['date'])
    return df

def filter_by_date_range(df, start_date, end_date):
    """Filter DataFrame by date range"""
    if df.empty:
        return df
    return df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]

def get_current_month_range():
    """Get start and end date of current month"""
    today = datetime.now().date()
    start = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end = today.replace(day=last_day)
    return start, end

def calculate_summary(df, transaction_type=None):
    """Calculate summary statistics"""
    if df.empty:
        return 0
    if transaction_type:
        df = df[df['type'] == transaction_type]
    return df['amount'].sum()

# Main app
st.title("💰 Ultimate Budget Tracker")
st.markdown("**Your complete personal finance management solution**")

# Sidebar
with st.sidebar:
    st.header("📊 Quick Stats")
    
    # Current month summary
    start_date, end_date = get_current_month_range()
    df = get_transactions_df()
    current_month_df = filter_by_date_range(df, start_date, end_date)
    
    income = calculate_summary(current_month_df, 'Income')
    expenses = calculate_summary(current_month_df, 'Expense')
    net = income - expenses
    
    st.metric("Monthly Income", f"${income:,.2f}", delta=None)
    st.metric("Monthly Expenses", f"${expenses:,.2f}", delta=None)
    st.metric("Net Savings", f"${net:,.2f}", 
              delta=f"${net:,.2f}", 
              delta_color="normal" if net >= 0 else "inverse")
    
    savings_rate = (net / income * 100) if income > 0 else 0
    st.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    st.divider()
    
    # Data management
    st.header("⚙️ Data Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Data", use_container_width=True):
            save_data()
            st.success("Data saved!")
    
    with col2:
        if st.button("🔄 Reload Data", use_container_width=True):
            load_data()
            st.success("Data reloaded!")
    
    if st.button("📥 Export to CSV", use_container_width=True):
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"budget_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
        if st.checkbox("I'm sure I want to delete everything"):
            st.session_state.transactions = []
            st.session_state.goals = []
            st.session_state.budgets = {}
            st.session_state.recurring = []
            save_data()
            st.success("All data cleared!")
            st.rerun()

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📝 Transactions", "📊 Dashboard", "🎯 Budget", "💎 Goals", 
    "📈 Reports", "🔄 Recurring", "⚙️ Categories", "📱 Insights"
])

# TAB 1: TRANSACTIONS
with tab1:
    st.header("💳 Transaction Management")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("➕ Add New Transaction")
        
        # Move type selector OUTSIDE the form so it updates immediately
        trans_type = st.radio("Type", ["Expense", "Income"], horizontal=True, key="trans_type_radio")
        
        with st.form("transaction_form", clear_on_submit=True):
            trans_date = st.date_input("Date", datetime.now())
            
            # Use session state to determine categories
            categories = st.session_state.categories['expense'] if trans_type == "Expense" else st.session_state.categories['income']
            trans_category = st.selectbox("Category", categories, key=f"cat_{trans_type}")
            
            trans_amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
            
            trans_description = st.text_input("Description")
            
            trans_tags = st.text_input("Tags (comma-separated)", placeholder="groceries, whole foods, weekly")
            
            trans_notes = st.text_area("Notes (optional)", height=100)
            
            submitted = st.form_submit_button("Add Transaction", type="primary", use_container_width=True)
            
            if submitted:
                transaction = {
                    'date': trans_date.isoformat(),
                    'type': trans_type,
                    'category': trans_category,
                    'amount': float(trans_amount),
                    'description': trans_description,
                    'tags': [tag.strip() for tag in trans_tags.split(',') if tag.strip()],
                    'notes': trans_notes,
                    'recurring': False
                }
                st.session_state.transactions.append(transaction)
                save_data()
                st.success(f"✅ {trans_type} of ${trans_amount:.2f} added!")
                st.rerun()
    
    with col2:
        st.subheader("📋 Recent Transactions")
        
        # Filters
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            filter_type = st.selectbox("Filter by Type", ["All", "Income", "Expense"])
        with col_b:
            all_categories = st.session_state.categories['expense'] + st.session_state.categories['income']
            filter_category = st.selectbox("Filter by Category", ["All"] + all_categories)
        with col_c:
            date_range = st.selectbox("Date Range", ["All Time", "This Month", "Last Month", "Last 3 Months", "This Year"])
        
        # Apply filters
        display_df = get_transactions_df()
        
        if not display_df.empty:
            if filter_type != "All":
                display_df = display_df[display_df['type'] == filter_type]
            
            if filter_category != "All":
                display_df = display_df[display_df['category'] == filter_category]
            
            # Date filtering
            today = datetime.now().date()
            if date_range == "This Month":
                start, end = get_current_month_range()
                display_df = filter_by_date_range(display_df, start, end)
            elif date_range == "Last Month":
                first = today.replace(day=1)
                end = first - timedelta(days=1)
                start = end.replace(day=1)
                display_df = filter_by_date_range(display_df, start, end)
            elif date_range == "Last 3 Months":
                end = today
                start = today - timedelta(days=90)
                display_df = filter_by_date_range(display_df, start, end)
            elif date_range == "This Year":
                start = today.replace(month=1, day=1)
                display_df = filter_by_date_range(display_df, start, today)
            
            # Sort by date descending
            display_df = display_df.sort_values('date', ascending=False)
            
            # Display transactions
            st.write(f"**{len(display_df)} transactions found**")
            
            for idx, row in display_df.head(20).iterrows():
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
                    
                    with col1:
                        st.write(f"**{row['date'].strftime('%Y-%m-%d')}**")
                    
                    with col2:
                        type_emoji = "📤" if row['type'] == "Income" else "📥"
                        st.write(f"{type_emoji} {row['category']}")
                        if row['description']:
                            st.caption(row['description'])
                    
                    with col3:
                        color = "green" if row['type'] == "Income" else "red"
                        st.markdown(f":{color}[**${row['amount']:,.2f}**]")
                    
                    with col4:
                        if st.button("🗑️", key=f"del_{idx}"):
                            st.session_state.transactions = [t for i, t in enumerate(st.session_state.transactions) if i != idx]
                            save_data()
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No transactions yet. Add your first transaction above!")

# TAB 2: DASHBOARD
with tab2:
    st.header("📊 Financial Dashboard")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        dashboard_start = st.date_input("From", datetime.now().date().replace(day=1))
    with col2:
        dashboard_end = st.date_input("To", datetime.now().date())
    
    df = get_transactions_df()
    dashboard_df = filter_by_date_range(df, dashboard_start, dashboard_end)
    
    if not dashboard_df.empty:
        # Summary metrics
        st.subheader("💰 Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        total_income = calculate_summary(dashboard_df, 'Income')
        total_expenses = calculate_summary(dashboard_df, 'Expense')
        net_savings = total_income - total_expenses
        avg_daily_spending = total_expenses / max(1, (dashboard_end - dashboard_start).days + 1)
        
        with col1:
            st.metric("Total Income", f"${total_income:,.2f}")
        with col2:
            st.metric("Total Expenses", f"${total_expenses:,.2f}")
        with col3:
            st.metric("Net Savings", f"${net_savings:,.2f}", 
                     delta=f"${net_savings:,.2f}",
                     delta_color="normal" if net_savings >= 0 else "inverse")
        with col4:
            st.metric("Avg Daily Spend", f"${avg_daily_spending:,.2f}")
        
        st.divider()
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Income vs Expenses")
            
            # Pie chart of expenses by category
            expense_df = dashboard_df[dashboard_df['type'] == 'Expense']
            if not expense_df.empty:
                category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
                category_totals = category_totals.sort_values('amount', ascending=False)
                
                fig = px.pie(category_totals, values='amount', names='category', 
                            title='Expenses by Category',
                            hole=0.4)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data for this period")
        
        with col2:
            st.subheader("💵 Income Sources")
            
            income_df = dashboard_df[dashboard_df['type'] == 'Income']
            if not income_df.empty:
                income_totals = income_df.groupby('category')['amount'].sum().reset_index()
                income_totals = income_totals.sort_values('amount', ascending=False)
                
                fig = px.pie(income_totals, values='amount', names='category',
                            title='Income by Source',
                            hole=0.4)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No income data for this period")
        
        # Spending trends
        st.subheader("📈 Spending Trends Over Time")
        
        # Group by date
        daily_df = dashboard_df.copy()
        daily_df['date'] = daily_df['date'].dt.date
        
        daily_income = daily_df[daily_df['type'] == 'Income'].groupby('date')['amount'].sum().reset_index()
        daily_expenses = daily_df[daily_df['type'] == 'Expense'].groupby('date')['amount'].sum().reset_index()
        
        fig = go.Figure()
        
        if not daily_income.empty:
            fig.add_trace(go.Scatter(x=daily_income['date'], y=daily_income['amount'],
                                    mode='lines+markers', name='Income',
                                    line=dict(color='green', width=2)))
        
        if not daily_expenses.empty:
            fig.add_trace(go.Scatter(x=daily_expenses['date'], y=daily_expenses['amount'],
                                    mode='lines+markers', name='Expenses',
                                    line=dict(color='red', width=2)))
        
        fig.update_layout(title='Daily Income vs Expenses',
                         xaxis_title='Date',
                         yaxis_title='Amount ($)',
                         hovermode='x unified')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top spending categories
        st.subheader("🏆 Top Spending Categories")
        
        if not expense_df.empty:
            top_categories = expense_df.groupby('category')['amount'].sum().reset_index()
            top_categories = top_categories.sort_values('amount', ascending=False).head(10)
            
            fig = px.bar(top_categories, x='amount', y='category', orientation='h',
                        title='Top 10 Expense Categories',
                        labels={'amount': 'Total Amount ($)', 'category': 'Category'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions found for the selected date range. Start adding transactions!")

# TAB 3: BUDGET
with tab3:
    st.header("🎯 Monthly Budget Planning")
    
    # Current month budget
    current_month = datetime.now().strftime("%Y-%m")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("💡 Set Category Budgets")
        
        budget_month = st.selectbox("Select Month", 
                                   [current_month] + [(datetime.now() + timedelta(days=30*i)).strftime("%Y-%m") for i in range(1, 12)])
        
        if budget_month not in st.session_state.budgets:
            st.session_state.budgets[budget_month] = {}
        
        with st.form("budget_form"):
            st.write("**Set budgets for each category:**")
            
            budget_values = {}
            for category in st.session_state.categories['expense']:
                current_budget = st.session_state.budgets[budget_month].get(category, 0.0)
                budget_values[category] = st.number_input(
                    category, 
                    min_value=0.0, 
                    value=float(current_budget),
                    step=10.0,
                    format="%.2f"
                )
            
            if st.form_submit_button("💾 Save Budget", type="primary", use_container_width=True):
                st.session_state.budgets[budget_month] = budget_values
                save_data()
                st.success("Budget saved successfully!")
                st.rerun()
    
    with col2:
        st.subheader("📊 Budget vs Actual")
        
        # Get current month transactions
        year, month = map(int, budget_month.split('-'))
        month_start = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        month_end = datetime(year, month, last_day).date()
        
        df = get_transactions_df()
        month_df = filter_by_date_range(df, month_start, month_end)
        
        if not month_df.empty:
            month_expenses = month_df[month_df['type'] == 'Expense']
        else:
            month_expenses = pd.DataFrame()
        
        if budget_month in st.session_state.budgets:
            budget_data = []
            
            for category, budget_amount in st.session_state.budgets[budget_month].items():
                if budget_amount > 0:
                    if not month_expenses.empty:
                        actual = month_expenses[month_expenses['category'] == category]['amount'].sum()
                    else:
                        actual = 0
                    remaining = budget_amount - actual
                    percent_used = (actual / budget_amount * 100) if budget_amount > 0 else 0
                    
                    budget_data.append({
                        'Category': category,
                        'Budget': budget_amount,
                        'Actual': actual,
                        'Remaining': remaining,
                        'Percent Used': percent_used
                    })
            
            if budget_data:
                budget_df = pd.DataFrame(budget_data)
                
                # Total budget summary
                total_budget = budget_df['Budget'].sum()
                total_actual = budget_df['Actual'].sum()
                total_remaining = total_budget - total_actual
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Budget", f"${total_budget:,.2f}")
                with col_b:
                    st.metric("Total Spent", f"${total_actual:,.2f}")
                with col_c:
                    st.metric("Remaining", f"${total_remaining:,.2f}",
                             delta=f"${total_remaining:,.2f}",
                             delta_color="normal" if total_remaining >= 0 else "inverse")
                
                st.divider()
                
                # Category breakdown
                for _, row in budget_df.iterrows():
                    with st.container():
                        st.write(f"**{row['Category']}**")
                        
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            progress = min(row['Percent Used'] / 100, 1.0)
                            st.progress(progress)
                        
                        with col2:
                            st.write(f"${row['Actual']:,.2f}")
                        
                        with col3:
                            if row['Remaining'] >= 0:
                                st.success(f"${row['Remaining']:,.2f}")
                            else:
                                st.error(f"${row['Remaining']:,.2f}")
                        
                        st.caption(f"Budget: ${row['Budget']:,.2f} | {row['Percent Used']:.1f}% used")
                        
                        st.divider()
                
                # Visualization
                fig = px.bar(budget_df, x='Category', y=['Budget', 'Actual'],
                            title='Budget vs Actual by Category',
                            barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Set some category budgets to see the comparison!")
        else:
            st.info(f"No budget set for {budget_month}. Use the form on the left to create one!")

# TAB 4: GOALS
with tab4:
    st.header("💎 Savings Goals")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("🎯 Create New Goal")
        
        with st.form("goal_form", clear_on_submit=True):
            goal_name = st.text_input("Goal Name", placeholder="Emergency Fund, Vacation, New Car...")
            
            goal_target = st.number_input("Target Amount ($)", min_value=1.0, step=100.0, format="%.2f")
            
            goal_current = st.number_input("Current Amount ($)", min_value=0.0, step=10.0, format="%.2f")
            
            goal_deadline = st.date_input("Target Date", min_value=datetime.now().date())
            
            goal_priority = st.select_slider("Priority", options=["Low", "Medium", "High", "Critical"])
            
            goal_notes = st.text_area("Notes", height=100)
            
            if st.form_submit_button("Create Goal", type="primary", use_container_width=True):
                goal = {
                    'name': goal_name,
                    'target': float(goal_target),
                    'current': float(goal_current),
                    'deadline': goal_deadline.isoformat(),
                    'priority': goal_priority,
                    'notes': goal_notes,
                    'created': datetime.now().isoformat()
                }
                st.session_state.goals.append(goal)
                save_data()
                st.success(f"Goal '{goal_name}' created!")
                st.rerun()
    
    with col2:
        st.subheader("📊 Your Goals")
        
        if st.session_state.goals:
            # Sort by priority
            priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
            sorted_goals = sorted(st.session_state.goals, 
                                key=lambda x: priority_order.get(x.get('priority', 'Medium'), 2))
            
            for idx, goal in enumerate(sorted_goals):
                with st.container():
                    col_a, col_b = st.columns([4, 1])
                    
                    with col_a:
                        st.write(f"### {goal['name']}")
                    
                    with col_b:
                        priority_colors = {
                            "Critical": "🔴",
                            "High": "🟠",
                            "Medium": "🟡",
                            "Low": "🟢"
                        }
                        st.write(f"{priority_colors.get(goal['priority'], '⚪')} {goal['priority']}")
                    
                    # Progress
                    progress = min(goal['current'] / goal['target'], 1.0)
                    st.progress(progress)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Current", f"${goal['current']:,.2f}")
                    
                    with col2:
                        st.metric("Target", f"${goal['target']:,.2f}")
                    
                    with col3:
                        remaining = goal['target'] - goal['current']
                        st.metric("Remaining", f"${remaining:,.2f}")
                    
                    with col4:
                        percent = (goal['current'] / goal['target'] * 100) if goal['target'] > 0 else 0
                        st.metric("Progress", f"{percent:.1f}%")
                    
                    # Time remaining
                    deadline = datetime.fromisoformat(goal['deadline']).date()
                    days_remaining = (deadline - datetime.now().date()).days
                    
                    if days_remaining > 0:
                        st.info(f"⏰ {days_remaining} days remaining until {deadline.strftime('%Y-%m-%d')}")
                        
                        # Calculate required monthly savings
                        months_remaining = max(days_remaining / 30, 1)
                        monthly_needed = remaining / months_remaining
                        st.caption(f"💡 Save ${monthly_needed:,.2f}/month to reach your goal")
                    else:
                        st.warning(f"⚠️ Deadline passed on {deadline.strftime('%Y-%m-%d')}")
                    
                    if goal['notes']:
                        st.caption(f"📝 {goal['notes']}")
                    
                    # Actions
                    col_a, col_b, col_c = st.columns([2, 2, 1])
                    
                    with col_a:
                        contribution = st.number_input(f"Add to goal", min_value=0.0, step=10.0, 
                                                      key=f"contrib_{idx}", format="%.2f")
                    
                    with col_b:
                        if st.button("💰 Add Contribution", key=f"add_{idx}"):
                            if contribution > 0:
                                st.session_state.goals[idx]['current'] += contribution
                                save_data()
                                st.success(f"Added ${contribution:.2f} to {goal['name']}!")
                                st.rerun()
                    
                    with col_c:
                        if st.button("🗑️ Delete", key=f"del_goal_{idx}"):
                            st.session_state.goals.pop(idx)
                            save_data()
                            st.rerun()
                    
                    st.divider()
        else:
            st.info("No goals yet. Create your first savings goal!")

# TAB 5: REPORTS
with tab5:
    st.header("📈 Financial Reports & Analytics")
    
    # Report type selector
    report_type = st.selectbox("Select Report Type", [
        "Monthly Summary",
        "Category Analysis",
        "Spending Patterns",
        "Year-over-Year Comparison",
        "Cash Flow Analysis",
        "Tax Summary"
    ])
    
    df = get_transactions_df()
    
    if not df.empty:
        if report_type == "Monthly Summary":
            st.subheader("📅 Monthly Summary Report")
            
            # Group by month
            df['month'] = df['date'].dt.to_period('M')
            monthly_income = df[df['type'] == 'Income'].groupby('month')['amount'].sum()
            monthly_expenses = df[df['type'] == 'Expense'].groupby('month')['amount'].sum()
            
            summary_df = pd.DataFrame({
                'Income': monthly_income,
                'Expenses': monthly_expenses,
                'Net Savings': monthly_income - monthly_expenses,
                'Savings Rate': (monthly_income - monthly_expenses) / monthly_income * 100
            }).reset_index()
            
            summary_df['month'] = summary_df['month'].astype(str)
            
            st.dataframe(summary_df.style.format({
                'Income': '${:,.2f}',
                'Expenses': '${:,.2f}',
                'Net Savings': '${:,.2f}',
                'Savings Rate': '{:.1f}%'
            }), use_container_width=True)
            
            # Visualization
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Income', x=summary_df['month'], y=summary_df['Income'], marker_color='green'))
            fig.add_trace(go.Bar(name='Expenses', x=summary_df['month'], y=summary_df['Expenses'], marker_color='red'))
            fig.add_trace(go.Scatter(name='Net Savings', x=summary_df['month'], y=summary_df['Net Savings'], 
                                    mode='lines+markers', marker_color='blue', yaxis='y2'))
            
            fig.update_layout(
                title='Monthly Financial Overview',
                xaxis_title='Month',
                yaxis_title='Amount ($)',
                yaxis2=dict(title='Net Savings ($)', overlaying='y', side='right'),
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif report_type == "Category Analysis":
            st.subheader("🏷️ Category Analysis")
            
            analysis_type = st.radio("Analyze", ["Expenses", "Income"], horizontal=True)
            time_period = st.selectbox("Time Period", ["Last Month", "Last 3 Months", "Last 6 Months", "Last Year", "All Time"])
            
            # Filter by time period
            today = datetime.now().date()
            if time_period == "Last Month":
                start_date = today - timedelta(days=30)
            elif time_period == "Last 3 Months":
                start_date = today - timedelta(days=90)
            elif time_period == "Last 6 Months":
                start_date = today - timedelta(days=180)
            elif time_period == "Last Year":
                start_date = today - timedelta(days=365)
            else:
                start_date = df['date'].min().date()
            
            filtered_df = filter_by_date_range(df, start_date, today)
            type_df = filtered_df[filtered_df['type'] == analysis_type]
            
            if not type_df.empty:
                category_stats = type_df.groupby('category').agg({
                    'amount': ['sum', 'mean', 'count']
                }).reset_index()
                
                category_stats.columns = ['Category', 'Total', 'Average', 'Count']
                category_stats = category_stats.sort_values('Total', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(category_stats, values='Total', names='Category',
                                title=f'{analysis_type} by Category')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(category_stats, x='Category', y='Total',
                                title=f'Total {analysis_type} by Category')
                    fig.update_layout(xaxis={'categoryorder': 'total descending'})
                    st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(category_stats.style.format({
                    'Total': '${:,.2f}',
                    'Average': '${:,.2f}',
                    'Count': '{:,.0f}'
                }), use_container_width=True)
            else:
                st.info(f"No {analysis_type.lower()} data for selected period")
        
        elif report_type == "Spending Patterns":
            st.subheader("🔍 Spending Pattern Analysis")
            
            expense_df = df[df['type'] == 'Expense'].copy()
            
            if not expense_df.empty:
                # Day of week analysis
                expense_df['day_of_week'] = expense_df['date'].dt.day_name()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                dow_spending = expense_df.groupby('day_of_week')['amount'].sum().reindex(day_order)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.bar(x=dow_spending.index, y=dow_spending.values,
                                title='Spending by Day of Week',
                                labels={'x': 'Day', 'y': 'Total Amount ($)'})
                    st.plotly_chart(fig, use_container_width=True)
                
                # Hour analysis (if time data available)
                with col2:
                    expense_df['day_of_month'] = expense_df['date'].dt.day
                    dom_spending = expense_df.groupby('day_of_month')['amount'].sum()
                    
                    fig = px.line(x=dom_spending.index, y=dom_spending.values,
                                 title='Spending by Day of Month',
                                 labels={'x': 'Day of Month', 'y': 'Total Amount ($)'})
                    st.plotly_chart(fig, use_container_width=True)
                
                # Average transaction size by category
                st.subheader("💵 Average Transaction Size")
                avg_by_category = expense_df.groupby('category')['amount'].mean().sort_values(ascending=False)
                
                fig = px.bar(x=avg_by_category.index, y=avg_by_category.values,
                            title='Average Transaction Size by Category',
                            labels={'x': 'Category', 'y': 'Average Amount ($)'})
                st.plotly_chart(fig, use_container_width=True)
        
        elif report_type == "Cash Flow Analysis":
            st.subheader("💸 Cash Flow Analysis")
            
            # Weekly cash flow
            df['week'] = df['date'].dt.to_period('W')
            
            weekly_income = df[df['type'] == 'Income'].groupby('week')['amount'].sum()
            weekly_expenses = df[df['type'] == 'Expense'].groupby('week')['amount'].sum()
            weekly_net = weekly_income - weekly_expenses
            
            # Cumulative
            cumulative_net = weekly_net.cumsum()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(x=weekly_income.index.astype(str), y=weekly_income.values,
                                    name='Income', mode='lines', line=dict(color='green')))
            fig.add_trace(go.Scatter(x=weekly_expenses.index.astype(str), y=weekly_expenses.values,
                                    name='Expenses', mode='lines', line=dict(color='red')))
            fig.add_trace(go.Scatter(x=weekly_net.index.astype(str), y=weekly_net.values,
                                    name='Net Cash Flow', mode='lines', line=dict(color='blue', dash='dash')))
            
            fig.update_layout(title='Weekly Cash Flow',
                            xaxis_title='Week',
                            yaxis_title='Amount ($)',
                            hovermode='x unified')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Cumulative savings
            fig = px.line(x=cumulative_net.index.astype(str), y=cumulative_net.values,
                         title='Cumulative Net Savings Over Time',
                         labels={'x': 'Week', 'y': 'Cumulative Savings ($)'})
            fig.update_traces(line_color='green', fill='tozeroy')
            st.plotly_chart(fig, use_container_width=True)
        
        elif report_type == "Tax Summary":
            st.subheader("📋 Tax Summary Report")
            
            tax_year = st.selectbox("Select Year", 
                                   sorted(df['date'].dt.year.unique(), reverse=True))
            
            year_df = df[df['date'].dt.year == tax_year]
            
            st.write(f"### {tax_year} Tax Year Summary")
            
            income_df = year_df[year_df['type'] == 'Income']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_income = income_df['amount'].sum()
                st.metric("Total Income", f"${total_income:,.2f}")
            
            with col2:
                # Deductible expenses (customize categories as needed)
                deductible_categories = ["🏥 Healthcare", "🎓 Education", "🔧 Maintenance"]
                deductible = year_df[year_df['category'].isin(deductible_categories)]['amount'].sum()
                st.metric("Potential Deductions", f"${deductible:,.2f}")
            
            with col3:
                donations = year_df[year_df['category'] == "🎁 Gifts & Donations"]['amount'].sum()
                st.metric("Charitable Donations", f"${donations:,.2f}")
            
            # Income breakdown
            st.subheader("Income Sources")
            income_by_source = income_df.groupby('category')['amount'].sum().reset_index()
            
            st.dataframe(income_by_source.style.format({'amount': '${:,.2f}'}),
                        use_container_width=True)
            
            st.info("💡 This is a summary for informational purposes only. Consult a tax professional for actual tax preparation.")
    else:
        st.info("No transaction data available for reports. Start adding transactions!")

# TAB 6: RECURRING TRANSACTIONS
with tab6:
    st.header("🔄 Recurring Transactions")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("➕ Add Recurring Transaction")
        
        # Move type selector OUTSIDE the form so it updates immediately
        rec_type = st.radio("Type", ["Expense", "Income"], horizontal=True, key="rec_type_radio")
        
        with st.form("recurring_form", clear_on_submit=True):
            categories = st.session_state.categories['expense'] if rec_type == "Expense" else st.session_state.categories['income']
            rec_category = st.selectbox("Category", categories, key=f"rec_cat_{rec_type}")
            
            rec_amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
            
            rec_description = st.text_input("Description")
            
            rec_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Bi-weekly", "Monthly", "Yearly"])
            
            rec_start_date = st.date_input("Start Date", datetime.now())
            
            rec_tags = st.text_input("Tags (comma-separated)")
            
            if st.form_submit_button("Create Recurring Transaction", type="primary", use_container_width=True):
                recurring = {
                    'type': rec_type,
                    'category': rec_category,
                    'amount': float(rec_amount),
                    'description': rec_description,
                    'frequency': rec_frequency,
                    'start_date': rec_start_date.isoformat(),
                    'tags': [tag.strip() for tag in rec_tags.split(',') if tag.strip()],
                    'active': True,
                    'last_processed': None
                }
                st.session_state.recurring.append(recurring)
                save_data()
                st.success("Recurring transaction created!")
                st.rerun()
    
    with col2:
        st.subheader("📋 Active Recurring Transactions")
        
        if st.session_state.recurring:
            for idx, rec in enumerate(st.session_state.recurring):
                if rec.get('active', True):
                    with st.container():
                        col_a, col_b, col_c = st.columns([3, 2, 1])
                        
                        with col_a:
                            type_emoji = "📤" if rec['type'] == "Income" else "📥"
                            st.write(f"**{type_emoji} {rec['description']}**")
                            st.caption(f"{rec['category']} - {rec['frequency']}")
                        
                        with col_b:
                            color = "green" if rec['type'] == "Income" else "red"
                            st.markdown(f":{color}[**${rec['amount']:,.2f}**]")
                            if rec.get('last_processed'):
                                last_date = datetime.fromisoformat(rec['last_processed']).strftime('%Y-%m-%d')
                                st.caption(f"Last: {last_date}")
                        
                        with col_c:
                            if st.button("⏸️", key=f"pause_{idx}"):
                                st.session_state.recurring[idx]['active'] = False
                                save_data()
                                st.rerun()
                            
                            if st.button("🗑️", key=f"del_rec_{idx}"):
                                st.session_state.recurring.pop(idx)
                                save_data()
                                st.rerun()
                        
                        st.divider()
        else:
            st.info("No recurring transactions set up. Create one to automate your budget tracking!")
        
        # Show inactive
        inactive = [r for r in st.session_state.recurring if not r.get('active', True)]
        if inactive:
            st.subheader("⏸️ Paused Recurring Transactions")
            for idx, rec in enumerate(inactive):
                actual_idx = st.session_state.recurring.index(rec)
                with st.container():
                    st.write(f"**{rec['description']}** - ${rec['amount']:.2f}")
                    if st.button("▶️ Resume", key=f"resume_{actual_idx}"):
                        st.session_state.recurring[actual_idx]['active'] = True
                        save_data()
                        st.rerun()

# TAB 7: CATEGORIES
with tab7:
    st.header("⚙️ Category Management")
    
    st.info("💡 Tip: Use emojis to make your categories visually distinct! For example: 🎮 Gaming, ☕ Coffee, 🎵 Music")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Expense Categories")
        
        with st.form("expense_category_form"):
            new_expense_cat = st.text_input("Add New Expense Category", 
                                           placeholder="🎮 Gaming")
            
            col_a, col_b = st.columns(2)
            with col_a:
                add_expense = st.form_submit_button("➕ Add Category", use_container_width=True, type="primary")
            with col_b:
                reset_expense = st.form_submit_button("🔄 Reset to Default", use_container_width=True)
            
            if add_expense and new_expense_cat:
                if new_expense_cat not in st.session_state.categories['expense']:
                    st.session_state.categories['expense'].append(new_expense_cat)
                    st.session_state.categories['expense'].sort()
                    save_data()
                    st.success(f"✅ Added '{new_expense_cat}'!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ '{new_expense_cat}' already exists!")
            
            if reset_expense:
                st.session_state.categories['expense'] = DEFAULT_EXPENSE_CATEGORIES.copy()
                save_data()
                st.success("✅ Reset to default expense categories!")
                st.rerun()
        
        st.write("**Current Expense Categories:**")
        st.caption(f"{len(st.session_state.categories['expense'])} categories")
        
        # Display in a container with delete buttons
        for idx, cat in enumerate(sorted(st.session_state.categories['expense'])):
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.write(f"{idx + 1}. {cat}")
            with col_b:
                # Allow deletion of any category, but warn if it's a default
                if st.button("🗑️", key=f"del_exp_{idx}_{cat}", help="Delete this category"):
                    # Check if category is in use
                    df = get_transactions_df()
                    if not df.empty:
                        in_use = len(df[df['category'] == cat]) > 0
                        if in_use:
                            st.warning(f"⚠️ '{cat}' is used in {len(df[df['category'] == cat])} transactions!")
                            if st.button(f"⚠️ Delete anyway?", key=f"confirm_del_exp_{idx}"):
                                st.session_state.categories['expense'].remove(cat)
                                save_data()
                                st.success(f"Deleted '{cat}'")
                                st.rerun()
                        else:
                            st.session_state.categories['expense'].remove(cat)
                            save_data()
                            st.success(f"Deleted '{cat}'")
                            st.rerun()
                    else:
                        st.session_state.categories['expense'].remove(cat)
                        save_data()
                        st.rerun()
    
    with col2:
        st.subheader("📤 Income Categories")
        
        with st.form("income_category_form"):
            new_income_cat = st.text_input("Add New Income Category",
                                          placeholder="🎨 Side Hustle")
            
            col_a, col_b = st.columns(2)
            with col_a:
                add_income = st.form_submit_button("➕ Add Category", use_container_width=True, type="primary")
            with col_b:
                reset_income = st.form_submit_button("🔄 Reset to Default", use_container_width=True)
            
            if add_income and new_income_cat:
                if new_income_cat not in st.session_state.categories['income']:
                    st.session_state.categories['income'].append(new_income_cat)
                    st.session_state.categories['income'].sort()
                    save_data()
                    st.success(f"✅ Added '{new_income_cat}'!")
                    st.rerun()
                else:
                    st.warning(f"⚠️ '{new_income_cat}' already exists!")
            
            if reset_income:
                st.session_state.categories['income'] = DEFAULT_INCOME_CATEGORIES.copy()
                save_data()
                st.success("✅ Reset to default income categories!")
                st.rerun()
        
        st.write("**Current Income Categories:**")
        st.caption(f"{len(st.session_state.categories['income'])} categories")
        
        # Display in a container with delete buttons
        for idx, cat in enumerate(sorted(st.session_state.categories['income'])):
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.write(f"{idx + 1}. {cat}")
            with col_b:
                if st.button("🗑️", key=f"del_inc_{idx}_{cat}", help="Delete this category"):
                    # Check if category is in use
                    df = get_transactions_df()
                    if not df.empty:
                        in_use = len(df[df['category'] == cat]) > 0
                        if in_use:
                            st.warning(f"⚠️ '{cat}' is used in {len(df[df['category'] == cat])} transactions!")
                            if st.button(f"⚠️ Delete anyway?", key=f"confirm_del_inc_{idx}"):
                                st.session_state.categories['income'].remove(cat)
                                save_data()
                                st.success(f"Deleted '{cat}'")
                                st.rerun()
                        else:
                            st.session_state.categories['income'].remove(cat)
                            save_data()
                            st.success(f"Deleted '{cat}'")
                            st.rerun()
                    else:
                        st.session_state.categories['income'].remove(cat)
                        save_data()
                        st.rerun()
    
    st.divider()
    
    # Category statistics
    st.subheader("📊 Category Usage Statistics")
    
    df = get_transactions_df()
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Most Used Expense Categories:**")
            expense_df = df[df['type'] == 'Expense']
            if not expense_df.empty:
                usage = expense_df['category'].value_counts().head(5)
                for cat, count in usage.items():
                    st.write(f"• {cat}: {count} transactions")
            else:
                st.caption("No expense transactions yet")
        
        with col2:
            st.write("**Most Used Income Categories:**")
            income_df = df[df['type'] == 'Income']
            if not income_df.empty:
                usage = income_df['category'].value_counts().head(5)
                for cat, count in usage.items():
                    st.write(f"• {cat}: {count} transactions")
            else:
                st.caption("No income transactions yet")
    else:
        st.info("Add some transactions to see category usage statistics!")

# TAB 8: INSIGHTS
with tab8:
    st.header("📱 Financial Insights & Tips")
    
    df = get_transactions_df()
    
    if not df.empty:
        # Current month data
        start_date, end_date = get_current_month_range()
        current_month_df = filter_by_date_range(df, start_date, end_date)
        
        # Previous month data
        prev_month_end = start_date - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)
        prev_month_df = filter_by_date_range(df, prev_month_start, prev_month_end)
        
        st.subheader("💡 Monthly Insights")
        
        # Calculate changes
        current_expenses = calculate_summary(current_month_df, 'Expense')
        prev_expenses = calculate_summary(prev_month_df, 'Expense')
        expense_change = current_expenses - prev_expenses
        expense_change_pct = (expense_change / prev_expenses * 100) if prev_expenses > 0 else 0
        
        current_income = calculate_summary(current_month_df, 'Income')
        prev_income = calculate_summary(prev_month_df, 'Income')
        
        # Insights
        col1, col2 = st.columns(2)
        
        with col1:
            if expense_change_pct > 10:
                st.warning(f"⚠️ Your expenses increased by {expense_change_pct:.1f}% compared to last month!")
            elif expense_change_pct < -10:
                st.success(f"🎉 Great job! Your expenses decreased by {abs(expense_change_pct):.1f}% compared to last month!")
            
            # Top spending category
            if not current_month_df[current_month_df['type'] == 'Expense'].empty:
                top_category = current_month_df[current_month_df['type'] == 'Expense'].groupby('category')['amount'].sum().idxmax()
                top_amount = current_month_df[current_month_df['type'] == 'Expense'].groupby('category')['amount'].sum().max()
                st.info(f"🏆 Your highest spending category this month is **{top_category}** at ${top_amount:,.2f}")
        
        with col2:
            # Savings rate
            if current_income > 0:
                savings_rate = ((current_income - current_expenses) / current_income * 100)
                
                if savings_rate >= 20:
                    st.success(f"💰 Excellent! You're saving {savings_rate:.1f}% of your income!")
                elif savings_rate >= 10:
                    st.info(f"👍 Good job! You're saving {savings_rate:.1f}% of your income. Try to increase it to 20%!")
                elif savings_rate > 0:
                    st.warning(f"⚠️ You're only saving {savings_rate:.1f}%. Try to increase your savings rate!")
                else:
                    st.error(f"🚨 You're spending more than you earn! Time to review your budget.")
        
        st.divider()
        
        # Spending trends
        st.subheader("📊 Spending Trends")
        
        # Get last 6 months
        expense_df = df[df['type'] == 'Expense'].copy()
        expense_df['month'] = expense_df['date'].dt.to_period('M')
        monthly_expenses = expense_df.groupby('month')['amount'].sum().tail(6)
        
        if len(monthly_expenses) >= 3:
            # Calculate trend
            recent_avg = monthly_expenses.tail(3).mean()
            older_avg = monthly_expenses.head(3).mean()
            
            if recent_avg > older_avg * 1.1:
                st.warning("📈 Your spending has been trending upward over the last few months")
            elif recent_avg < older_avg * 0.9:
                st.success("📉 Your spending has been trending downward - great work!")
            else:
                st.info("➡️ Your spending has been relatively stable")
        
        # Recommendations
        st.subheader("💭 Personalized Recommendations")
        
        recommendations = []
        
        # Budget recommendations
        current_month_key = datetime.now().strftime("%Y-%m")
        if current_month_key in st.session_state.budgets:
            over_budget_categories = []
            for category, budget in st.session_state.budgets[current_month_key].items():
                if budget > 0:
                    actual = current_month_df[current_month_df['category'] == category]['amount'].sum()
                    if actual > budget:
                        over_budget_categories.append((category, actual, budget))
            
            if over_budget_categories:
                recommendations.append(f"⚠️ You're over budget in {len(over_budget_categories)} categories this month. Focus on: {', '.join([c[0] for c in over_budget_categories[:3]])}")
        
        # Goal recommendations
        if st.session_state.goals:
            urgent_goals = []
            for goal in st.session_state.goals:
                deadline = datetime.fromisoformat(goal['deadline']).date()
                days_left = (deadline - datetime.now().date()).days
                remaining = goal['target'] - goal['current']
                
                if days_left > 0 and days_left < 60 and remaining > 0:
                    urgent_goals.append(goal['name'])
            
            if urgent_goals:
                recommendations.append(f"🎯 You have {len(urgent_goals)} goals approaching their deadline. Focus on: {', '.join(urgent_goals[:2])}")
        
        # Savings recommendation
        if current_income > 0:
            current_savings = current_income - current_expenses
            recommended_savings = current_income * 0.2
            
            if current_savings < recommended_savings:
                diff = recommended_savings - current_savings
                recommendations.append(f"💰 Try to save an additional ${diff:,.2f} this month to reach the recommended 20% savings rate")
        
        # Display recommendations
        if recommendations:
            for rec in recommendations:
                st.write(f"• {rec}")
        else:
            st.success("✅ You're doing great! Keep up the good financial habits!")
        
        st.divider()
        
        # Financial health score
        st.subheader("🏥 Financial Health Score")
        
        score = 0
        max_score = 100
        
        # Income vs Expenses (30 points)
        if current_income > current_expenses:
            score += 30
        elif current_income > current_expenses * 0.9:
            score += 15
        
        # Savings rate (25 points)
        if current_income > 0:
            savings_rate = (current_income - current_expenses) / current_income
            score += min(25, int(savings_rate * 125))  # Max at 20% savings rate
        
        # Budget adherence (25 points)
        if current_month_key in st.session_state.budgets:
            budget_count = sum(1 for b in st.session_state.budgets[current_month_key].values() if b > 0)
            if budget_count > 0:
                score += 10
                
                within_budget = 0
                for category, budget in st.session_state.budgets[current_month_key].items():
                    if budget > 0:
                        actual = current_month_df[current_month_df['category'] == category]['amount'].sum()
                        if actual <= budget:
                            within_budget += 1
                
                score += int((within_budget / budget_count) * 15)
        
        # Goal progress (20 points)
        if st.session_state.goals:
            total_progress = 0
            for goal in st.session_state.goals:
                progress = min(goal['current'] / goal['target'], 1.0)
                total_progress += progress
            
            avg_progress = total_progress / len(st.session_state.goals)
            score += int(avg_progress * 20)
        
        # Display score
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.metric("Financial Health Score", f"{score}/{max_score}")
            st.progress(score / max_score)
            
            if score >= 80:
                st.success("🌟 Excellent! Your finances are in great shape!")
            elif score >= 60:
                st.info("👍 Good job! Keep working on your financial goals.")
            elif score >= 40:
                st.warning("⚠️ Room for improvement. Focus on budgeting and saving.")
            else:
                st.error("🚨 Your finances need attention. Consider reviewing your budget and spending habits.")
    
    else:
        st.info("Add some transactions to see personalized insights and recommendations!")

# Footer
st.divider()
st.caption("💰 Ultimate Budget Tracker - Your complete personal finance solution | Data saved locally")
