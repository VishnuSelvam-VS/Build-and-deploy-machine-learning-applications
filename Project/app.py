from flask import Flask, render_template, request, redirect, flash
import csv
import os
import pandas as pd
from datetime import date

app = Flask(__name__)
app.secret_key = "my_secret_key"  # Needed for flashing messages
CSV_FILE = "habits.csv"

# ---------- File Handling ----------
def read_habits():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "habit", "completed", "time"])
    return pd.read_csv(CSV_FILE)

def add_to_csv(habit, time):
    today = date.today().isoformat()
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([today, habit, 0, time])

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_habit():
    df = read_habits()
    today = date.today().isoformat()
    if request.method == 'POST':
        habit = request.form['habit'].strip().lower()
        time = request.form.get('time', "")

        # Check if habit already exists today
        if not df.empty and ((df["date"] == today) & (df["habit"].str.lower() == habit)).any():
            flash("⚠️ This habit already exists for today!")
            return redirect('/add')

        add_to_csv(habit, time)
        flash("✅ Habit added successfully!")
        return redirect('/')

    return render_template('add_habit.html')

@app.route('/habits')
def view_habits():
    df = read_habits()
    today = date.today().isoformat()
    today_habits = df[df["date"] == today]
    return render_template('habits.html', habits=today_habits.to_dict(orient='records'), today=today)

@app.route('/complete/<habit>')
def complete(habit):
    df = read_habits()
    today = date.today().isoformat()
    df.loc[(df["date"] == today) & (df["habit"] == habit), "completed"] = 1
    df.to_csv(CSV_FILE, index=False)
    flash(f"✅ Marked '{habit}' as Done!")
    return redirect('/habits')

if __name__ == '__main__':
    app.run(debug=True)
