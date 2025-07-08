import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

CSV_FILE = "medicines.csv"

# Ensure CSV exists
def create_csv():
    try:
        pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        pd.DataFrame(columns=["name", "batch", "expiry_date"]).to_csv(CSV_FILE, index=False)

# Add new medicine
def add_medicine(name, batch, expiry_date):
    new_row = pd.DataFrame([[name, batch, expiry_date]], columns=["name", "batch", "expiry_date"])
    new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)

# Load and process data
def load_data():
    df = pd.read_csv(CSV_FILE)
    df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce')
    df['days_left'] = (df['expiry_date'] - datetime.today()).dt.days
    return df

# Save dataframe to CSV
def save_data(df):
    df[['name', 'batch', 'expiry_date']].to_csv(CSV_FILE, index=False)

# Highlight function

def highlight_expiry(row):
    if row['days_left'] <= 7:
        return ['background-color: #ffcccc']*4  # red
    elif row['days_left'] <= 30:
        return ['background-color: #fff3cd']*4  # yellow
    else:
        return ['background-color: #d4edda']*4  # green

# Main UI

def main():
    st.set_page_config("💊 Expiry Notifier", layout="centered")
    create_csv()

    st.title("💊 Medicine Expiry Dashboard")
    st.write("Manage medicines, check expiry, and update your list in real-time.")

    # ➕ Add Medicine
    with st.form("add_form"):
        st.subheader("➕ Add New Medicine")
        name = st.text_input("Medicine Name")
        batch = st.text_input("Batch Number")
        expiry = st.date_input("Expiry Date")
        add_submit = st.form_submit_button("Add")

        if add_submit:
            if name and batch:
                add_medicine(name, batch, expiry.strftime("%Y-%m-%d"))
                st.success(f"✅ {name} added.")
            else:
                st.error("❌ Fill all fields.")

    df = load_data()

    # 🧼 Color-coded Expiry Section
    st.subheader("⚠️ Expiry Tracker (Color Coded)")
    if not df.empty:
        st.dataframe(df.style.apply(highlight_expiry, axis=1))
    else:
        st.info("No data available.")

    # 📈 Expiry Distribution Chart
    st.subheader("📊 Expiry Distribution Chart")
    if not df.empty:
        bins = [0, 7, 30, 90, 180, 10000]
        labels = ['0-7 days', '8-30 days', '31-90 days', '91-180 days', '181+ days']
        df['range'] = pd.cut(df['days_left'], bins=bins, labels=labels)

        chart_data = df['range'].value_counts().sort_index()
        fig, ax = plt.subplots()
        chart_data.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title("Medicines by Expiry Range")
        ax.set_ylabel("Count")
        ax.set_xlabel("Days Left")
        st.pyplot(fig)
    else:
        st.info("📟 No data to visualize.")

    # 🗒️ Update or 🗑️ Delete
    st.subheader("🧰 Update / Delete Medicines")
    if not df.empty:
        edited_df = st.data_editor(
            df[['name', 'batch', 'expiry_date']],
            num_rows="dynamic",
            use_container_width=True,
            key="editor"
        )

        # Save edits
        if st.button("📂 Save Changes"):
            save_data(edited_df)
            st.success("✅ Data updated successfully!")

        # Delete selected row
        delete_index = st.selectbox("Select row to delete:", df.index)
        if st.button("🖑️ Delete Selected Row"):
            df = df.drop(delete_index)
            save_data(df)
            st.success("✅ Row deleted.")
    else:
        st.info("No entries to modify.")

if __name__ == "__main__":
    main()
