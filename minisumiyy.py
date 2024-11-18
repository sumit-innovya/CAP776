import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Load and prepare the dataset
def load_dataset(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()  # Remove leading/trailing spaces from column names
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', dayfirst=True)
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

# Function to fetch distance data for a specific date
def get_distance(df, date, column):
    try:
        date = pd.to_datetime(date, format='%d-%m-%Y')  # Convert input to datetime
        result = df[df['Date'] == date]
        if not result.empty:
            return result[column].values[0]
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to plot graph for distance with the chosen graph type
def plot_graph(df, start_date, end_date, columns, labels, graph_type):
    try:
        start_date = pd.to_datetime(start_date, format='%d-%m-%Y')
        end_date = pd.to_datetime(end_date, format='%d-%m-%Y')
        filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        if filtered_df.empty:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        for col, label in zip(columns, labels):
            if graph_type == 'Line':
                ax.plot(filtered_df['Date'], filtered_df[col], label=label, marker='o')
            elif graph_type == 'Bar':
                ax.bar(filtered_df['Date'], filtered_df[col], label=label)
            elif graph_type == 'Scatter':
                ax.scatter(filtered_df['Date'], filtered_df[col], label=label)

        ax.set_title("Distance Graph")
        ax.set_xlabel("Date")
        ax.set_ylabel("Distance (KM)")
        ax.legend()
        return fig
    except Exception as e:
        print(f"Error: {e}")
        return None

# Main GUI Application
def main():
    file_path = 'trekdataset.csv'  # Ensure the dataset file is in the same directory
    df = load_dataset(file_path)
    if df is None:
        messagebox.showerror("Error", "Failed to load the dataset. Ensure the file exists and has the correct format.")
        return

    root = tk.Tk()
    root.title("Trek Distance Tracker")
    root.geometry("800x600")

    def clear_frame():
        for widget in root.winfo_children():
            widget.destroy()

    def show_jogging_distance_page():
        clear_frame()
        tk.Label(root, text="Enter Date (DD-MM-YYYY):").pack(pady=10)
        date_input = tk.Entry(root)
        date_input.pack(pady=5)

        def display_jogging_distance():
            date = date_input.get()
            distance = get_distance(df, date, "Jogging_Distance_km")
            if distance is not None:
                messagebox.showinfo("Jogging Distance", f"Jogging Distance on {date}: {distance} KM")
            else:
                messagebox.showerror("Error", "Invalid date or no data found.")

        tk.Button(root, text="Submit", command=display_jogging_distance).pack(pady=20)
        tk.Button(root, text="Back", command=dashboard).pack(pady=10)

    def show_walking_distance_page():
        clear_frame()
        tk.Label(root, text="Enter Date (DD-MM-YYYY):").pack(pady=10)
        date_input = tk.Entry(root)
        date_input.pack(pady=5)

        def display_walking_distance():
            date = date_input.get()
            distance = get_distance(df, date, "Walking_Distance_km")
            if distance is not None:
                messagebox.showinfo("Walking Distance", f"Walking Distance on {date}: {distance} KM")
            else:
                messagebox.showerror("Error", "Invalid date or no data found.")

        tk.Button(root, text="Submit", command=display_walking_distance).pack(pady=20)
        tk.Button(root, text="Back", command=dashboard).pack(pady=10)

    def show_total_distance_page():
        clear_frame()
        tk.Label(root, text="Enter Date (DD-MM-YYYY):").pack(pady=10)
        date_input = tk.Entry(root)
        date_input.pack(pady=5)

        def display_total_distance():
            date = date_input.get()
            distance = get_distance(df, date, "Total_Distance_km")
            if distance is not None:
                messagebox.showinfo("Total Distance", f"Total Distance on {date}: {distance} KM")
            else:
                messagebox.showerror("Error", "Invalid date or no data found.")

        tk.Button(root, text="Submit", command=display_total_distance).pack(pady=20)
        tk.Button(root, text="Back", command=dashboard).pack(pady=10)

    def show_graph_page(columns_dict):
        clear_frame()

        # Define the date input fields
        tk.Label(root, text="Enter Start Date (DD-MM-YYYY):").pack(pady=5)
        start_date_input = tk.Entry(root)
        start_date_input.pack(pady=5)

        tk.Label(root, text="Enter End Date (DD-MM-YYYY):").pack(pady=5)
        end_date_input = tk.Entry(root)
        end_date_input.pack(pady=5)

        tk.Label(root, text="Select Graph Type:").pack(pady=5)
        graph_type_combobox = ttk.Combobox(root, values=["Line", "Bar", "Scatter"], state="readonly")
        graph_type_combobox.pack(pady=5)
        graph_type_combobox.set("Line")

        tk.Label(root, text="Choose Distance Type:").pack(pady=5)
        distance_combobox = ttk.Combobox(
            root, values=list(columns_dict.keys()), state="readonly"
        )
        distance_combobox.pack(pady=5)
        distance_combobox.set(list(columns_dict.keys())[0])

        # Canvas to display the graph
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(pady=20)

        def update_graph():
            start_date = start_date_input.get()
            end_date = end_date_input.get()
            graph_type = graph_type_combobox.get()
            selected_distance = distance_combobox.get()

            if not start_date or not end_date:
                messagebox.showerror("Error", "Please enter both start and end dates.")
                return

            columns, labels = columns_dict[selected_distance]
            fig = plot_graph(df, start_date, end_date, columns, labels, graph_type)
            if fig is not None:
                # Clear existing graph
                for widget in canvas_frame.winfo_children():
                    widget.destroy()
                canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
                canvas.get_tk_widget().pack()
                canvas.draw()
            else:
                messagebox.showerror("Error", "Invalid date range or no data found.")

        tk.Button(root, text="Show Graph", command=update_graph).pack(pady=10)
        tk.Button(root, text="Back", command=dashboard).pack(pady=10)

    def dashboard():
        clear_frame()
        tk.Label(root, text="Trek Distance Tracker Dashboard", font=("Arial", 18)).pack(pady=20)
        tk.Button(root, text="View Jogging Distance by Date", command=show_jogging_distance_page, font=("Arial", 12), bg="lightblue").pack(pady=10)
        tk.Button(root, text="View Walking Distance by Date", command=show_walking_distance_page, font=("Arial", 12), bg="lightblue").pack(pady=10)
        tk.Button(root, text="View Total Distance by Date", command=show_total_distance_page, font=("Arial", 12), bg="lightblue").pack(pady=10)
        tk.Button(root, text="View Graphs", command=lambda: show_graph_page({
            "Jogging Distance": (["Jogging_Distance_km"], ["Jogging Distance"]),
            "Walking Distance": (["Walking_Distance_km"], ["Walking Distance"]),
            "Total Distance": (["Total_Distance_km"], ["Total Distance"]),
            "Combined Distance": (
                ["Jogging_Distance_km", "Walking_Distance_km", "Total_Distance_km"],
                ["Jogging Distance", "Walking Distance", "Total Distance"]
            )
        }), font=("Arial", 12), bg="lightblue").pack(pady=10)
        tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12), bg="lightgray").pack(pady=10)

    dashboard()
    root.mainloop()

if __name__ == "__main__":
    main()
