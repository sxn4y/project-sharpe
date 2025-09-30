import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def load_holdings_html(file_path):
    """
    Load holdings from an HTML file containing a table.
    """
    try:
        tables = pd.read_html(file_path)
        if len(tables) == 0:
            raise ValueError("No tables found in HTML file.")
        # Use the first table by default
        df = tables[0]
        df.columns = [str(c).strip() for c in df.columns]  # clean column names
    except Exception as e:
        raise ValueError(f"Could not read HTML table: {e}")

    # Convert numeric columns
    for col in ['Weight (%)', 'Market Value', 'Notional Value', 'Quantity', 'Price', 'FX Rate']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def filter_by_date(df, start_date=None, end_date=None):
    """
    Filter DataFrame by 'Accrual Date' column if present.
    """
    if 'Accrual Date' in df.columns:
        df['Accrual Date'] = pd.to_datetime(df['Accrual Date'], errors='coerce')
        if start_date:
            df = df[df['Accrual Date'] >= start_date]
        if end_date:
            df = df[df['Accrual Date'] <= end_date]
    return df

def run_gui():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select ESG Holdings HTML File",
        filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")]
    )
    if not file_path:
        messagebox.showerror("Error", "No file selected.")
        return

    try:
        start_date_str = tk.simpledialog.askstring("Start Date", "Enter start date (YYYY-MM-DD) or leave blank:")
        end_date_str = tk.simpledialog.askstring("End Date", "Enter end date (YYYY-MM-DD) or leave blank:")

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

        holdings_df = load_holdings_html(file_path)
        holdings_df = filter_by_date(holdings_df, start_date, end_date)

        # Print all rows
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 2000):
            print("\n=== Holdings Data ===")
            print(holdings_df)

        messagebox.showinfo("Success", "Holdings loaded successfully! Check terminal output.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to process file:\n{e}")

if __name__ == "__main__":
    run_gui()
ø